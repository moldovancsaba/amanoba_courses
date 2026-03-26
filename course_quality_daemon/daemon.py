from __future__ import annotations

import argparse
import ast
import fcntl
import hashlib
from html import unescape as html_unescape
import json
import os
import shutil
import signal
import sqlite3
import socket
import sys
import tempfile
import subprocess
import time
import threading
import re
import uuid
import urllib.parse
import urllib.request
import urllib.error
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .confidence import confidence_for_completion, confidence_for_validation
from .local_runtime import LocalRuntimeManager
from .portable_paths import resolve_mlx_model_path, resolve_portable_path
from .validator import _language_purity_errors, audit_lesson, validate_question


DEFAULT_FEED_LIMIT = 25
DONE_COLUMN_LIMIT = 10
FAILED_COLUMN_LIMIT = 10
QUARANTINED_COLUMN_LIMIT = 25
ARCHIVED_COLUMN_LIMIT = 50
CREATOR_QC_PRIORITY = 1000
AMANOBA_VERSION = "0.2.0"
DEFAULT_RESIDENT_CREATOR_ROLES = [
    {"name": "DRAFTER", "host": "127.0.0.1", "port": 8080},
    {"name": "WRITER", "host": "127.0.0.1", "port": 8081},
    {"name": "JUDGE", "host": "127.0.0.1", "port": 8082},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_text(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _resident_role_health_payload(host: str, port: int, timeout: float = 1.5) -> dict[str, Any] | None:
    url = f"http://{host}:{port}/health"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
            return body if isinstance(body, dict) else None
    except Exception:
        return None


class TaskProcessingError(RuntimeError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = dict(details or {})


def acquire_process_lock(lock_path: Path) -> int | None:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        return None
    os.ftruncate(fd, 0)
    os.write(fd, str(os.getpid()).encode("utf-8"))
    return fd


def release_process_lock(fd: int | None) -> None:
    if fd is None:
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _normalize_lesson_payload(payload: dict[str, Any]) -> dict[str, str]:
    title = str(payload.get("title") or "").strip()
    content_value = payload.get("content")
    content = _coerce_lesson_content(title, content_value)
    email_subject = str(payload.get("emailSubject") or title).strip()
    email_body = str(payload.get("emailBody") or "").strip()
    if not email_body:
        if content:
            email_body = content[:500].strip()
        elif title:
            email_body = f"## Today\n{title}"
    return {
        "title": title,
        "content": content,
        "emailSubject": email_subject,
        "emailBody": email_body,
    }


def _coerce_lesson_content(title: str, content_value: Any) -> str:
    if isinstance(content_value, dict):
        return _render_lesson_content_from_mapping(title, content_value)
    content = str(content_value or "").strip()
    if not content:
        return ""
    if content.startswith("{") and content.endswith("}"):
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(content)
            except Exception:
                continue
            if isinstance(parsed, dict):
                return _render_lesson_content_from_mapping(title, parsed)
    return content


def _render_lesson_content_from_mapping(title: str, data: dict[str, Any]) -> str:
    resolved_title = str(data.get("title") or title or "").strip()
    body = str(data.get("body") or data.get("content") or "").strip()
    steps = data.get("steps") or []
    lines: list[str] = []
    if resolved_title:
        lines.append(f"# {resolved_title}")
    if body:
        lines.append("")
        lines.append("## Learning goal")
        lines.append(body)
    if isinstance(steps, list) and steps:
        lines.append("")
        lines.append("## Guided exercise")
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            step_title = str(step.get("title") or f"Step {index}").strip()
            step_desc = str(step.get("description") or "").strip()
            step_input = step.get("input")
            step_output = step.get("output")
            lines.append(f"### {step_title}")
            if step_desc:
                lines.append(step_desc)
            if isinstance(step_input, dict) and step_input:
                lines.append(f"- Input: {json.dumps(step_input, ensure_ascii=False)}")
            if isinstance(step_output, dict) and step_output:
                lines.append(f"- Output: {json.dumps(step_output, ensure_ascii=False)}")
    if not lines:
        return ""
    return "\n".join(lines).strip()


def _merge_lesson_payload(before: dict[str, Any], payload: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    normalized = _normalize_lesson_payload(payload)
    merged_fields: list[str] = []
    merged: dict[str, str] = {}
    for field in ["title", "content", "emailSubject", "emailBody"]:
        candidate = str(normalized.get(field) or "").strip()
        if candidate:
            merged[field] = candidate
            continue
        fallback = str(before.get(field) or "").strip()
        if field == "emailSubject" and not fallback:
            fallback = str(normalized.get("title") or before.get("title") or "").strip()
        if field == "emailBody" and not fallback:
            fallback = str(normalized.get("content") or before.get("content") or "").strip()[:500]
            if not fallback:
                title = str(normalized.get("title") or before.get("title") or "").strip()
                if title:
                    fallback = f"## Today\n{title}"
        merged[field] = fallback
        merged_fields.append(field)
    return merged, merged_fields


def _missing_lesson_fields(payload: dict[str, Any]) -> list[str]:
    return [field for field in ["title", "content", "emailSubject", "emailBody"] if not str(payload.get(field) or "").strip()]


def _looks_like_repairable_content_error(message: str) -> bool:
    lower = str(message or "").strip().lower()
    return (
        "does not show clear" in lower
        or "mixes languages" in lower
        or "language markers" in lower
        or "meta distractor" in lower
        or "rejected invalid question draft" in lower
        or "rejected invalid lesson draft" in lower
    )


def _creator_has_leakage(text: str) -> bool:
    lowered = str(text or "").strip().lower()
    return any(pattern in lowered for pattern in CREATOR_LEAK_PATTERNS)


DEFAULT_CREATOR_PIPELINE = {
    "drafter": {
        "tool": "MLX-LM",
        "model": "Gemma 3 270M",
        "label": "Gemma 3 270M",
        "provider": "mlx",
        "statusLabel": "drafting",
        "description": "Decomposes source material into atomic draft pieces and initial structure.",
    },
    "writer": {
        "tool": "MLX-LM",
        "model": "Granite 4.0 350M (H-variant)",
        "label": "Granite 4.0 350M (H-variant)",
        "provider": "mlx",
        "statusLabel": "enriching",
        "description": "Expands the draft into fluent, structured, publication-ready content.",
    },
    "judge": {
        "tool": "MLX-LM",
        "model": "Qwen 2.5 0.5B",
        "label": "Qwen 2.5 0.5B",
        "provider": "mlx",
        "statusLabel": "judging",
        "description": "Checks structure, language, and quality gates before acceptance.",
    },
}

CREATOR_LEAK_PATTERNS = (
    "localized lesson title",
    "localized subject line",
    "the best answer should",
    "distractors should",
    "generic action.",
    "incomplete delivery.",
    "focus ",
    "### what learners will be able to do",
)


LESSON_LANGUAGE_PACKS: dict[str, dict[str, str]] = {
    "en": {
        "goal": "Learning goal",
        "why": "Why it matters",
        "explanation": "Explanation",
        "example": "Example",
        "exercise": "Guided exercise",
        "self_check": "Self-check",
        "today": "Today",
        "open_lesson": "Open the lesson",
        "email_subject_prefix": "Lesson",
        "goal_text": "Build calm judgement and flexible action around {title}, so you can respond without losing focus when conditions change.",
        "why_text": "{title} matters because unexpected pressure usually creates confusion, delay, and avoidable mistakes. A simple response pattern helps you protect priorities, communicate clearly, and adapt without overreacting.",
        "explanation_text": "Start by naming what changed, what still matters, and what must happen next. Then separate facts from assumptions, reduce the problem into one or two concrete decisions, and choose the smallest useful next action. Use short feedback loops: act, check, adjust. This keeps momentum while avoiding panic and overcorrection.",
        "context_text": "In this course context, the lesson connects to {previous} and prepares the learner for {next}. That means the goal is not abstract resilience; it is practical, repeatable decision-making that supports the rest of the learning journey.",
        "example_text": "Imagine a plan breaks down halfway through the day: a colleague is blocked, a deadline moves, and your original schedule no longer fits reality. Instead of trying to preserve the old plan, you identify the true priority, communicate the new sequence, and reserve time for one fast review after the first adjustment.",
        "exercise_text": "Write down one current disruption you could realistically face this week. List the signal that tells you the situation changed, the priority that must still be protected, and the first action you would take in the next fifteen minutes. Then note what you would review after that first move.",
        "question_bridge": "Questions in this lesson focus on judgement under pressure, so the learner should leave with a clear way to decide, act, and adapt.",
        "self_check_text": "Can you describe the difference between reacting quickly and adapting deliberately? Can you name one sign that a plan should change, one priority that should stay stable, and one action you would take first?",
        "email_body": "## Today\n{summary}\n\nOpen the lesson to see a clear structure for noticing change, protecting priorities, and adapting with calm judgement.\n\nOpen the lesson ->",
    },
    "hu": {
        "goal": "Tanulási cél",
        "why": "Miért fontos",
        "explanation": "Magyarázat",
        "example": "Példa",
        "exercise": "Irányított gyakorlat",
        "self_check": "Önellenőrzés",
        "today": "Ma",
        "open_lesson": "Nyisd meg a leckét",
        "email_subject_prefix": "Lecke",
        "goal_text": "Építs tudatos döntési rutint a(z) {title} témájában, hogy váratlan helyzetben is higgadtan és rugalmasan tudj reagálni.",
        "why_text": "A(z) {title} azért fontos, mert a váratlan nyomás könnyen szétszórja a figyelmet és rossz sorrendbe kényszeríti a feladatokat. Egy egyszerű reakciós keret segít megőrizni a prioritásokat és csökkenteni a kapkodást.",
        "explanation_text": "Először nevezd meg, mi változott, mi maradt fontos, és mi a következő szükséges lépés. Ezután válaszd szét a tényeket a feltételezésektől, bontsd a helyzetet egy-két konkrét döntésre, majd indulj el a legkisebb hasznos lépéssel. Rövid visszacsatolási körökkel dolgozz: lépj, ellenőrizz, finomíts.",
        "context_text": "Ebben a kurzusban a lecke kapcsolódik ehhez: {previous}, és előkészíti ezt: {next}. A cél ezért nem elvont rugalmasság, hanem jól ismételhető döntési gyakorlat, amely a következő napokat is támogatja.",
        "example_text": "Képzeld el, hogy a nap közepén felborul a terved: valaki elakad, módosul a határidő, és az eredeti menetrend már nem működik. Ahelyett, hogy mindenáron ragaszkodnál a régi tervhez, újrasorrendezed a feladatokat, jelzed a változást, és rövid ellenőrzési pontot rögzítesz az első módosítás után.",
        "exercise_text": "Írj le egy olyan zavaró helyzetet, amely ezen a héten reálisan előfordulhat. Jegyezd fel, miből látod a változást, melyik prioritást kell megőrizni, és mi az első lépés, amit tizenöt percen belül megtennél. Végül írd le, mit ellenőriznél az első lépés után.",
        "question_bridge": "A kapcsolódó kérdések nyomás alatti döntésről szólnak, ezért a lecke végére legyen egy tiszta mintád arra, hogyan dönts, cselekedj és alkalmazkodj.",
        "self_check_text": "Meg tudod fogalmazni, mi a különbség a gyors reakció és a tudatos alkalmazkodás között? Fel tudsz sorolni egy jelet, amely változtatást kér, egy prioritást, amely marad, és egy első lépést, amit azonnal megtennél?",
        "email_body": "## Ma\n{summary}\n\nNyisd meg a leckét egy rövid, jól használható keretért arról, hogyan vedd észre a változást, hogyan őrizd meg a prioritásokat, és hogyan alkalmazkodj kapkodás nélkül.\n\nNyisd meg a leckét ->",
    },
    "pl": {
        "goal": "Cel nauki",
        "why": "Dlaczego to ważne",
        "explanation": "Wyjaśnienie",
        "example": "Przykład",
        "exercise": "Ćwiczenie",
        "self_check": "Samokontrola",
        "today": "Dzisiaj",
        "open_lesson": "Otwórz lekcję",
        "email_subject_prefix": "Lekcja",
        "goal_text": "Zbuduj spokojny sposób działania wokół tematu {title}, aby reagować na zmianę bez chaosu i bez utraty priorytetów.",
        "why_text": "{title} ma znaczenie, bo presja i nieoczekiwane zmiany szybko rozbijają plan dnia. Prosty schemat reakcji pomaga utrzymać kierunek, komunikować decyzje i dostosować działania bez paniki.",
        "explanation_text": "Najpierw nazwij, co się zmieniło, co nadal jest ważne i co musi wydarzyć się jako następny krok. Potem oddziel fakty od założeń, sprowadź sytuację do jednej lub dwóch decyzji i wybierz najmniejszy użyteczny ruch. Pracuj w krótkich pętlach: działanie, sprawdzenie, korekta. Dzięki temu zachowujesz tempo i nie reagujesz zbyt szeroko.",
        "context_text": "W kontekście tego kursu ta lekcja łączy się z tematem {previous} i przygotowuje grunt pod {next}. Celem nie jest więc ogólna odporność, ale praktyczny sposób podejmowania decyzji, który da się powtarzać w codziennej pracy.",
        "example_text": "Wyobraź sobie, że w połowie dnia plan przestaje działać: ktoś z zespołu utknął, termin się przesuwa, a dotychczasowa kolejność zadań traci sens. Zamiast bronić starego planu, ustalasz prawdziwy priorytet, jasno komunikujesz nową kolejność i planujesz szybki przegląd po pierwszej zmianie.",
        "exercise_text": "Zapisz jedną sytuację zakłócenia, która może wydarzyć się jeszcze w tym tygodniu. Określ sygnał, który pokaże Ci zmianę, priorytet, którego nie wolno zgubić, oraz pierwszy krok, który wykonasz w ciągu piętnastu minut. Na końcu dopisz, co sprawdzisz po tym pierwszym ruchu.",
        "question_bridge": "Pytania w tej lekcji dotyczą oceny sytuacji pod presją, dlatego po lekturze powinien zostać Ci prosty sposób: zauważ, zdecyduj, działaj i dostosuj.",
        "self_check_text": "Czy potrafisz wyjaśnić różnicę między szybką reakcją a świadomą adaptacją? Czy umiesz wskazać jeden sygnał zmiany, jeden stabilny priorytet i jeden pierwszy krok, który wykonasz od razu?",
        "email_body": "## Dzisiaj\n{summary}\n\nOtwórz lekcję, aby zobaczyć prostą strukturę reagowania na zmianę, ochrony priorytetów i spokojnej adaptacji w pracy.\n\nOtwórz lekcję ->",
    },
    "pt": {
        "goal": "Objetivo de aprendizado",
        "why": "Por que é importante",
        "explanation": "Explicação",
        "example": "Exemplo",
        "exercise": "Exercício guiado",
        "self_check": "Autoavaliação",
        "today": "Hoje",
        "open_lesson": "Abra a lição",
        "email_subject_prefix": "Lição",
        "goal_text": "Desenvolva um modo calmo de agir em torno de {title}, para responder a mudanças inesperadas sem perder prioridades.",
        "why_text": "{title} importa porque pressão e mudança costumam quebrar o plano inicial. Um roteiro simples de resposta ajuda a proteger o foco, comunicar decisões e adaptar o trabalho sem exagero.",
        "explanation_text": "Comece nomeando o que mudou, o que continua importante e o que precisa acontecer em seguida. Depois separe fatos de suposições, reduza a situação a uma ou duas decisões e escolha a menor ação útil. Trabalhe em ciclos curtos: agir, verificar, ajustar.",
        "context_text": "No contexto deste curso, esta lição se conecta a {previous} e prepara o terreno para {next}. O objetivo não é apenas falar de resiliência, mas criar um padrão prático de decisão que possa ser repetido no dia a dia.",
        "example_text": "Imagine que, no meio do dia, o plano deixa de funcionar: alguém do time trava, o prazo muda e a sequência anterior perde valor. Em vez de defender o plano antigo, você redefine a prioridade real, comunica a nova ordem e agenda uma revisão rápida após a primeira mudança.",
        "exercise_text": "Escreva uma interrupção realista que pode acontecer nesta semana. Liste o sinal que mostra a mudança, a prioridade que precisa permanecer protegida e a primeira ação que você tomaria nos próximos quinze minutos. Depois registre o que você revisaria após esse primeiro movimento.",
        "question_bridge": "As perguntas desta lição tratam de julgamento sob pressão, então a saída esperada é um jeito claro de perceber, decidir, agir e adaptar.",
        "self_check_text": "Você consegue explicar a diferença entre reagir rápido e adaptar-se com intenção? Consegue indicar um sinal de mudança, uma prioridade estável e a primeira ação que tomaria?",
        "email_body": "## Hoje\n{summary}\n\nAbra a lição para ver uma estrutura simples de resposta à mudança, proteção de prioridades e adaptação com clareza.\n\nAbra a lição ->",
    },
    "es": {
        "goal": "Objetivo de aprendizaje",
        "why": "Por qué importa",
        "explanation": "Explicación",
        "example": "Ejemplo",
        "exercise": "Ejercicio guiado",
        "self_check": "Autoevaluación",
        "today": "Hoy",
        "open_lesson": "Abre la lección",
        "email_subject_prefix": "Lección",
        "goal_text": "Construye una manera serena de actuar alrededor de {title}, para responder a cambios inesperados sin perder prioridades.",
        "why_text": "{title} importa porque la presión y los cambios inesperados rompen con facilidad el plan original. Un marco simple de respuesta ayuda a proteger el foco, comunicar decisiones y adaptarse sin pánico.",
        "explanation_text": "Primero nombra qué cambió, qué sigue siendo importante y qué debe ocurrir después. Luego separa hechos de suposiciones, reduce la situación a una o dos decisiones y elige la acción útil más pequeña. Trabaja en ciclos cortos: actuar, revisar, ajustar.",
        "context_text": "Dentro de este curso, esta lección se conecta con {previous} y prepara el terreno para {next}. La meta no es una resiliencia abstracta, sino un patrón práctico de decisión que pueda repetirse en el trabajo diario.",
        "example_text": "Imagina que a mitad del día el plan deja de funcionar: una persona del equipo se bloquea, el plazo cambia y el orden original ya no sirve. En lugar de defender el plan anterior, redefinirás la prioridad real, comunicarás la nueva secuencia y programarás una revisión rápida tras el primer ajuste.",
        "exercise_text": "Escribe una interrupción realista que podría ocurrir esta semana. Anota la señal que te mostraría el cambio, la prioridad que debe mantenerse y la primera acción que tomarías en los próximos quince minutos. Luego indica qué revisarías después de ese primer movimiento.",
        "question_bridge": "Las preguntas de esta lección se centran en el juicio bajo presión, así que el resultado esperado es un modo claro de observar, decidir, actuar y adaptarse.",
        "self_check_text": "¿Puedes explicar la diferencia entre reaccionar rápido y adaptarte con intención? ¿Puedes nombrar una señal de cambio, una prioridad estable y la primera acción que tomarías?",
        "email_body": "## Hoy\n{summary}\n\nAbre la lección para ver una estructura simple para responder al cambio, proteger prioridades y adaptarte con claridad.\n\nAbre la lección ->",
    },
    "vi": {
        "goal": "Mục tiêu học tập",
        "why": "Tại sao điều này quan trọng",
        "explanation": "Giải thích",
        "example": "Ví dụ",
        "exercise": "Bài tập có hướng dẫn",
        "self_check": "Tự kiểm tra",
        "today": "Hôm nay",
        "open_lesson": "Mở bài học",
        "email_subject_prefix": "Bài học",
        "goal_text": "Xây dựng cách phản ứng bình tĩnh với chủ đề {title}, để bạn có thể thích nghi trước thay đổi mà không làm mất ưu tiên quan trọng.",
        "why_text": "{title} quan trọng vì áp lực và thay đổi bất ngờ rất dễ làm kế hoạch ban đầu bị vỡ. Một khung phản ứng đơn giản giúp bạn giữ trọng tâm, giao tiếp rõ ràng và điều chỉnh hành động mà không hoảng loạn.",
        "explanation_text": "Trước hết hãy gọi tên điều gì đã thay đổi, điều gì vẫn quan trọng và bước tiếp theo bắt buộc là gì. Sau đó tách sự thật khỏi giả định, rút tình huống về một hoặc hai quyết định cụ thể và chọn hành động hữu ích nhỏ nhất để bắt đầu. Làm việc theo vòng ngắn: hành động, kiểm tra, điều chỉnh.",
        "context_text": "Trong mạch của khóa học này, bài học liên kết với {previous} và chuẩn bị cho {next}. Mục tiêu không phải là nói chung về khả năng chịu áp lực, mà là tạo ra một cách ra quyết định thực tế có thể lặp lại trong công việc hằng ngày.",
        "example_text": "Hãy tưởng tượng giữa ngày làm việc kế hoạch không còn phù hợp: một đồng nghiệp bị kẹt, thời hạn thay đổi và thứ tự công việc cũ không còn hiệu quả. Thay vì cố giữ kế hoạch cũ, bạn xác định lại ưu tiên thật sự, thông báo thứ tự mới và đặt một điểm kiểm tra nhanh sau điều chỉnh đầu tiên.",
        "exercise_text": "Viết ra một tình huống gián đoạn thực tế có thể xảy ra trong tuần này. Ghi lại tín hiệu cho thấy tình hình đã thay đổi, ưu tiên nào vẫn phải được bảo vệ và hành động đầu tiên bạn sẽ làm trong mười lăm phút tới. Cuối cùng, ghi thêm điều bạn sẽ kiểm tra sau bước đầu tiên đó.",
        "question_bridge": "Các câu hỏi đi kèm tập trung vào phán đoán dưới áp lực, vì vậy người học cần rời bài với một cách rõ ràng để quan sát, quyết định, hành động và thích nghi.",
        "self_check_text": "Bạn có thể giải thích sự khác nhau giữa phản ứng nhanh và thích nghi có chủ đích không? Bạn có thể nêu một tín hiệu thay đổi, một ưu tiên cần giữ ổn định và một hành động đầu tiên bạn sẽ thực hiện ngay không?",
        "email_body": "## Hôm nay\n{summary}\n\nMở bài học để xem một cấu trúc đơn giản giúp bạn phản ứng với thay đổi, bảo vệ ưu tiên và thích nghi một cách rõ ràng.\n\nMở bài học ->",
    },
    "id": {
        "goal": "Tujuan belajar",
        "why": "Mengapa ini penting",
        "explanation": "Penjelasan",
        "example": "Contoh",
        "exercise": "Latihan terpandu",
        "self_check": "Pemeriksaan mandiri",
        "today": "Hari ini",
        "open_lesson": "Buka pelajaran",
        "email_subject_prefix": "Pelajaran",
        "goal_text": "Bangun cara bertindak yang tenang dalam topik {title}, agar Anda bisa merespons perubahan tanpa kehilangan prioritas.",
        "why_text": "{title} penting karena tekanan dan perubahan mendadak mudah merusak rencana kerja. Kerangka respons yang sederhana membantu menjaga fokus, mengomunikasikan keputusan, dan menyesuaikan langkah tanpa panik.",
        "explanation_text": "Mulailah dengan menamai apa yang berubah, apa yang tetap penting, dan apa yang harus dilakukan berikutnya. Lalu pisahkan fakta dari asumsi, sederhanakan situasi menjadi satu atau dua keputusan, dan pilih tindakan berguna terkecil. Bekerjalah dalam siklus pendek: bertindak, memeriksa, menyesuaikan.",
        "context_text": "Dalam konteks kursus ini, pelajaran ini terhubung dengan {previous} dan menyiapkan landasan untuk {next}. Tujuannya bukan sekadar ketahanan yang abstrak, tetapi pola pengambilan keputusan yang praktis dan dapat diulang.",
        "example_text": "Bayangkan di tengah hari rencana tidak lagi berjalan: rekan kerja terhambat, tenggat berubah, dan urutan tugas lama tidak lagi cocok. Alih-alih mempertahankan rencana lama, Anda menetapkan prioritas yang sebenarnya, mengomunikasikan urutan baru, dan menjadwalkan tinjauan singkat setelah perubahan pertama.",
        "exercise_text": "Tuliskan satu gangguan realistis yang bisa terjadi minggu ini. Catat sinyal yang menunjukkan perubahan, prioritas yang tetap harus dilindungi, dan tindakan pertama yang akan Anda ambil dalam lima belas menit ke depan. Setelah itu, tuliskan apa yang akan Anda cek sesudah langkah pertama tersebut.",
        "question_bridge": "Pertanyaan dalam pelajaran ini berfokus pada penilaian saat tekanan tinggi, jadi hasil akhirnya harus berupa cara yang jelas untuk melihat situasi, memutuskan, bertindak, dan menyesuaikan diri.",
        "self_check_text": "Bisakah Anda menjelaskan perbedaan antara bereaksi cepat dan beradaptasi dengan sengaja? Bisakah Anda menyebutkan satu tanda perubahan, satu prioritas tetap, dan satu tindakan pertama yang akan Anda ambil?",
        "email_body": "## Hari ini\n{summary}\n\nBuka pelajaran untuk melihat struktur sederhana dalam merespons perubahan, menjaga prioritas, dan menyesuaikan diri dengan tenang.\n\nBuka pelajaran ->",
    },
    "ar": {
        "goal": "هدف التعلّم",
        "why": "لماذا هذا مهم",
        "explanation": "الشرح",
        "example": "مثال",
        "exercise": "تمرين موجّه",
        "self_check": "تحقق ذاتي",
        "today": "اليوم",
        "open_lesson": "افتح الدرس",
        "email_subject_prefix": "درس",
        "goal_text": "ابنِ طريقة هادئة للعمل حول موضوع {title} حتى تتمكن من الاستجابة للتغيير من دون فقدان الأولويات.",
        "why_text": "تزداد أهمية {title} لأن الضغط والتغيير المفاجئ قد يربكان الخطة بسرعة. يساعدك إطار استجابة بسيط على حماية التركيز، وتوضيح القرار، والتكيّف من دون ارتباك.",
        "explanation_text": "ابدأ بتحديد ما الذي تغيّر، وما الذي ما زال مهمًا، وما الخطوة التالية المطلوبة. ثم افصل بين الحقائق والافتراضات، وقلّص الموقف إلى قرار أو قرارين، واختر أصغر خطوة مفيدة. اعمل في دورات قصيرة: تحرّك، تحقّق، عدّل.",
        "context_text": "ضمن سياق هذا المساق، يرتبط هذا الدرس بموضوع {previous} ويمهّد لـ {next}. الهدف ليس الحديث المجرد عن المرونة، بل بناء نمط عملي ومتكرر لاتخاذ القرار.",
        "example_text": "تخيّل أن خطتك تعطلت في منتصف اليوم: زميل تعثّر، وموعد نهائي تغيّر، وترتيب العمل القديم لم يعد مناسبًا. بدلًا من التمسك بالخطة القديمة، تحدد الأولوية الحقيقية، وتعلن الترتيب الجديد، وتضع مراجعة سريعة بعد أول تعديل.",
        "exercise_text": "اكتب موقف تعطّل واقعي قد يحدث هذا الأسبوع. حدّد الإشارة التي تخبرك أن الوضع تغيّر، والأولوية التي يجب أن تبقى محفوظة، وأول خطوة ستقوم بها خلال الخمس عشرة دقيقة التالية. ثم دوّن ما الذي ستراجعه بعد تلك الخطوة.",
        "question_bridge": "تركّز أسئلة هذا الدرس على الحكم تحت الضغط، لذلك يجب أن يخرج المتعلم بطريقة واضحة للملاحظة والقرار والتصرف والتكيّف.",
        "self_check_text": "هل تستطيع شرح الفرق بين رد الفعل السريع والتكيّف المقصود؟ وهل يمكنك تسمية إشارة تغيير واحدة، وأولوية ثابتة واحدة، وخطوة أولى ستقوم بها فورًا؟",
        "email_body": "## اليوم\n{summary}\n\nافتح الدرس لترى بنية بسيطة تساعدك على ملاحظة التغيير، وحماية الأولويات، والتكيّف بوضوح.\n\nافتح الدرس ->",
    },
    "bg": {
        "goal": "Учебна цел",
        "why": "Защо е важно",
        "explanation": "Обяснение",
        "example": "Пример",
        "exercise": "Насочено упражнение",
        "self_check": "Самопроверка",
        "today": "Днес",
        "open_lesson": "Отвори урока",
        "email_subject_prefix": "Урок",
        "goal_text": "Изгради спокоен начин на действие около темата {title}, за да реагираш на промяна, без да губиш приоритетите си.",
        "why_text": "{title} е важно, защото натискът и неочакваната промяна лесно разбиват първоначалния план. Прост модел за реакция помага да запазиш фокуса, да комуникираш ясно и да се адаптираш без хаос.",
        "explanation_text": "Започни с това да назовеш какво се е променило, какво остава важно и каква е следващата необходима стъпка. После отдели фактите от предположенията, сведи ситуацията до едно или две решения и избери най-малкото полезно действие. Работи в кратки цикли: действай, провери, коригирай.",
        "context_text": "В контекста на този курс урокът се свързва с {previous} и подготвя основа за {next}. Целта не е абстрактна устойчивост, а практичен модел за решения, който може да се повтаря в реалната работа.",
        "example_text": "Представи си, че по средата на деня планът спира да работи: колега е блокиран, срокът се измества и старият ред на задачите вече не помага. Вместо да защитаваш стария план, определяш истинския приоритет, комуникираш новия ред и планираш кратка проверка след първата промяна.",
        "exercise_text": "Запиши едно реалистично прекъсване, което може да се случи тази седмица. Посочи сигнала, че ситуацията се е променила, приоритета, който трябва да остане защитен, и първото действие, което би предприел в следващите петнадесет минути. Накрая запиши какво ще провериш след тази първа стъпка.",
        "question_bridge": "Въпросите в този урок са свързани с преценка под натиск, затова резултатът трябва да е ясен начин да виждаш ситуацията, да решаваш, да действаш и да се адаптираш.",
        "self_check_text": "Можеш ли да обясниш разликата между бърза реакция и умишлена адаптация? Можеш ли да назовеш един сигнал за промяна, един стабилен приоритет и една първа стъпка, която би направил веднага?",
        "email_body": "## Днес\n{summary}\n\nОтвори урока, за да видиш проста структура за реакция при промяна, защита на приоритетите и спокойно адаптиране.\n\nОтвори урока ->",
    },
    "hi": {
        "goal": "सीखने का लक्ष्य",
        "why": "यह क्यों महत्वपूर्ण है",
        "explanation": "व्याख्या",
        "example": "उदाहरण",
        "exercise": "निर्देशित अभ्यास",
        "self_check": "स्व-जांच",
        "today": "आज",
        "open_lesson": "पाठ खोलें",
        "email_subject_prefix": "पाठ",
        "goal_text": "{title} के आसपास शांत और व्यावहारिक निर्णय-पद्धति बनाइए, ताकि बदलती परिस्थितियों में भी आप प्राथमिकताएँ खोए बिना प्रतिक्रिया दे सकें।",
        "why_text": "{title} महत्वपूर्ण है क्योंकि दबाव और अचानक बदलाव मूल योजना को जल्दी तोड़ देते हैं। एक सरल प्रतिक्रिया-ढांचा आपको फोकस बनाए रखने, निर्णय स्पष्ट करने और बिना घबराहट के अनुकूल होने में मदद करता है।",
        "explanation_text": "पहले यह पहचानिए कि क्या बदला है, क्या अभी भी महत्वपूर्ण है, और अगला आवश्यक कदम क्या है। फिर तथ्यों और धारणाओं को अलग कीजिए, स्थिति को एक या दो ठोस निर्णयों तक सीमित कीजिए, और सबसे छोटी उपयोगी कार्रवाई चुनिए। छोटे चक्रों में काम कीजिए: कार्य, जाँच, सुधार।",
        "context_text": "इस पाठ्यक्रम के संदर्भ में यह पाठ {previous} से जुड़ता है और {next} के लिए आधार तैयार करता है। लक्ष्य केवल अमूर्त लचीलापन नहीं, बल्कि दोहराई जा सकने वाली व्यावहारिक निर्णय-प्रक्रिया है।",
        "example_text": "कल्पना कीजिए कि दिन के बीच में आपकी योजना बिगड़ जाती है: कोई सहकर्मी अटक गया, समय-सीमा बदल गई, और पुराना कार्य-क्रम अब उपयोगी नहीं रहा। पुरानी योजना से चिपके रहने के बजाय, आप असली प्राथमिकता तय करते हैं, नया क्रम बताते हैं, और पहले बदलाव के बाद एक छोटी समीक्षा तय करते हैं।",
        "exercise_text": "इस सप्ताह होने वाली एक वास्तविक व्यवधान-स्थिति लिखिए। वह संकेत लिखिए जो बताए कि स्थिति बदल गई है, वह प्राथमिकता लिखिए जिसे बचाकर रखना है, और वह पहला कदम लिखिए जो आप अगले पंद्रह मिनट में उठाएँगे। अंत में लिखिए कि उस पहले कदम के बाद आप क्या जाँचेंगे।",
        "question_bridge": "इस पाठ के प्रश्न दबाव में निर्णय-क्षमता पर केंद्रित हैं, इसलिए सीखने वाले के पास देखने, तय करने, कार्य करने और अनुकूल होने का स्पष्ट तरीका बचना चाहिए।",
        "self_check_text": "क्या आप तेज प्रतिक्रिया और सोच-समझकर अनुकूलन के बीच अंतर समझा सकते हैं? क्या आप बदलाव का एक संकेत, एक स्थिर प्राथमिकता और एक पहला कदम बता सकते हैं जिसे आप तुरंत उठाएँगे?",
        "email_body": "## आज\n{summary}\n\nपाठ खोलें और देखें कि बदलाव को पहचानने, प्राथमिकताओं की रक्षा करने और स्पष्टता के साथ अनुकूल होने की सरल संरचना कैसी दिखती है।\n\nपाठ खोलें ->",
    },
    "ru": {
        "goal": "Цель обучения",
        "why": "Почему это важно",
        "explanation": "Объяснение",
        "example": "Пример",
        "exercise": "Упражнение",
        "self_check": "Самопроверка",
        "today": "Сегодня",
        "open_lesson": "Открой урок",
        "email_subject_prefix": "Урок",
        "goal_text": "Сформируйте спокойный способ действий вокруг темы {title}, чтобы отвечать на изменения без потери приоритетов.",
        "why_text": "{title} важно, потому что давление и неожиданные изменения быстро ломают исходный план. Простой шаблон реакции помогает сохранить фокус, ясно сообщать решения и адаптироваться без лишней суеты.",
        "explanation_text": "Сначала назовите, что изменилось, что по-прежнему важно и что должно произойти дальше. Затем отделите факты от предположений, сведите ситуацию к одному-двум решениям и выберите самое маленькое полезное действие. Работайте короткими циклами: действие, проверка, корректировка.",
        "context_text": "В контексте этого курса урок связан с темой {previous} и подготавливает переход к {next}. Цель здесь не в абстрактной устойчивости, а в практическом шаблоне решений, который можно повторять в повседневной работе.",
        "example_text": "Представьте, что в середине дня план перестал работать: коллега застрял, срок сдвинулся, а прежняя последовательность задач уже не подходит. Вместо защиты старого плана вы определяете реальный приоритет, сообщаете новый порядок и ставите короткую проверку после первого изменения.",
        "exercise_text": "Опишите одно реалистичное нарушение хода работы, которое может случиться на этой неделе. Запишите сигнал изменения, приоритет, который нельзя потерять, и первое действие, которое вы выполните в ближайшие пятнадцать минут. Затем отметьте, что вы проверите после этого шага.",
        "question_bridge": "Вопросы в этом уроке связаны с суждением под давлением, поэтому у ученика должен остаться понятный способ замечать, решать, действовать и адаптироваться.",
        "self_check_text": "Можете ли вы объяснить разницу между быстрой реакцией и осознанной адаптацией? Можете ли назвать один сигнал изменения, один стабильный приоритет и первое действие, которое вы бы сделали?",
        "email_body": "## Сегодня\n{summary}\n\nОткрой урок, чтобы увидеть простую структуру реакции на изменения, защиты приоритетов и спокойной адаптации.\n\nОткрой урок ->",
    },
    "sw": {
        "goal": "Lengo la kujifunza",
        "why": "Kwa nini hili ni muhimu",
        "explanation": "Maelezo",
        "example": "Mfano",
        "exercise": "Zoezi la mwongozo",
        "self_check": "Kujihakiki",
        "today": "Leo",
        "open_lesson": "Fungua somo",
        "email_subject_prefix": "Somo",
        "goal_text": "Jenga namna tulivu ya kutenda kuhusu mada ya {title}, ili uweze kujibu mabadiliko bila kupoteza vipaumbele.",
        "why_text": "{title} ni muhimu kwa sababu shinikizo na mabadiliko ya ghafla huvunja mpango wa awali kwa haraka. Mfumo rahisi wa mwitikio hukusaidia kulinda mwelekeo, kueleza maamuzi wazi, na kuzoea bila taharuki.",
        "explanation_text": "Anza kwa kutaja kilichobadilika, kile ambacho bado ni muhimu, na hatua inayofuata inayohitajika. Kisha tenganisha ukweli na makisio, punguza hali hadi uamuzi mmoja au miwili, na chagua hatua ndogo yenye manufaa. Fanya kazi kwa mizunguko mifupi: chukua hatua, kagua, rekebisha.",
        "context_text": "Katika muktadha wa kozi hii, somo hili linaungana na {previous} na linakuandaa kwa {next}. Lengo si kuzungumzia uimara kwa jumla, bali ni kujenga mtindo wa maamuzi wa vitendo unaoweza kurudiwa kazini.",
        "example_text": "Fikiria katikati ya siku mpango wako hauendi tena sawa: mwenzako amekwama, muda wa mwisho umebadilika, na mpangilio wa zamani wa kazi haukusaidii tena. Badala ya kushikilia mpango wa zamani, unaweka kipaumbele halisi, unaeleza mpangilio mpya, na unapanga ukaguzi mfupi baada ya mabadiliko ya kwanza.",
        "exercise_text": "Andika usumbufu mmoja wa kweli unaoweza kutokea wiki hii. Taja ishara inayoonyesha hali imebadilika, kipaumbele kinachopaswa kulindwa, na hatua ya kwanza utakayochukua ndani ya dakika kumi na tano zijazo. Kisha andika utakachokagua baada ya hatua hiyo ya kwanza.",
        "question_bridge": "Maswali ya somo hili yanahusu uamuzi chini ya shinikizo, hivyo matokeo yanapaswa kuwa njia wazi ya kuona hali, kuamua, kutenda, na kuzoea.",
        "self_check_text": "Je, unaweza kueleza tofauti kati ya kuitikia haraka na kuzoea kwa makusudi? Je, unaweza kutaja ishara moja ya mabadiliko, kipaumbele kimoja thabiti, na hatua moja ya kwanza ambayo ungechukua mara moja?",
        "email_body": "## Leo\n{summary}\n\nFungua somo uone muundo rahisi wa kuitikia mabadiliko, kulinda vipaumbele, na kuzoea kwa uwazi.\n\nFungua somo ->",
    },
    "sv": {
        "goal": "Lärandemål",
        "why": "Varför det är viktigt",
        "explanation": "Förklaring",
        "example": "Exempel",
        "exercise": "Guidad övning",
        "self_check": "Självkontroll",
        "today": "I dag",
        "open_lesson": "Öppna lektionen",
        "email_subject_prefix": "Lektion",
        "goal_text": "Bygg ett lugnt arbetssätt kring {title}, så att du kan svara på förändring utan att tappa prioriteringar.",
        "why_text": "{title} är viktigt eftersom press och oväntade förändringar snabbt kan bryta den ursprungliga planen. En enkel responsmodell hjälper dig att skydda fokus, kommunicera beslut och anpassa dig utan panik.",
        "explanation_text": "Börja med att sätta ord på vad som har förändrats, vad som fortfarande är viktigt och vad som måste hända härnäst. Skilj sedan fakta från antaganden, reducera läget till en eller två beslut och välj den minsta användbara handlingen. Arbeta i korta slingor: agera, kontrollera, justera.",
        "context_text": "I kursens sammanhang hänger den här lektionen ihop med {previous} och förbereder för {next}. Målet är alltså inte abstrakt motståndskraft, utan ett praktiskt beslutsmönster som går att upprepa i vardagen.",
        "example_text": "Tänk dig att planen mitt på dagen slutar fungera: en kollega fastnar, en deadline ändras och den gamla ordningen tappar värde. I stället för att försvara den gamla planen sätter du en ny verklig prioritet, kommunicerar den nya ordningen och bokar en snabb avstämning efter den första ändringen.",
        "exercise_text": "Skriv ned en realistisk störning som kan inträffa den här veckan. Ange signalen som visar att läget har ändrats, prioriteten som fortfarande måste skyddas och den första handlingen du skulle ta inom femton minuter. Skriv sedan vad du skulle följa upp efter det första steget.",
        "question_bridge": "Frågorna i lektionen handlar om omdöme under press, så resultatet ska vara ett tydligt sätt att se, besluta, agera och anpassa sig.",
        "self_check_text": "Kan du förklara skillnaden mellan att reagera snabbt och att anpassa sig med avsikt? Kan du nämna en signal om förändring, en stabil prioritet och den första handling du skulle ta?",
        "email_body": "## I dag\n{summary}\n\nÖppna lektionen för att se en enkel struktur för att svara på förändring, skydda prioriteringar och anpassa dig med klarhet.\n\nÖppna lektionen ->",
    },
    "tr": {
        "goal": "Öğrenme hedefi",
        "why": "Neden önemli",
        "explanation": "Açıklama",
        "example": "Örnek",
        "exercise": "Yönlendirmeli alıştırma",
        "self_check": "Öz kontrol",
        "today": "Bugün",
        "open_lesson": "Dersi aç",
        "email_subject_prefix": "Ders",
        "goal_text": "{title} konusunda sakin ve uygulanabilir bir karar düzeni kur, böylece değişime önceliklerini kaybetmeden yanıt verebil.",
        "why_text": "{title} önemlidir çünkü baskı ve beklenmedik değişiklikler ilk planı hızla bozar. Basit bir tepki çerçevesi odağı korumana, kararları netleştirmene ve paniğe kapılmadan uyum sağlamana yardımcı olur.",
        "explanation_text": "Önce neyin değiştiğini, neyin hâlâ önemli olduğunu ve sıradaki gerekli adımın ne olduğunu adlandır. Sonra gerçekleri varsayımlardan ayır, durumu bir veya iki karara indir ve en küçük faydalı adımı seç. Kısa döngülerle ilerle: harekete geç, kontrol et, ayarla.",
        "context_text": "Bu kurs bağlamında bu ders {previous} ile bağlantılıdır ve {next} için zemin hazırlar. Amaç soyut bir dayanıklılık anlatmak değil, günlük işte tekrarlanabilir pratik bir karar modeli kurmaktır.",
        "example_text": "Günün ortasında planının artık işlemediğini düşün: bir ekip arkadaşı takıldı, son tarih değişti ve eski görev sırası anlamını yitirdi. Eski planı savunmak yerine gerçek önceliği belirler, yeni sırayı açıkça paylaşırsın ve ilk değişiklikten sonra kısa bir gözden geçirme planlarsın.",
        "exercise_text": "Bu hafta yaşanabilecek gerçekçi bir aksaklık yaz. Değişimi gösterecek işareti, korunması gereken önceliği ve önümüzdeki on beş dakika içinde atacağın ilk adımı not et. Ardından bu ilk adımdan sonra neyi kontrol edeceğini yaz.",
        "question_bridge": "Bu dersteki sorular baskı altında muhakemeye odaklanır; bu yüzden öğrenenin elinde durumu görme, karar verme, harekete geçme ve uyum sağlama konusunda net bir yol kalmalıdır.",
        "self_check_text": "Hızlı tepki ile bilinçli uyum arasındaki farkı açıklayabilir misin? Bir değişim işareti, sabit kalması gereken bir öncelik ve hemen atacağın ilk adımı söyleyebilir misin?",
        "email_body": "## Bugün\n{summary}\n\nDeğişimi fark etme, öncelikleri koruma ve netlikle uyum sağlama konusunda basit bir yapı görmek için dersi aç.\n\nDersi aç ->",
    },
}


def _lesson_language_pack(code: str | None) -> dict[str, str]:
    return LESSON_LANGUAGE_PACKS.get(str(code or "").strip().lower(), LESSON_LANGUAGE_PACKS["en"])


def _has_lesson_language_pack(code: str | None) -> bool:
    return str(code or "").strip().lower() in LESSON_LANGUAGE_PACKS

@dataclass
class Config:
    config_path: Path
    power_mode: str
    workspace_root: Path
    source_mode: str
    state_db_path: Path
    backups_dir: Path
    reports_dir: Path
    scan_interval_seconds: int
    scan_globs: list[str]
    ignore_dirs: set[str]
    apply_fixes: bool
    fix_questions: bool
    fix_lessons: bool
    max_attempts_per_task: int
    feed_limit: int
    queue_check_interval_seconds: int
    idle_sleep_seconds: int
    post_task_sleep_seconds: int
    action_feed_limit: int
    max_task_runtime_seconds: int
    quarantine_after_failures: int
    runtime_config: dict[str, Any]
    live_app_root: Path | None
    live_bridge_script: str | None
    live_actor: str
    live_batch_size: int
    live_batch_passes: int
    live_bridge_timeout_seconds: int
    dashboard_host: str
    dashboard_port: int

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        raw = json.loads(path.read_text(encoding="utf-8"))
        root = path.parent.resolve()

        def resolve(value: str) -> Path:
            return resolve_portable_path(value, base_dir=root)

        return cls(
            config_path=path.resolve(),
            power_mode=str(raw.get("power_mode") or "balanced"),
            workspace_root=resolve(raw["workspace_root"]),
            source_mode=str(raw.get("source_mode") or "files").strip().lower(),
            state_db_path=resolve(raw["state_db_path"]),
            backups_dir=resolve(raw["backups_dir"]),
            reports_dir=resolve(raw["reports_dir"]),
            scan_interval_seconds=int(raw.get("scan_interval_seconds", 300)),
            scan_globs=list(raw.get("scan_globs", ["**/*.json"])),
            ignore_dirs=set(raw.get("ignore_dirs", [".course-quality", "__pycache__"])),
            apply_fixes=bool(raw.get("apply_fixes", True)),
            fix_questions=bool(raw.get("fix_questions", True)),
            fix_lessons=bool(raw.get("fix_lessons", False)),
            max_attempts_per_task=int(raw.get("max_attempts_per_task", 5)),
            feed_limit=int(raw.get("feed_limit", DEFAULT_FEED_LIMIT)),
            queue_check_interval_seconds=int(raw.get("queue_check_interval_seconds", 300)),
            idle_sleep_seconds=int(raw.get("idle_sleep_seconds", 15)),
            post_task_sleep_seconds=int(raw.get("post_task_sleep_seconds", 20)),
            action_feed_limit=int(raw.get("action_feed_limit", 3)),
            max_task_runtime_seconds=int(raw.get("max_task_runtime_seconds", 900)),
            quarantine_after_failures=int((raw.get("watchdog") or {}).get("quarantine_after_failures") or 2),
            runtime_config=dict(raw.get("runtime") or {}),
            live_app_root=resolve(str(raw.get("live", {}).get("app_root"))) if raw.get("live", {}).get("app_root") else None,
            live_bridge_script=str(raw.get("live", {}).get("bridge_script") or "scripts/course-quality-live-bridge.ts"),
            live_actor=str(raw.get("live", {}).get("actor") or "course-quality-daemon"),
            live_batch_size=int(raw.get("live", {}).get("batch_size") or 25),
            live_batch_passes=int(raw.get("live", {}).get("batch_passes") or 8),
            live_bridge_timeout_seconds=int(raw.get("live", {}).get("bridge_timeout_seconds") or 120),
            dashboard_host=str(raw.get("dashboard", {}).get("host") or "127.0.0.1"),
            dashboard_port=int(raw.get("dashboard", {}).get("port") or 8765),
        )


class StateStore:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self.reset_running_tasks()

    def _init_schema(self) -> None:
        with self._lock:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS packages (
                    path TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    course_id TEXT,
                    language TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tasks (
                    task_key TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    package_path TEXT NOT NULL,
                    course_id TEXT,
                    language TEXT,
                    lesson_id TEXT,
                    question_uuid TEXT,
                    question_index INTEGER,
                    source_hash TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    details_json TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS task_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_key TEXT NOT NULL,
                    comment TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS creator_runs (
                    run_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    research_mode TEXT NOT NULL,
                    status TEXT NOT NULL,
                    current_stage TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS creator_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    stage_key TEXT NOT NULL,
                    action TEXT NOT NULL,
                    comment TEXT,
                    payload_json TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            pragma_rows = self.conn.execute("PRAGMA table_info(tasks)").fetchall()
            columns = {str(row["name"] if isinstance(row, sqlite3.Row) else row[1]) for row in pragma_rows}
            for name in ["created_at", "started_at", "finished_at"]:
                if name not in columns:
                    self.conn.execute(f"ALTER TABLE tasks ADD COLUMN {name} TEXT")
            if "priority" not in columns:
                self.conn.execute("ALTER TABLE tasks ADD COLUMN priority INTEGER NOT NULL DEFAULT 0")
            self.conn.execute("UPDATE tasks SET created_at = COALESCE(created_at, updated_at) WHERE created_at IS NULL")
            self.conn.execute("UPDATE tasks SET priority = COALESCE(priority, 0) WHERE priority IS NULL")
            self.conn.commit()

    def _creator_stage_template(self) -> list[dict[str, str]]:
        return [
            {"key": "topic_intake", "label": "Topic Intake", "status": "completed"},
            {"key": "research", "label": "Research", "status": "active"},
            {"key": "blueprint", "label": "Blueprint", "status": "blocked"},
            {"key": "lesson_generation", "label": "Lesson Generation", "status": "blocked"},
            {"key": "quiz_generation", "label": "Quiz Generation", "status": "blocked"},
            {"key": "qc_review", "label": "QC Review", "status": "blocked"},
            {"key": "draft_to_live", "label": "Draft To Live", "status": "blocked"},
        ]

    def _creator_stage_artifacts(self, topic: str, target_language: str, research_mode: str) -> dict[str, dict[str, Any]]:
        compact_topic = topic.strip()
        return {
            "research": {
                "title": "Research Brief",
                "format": "markdown",
                "content": (
                    f"# Research Brief\n\n"
                    f"## Topic\n{compact_topic}\n\n"
                    f"## Target Language\n{target_language}\n\n"
                    f"## Research Mode\n{research_mode}\n\n"
                    f"## Core Learner Problem\n"
                    f"Define the real job-to-be-done behind '{compact_topic}' and the learner state before the course starts.\n\n"
                    f"## Primary Audience Hypotheses\n"
                    f"- Identify the primary learner segment.\n"
                    f"- Define the likely skill level.\n"
                    f"- Note the workplace or life context where the course will be used.\n\n"
                    f"## Outcome Hypotheses\n"
                    f"- What should the learner be able to do after completion?\n"
                    f"- What decisions or actions should become easier?\n"
                    f"- What bad outcomes should the course help avoid?\n\n"
                    f"## Scope Boundaries\n"
                    f"- What this course must cover.\n"
                    f"- What this course must not try to cover.\n"
                    f"- What should be left for follow-up courses.\n\n"
                    f"## Evidence And Freshness Needs\n"
                    f"- List the knowledge areas that require current evidence.\n"
                    f"- Mark which parts are timeless and which parts are time-sensitive.\n"
                    f"- Note where English fallback would be acceptable only if target-language evidence is weak.\n\n"
                    f"## Risks To Prevent\n"
                    f"- Mixed-language output.\n"
                    f"- Generic lesson titles with no action value.\n"
                    f"- Quiz questions that test recall instead of application.\n"
                    f"- Unsupported factual claims.\n"
                ),
            },
            "blueprint": {
                "title": "Course Blueprint",
                "format": "markdown",
                "content": "",
            },
            "lesson_generation": {
                "title": "Lesson Generation Workbench",
                "format": "markdown",
                "content": "",
            },
            "quiz_generation": {
                "title": "Quiz Generation Workbench",
                "format": "markdown",
                "content": "",
            },
            "qc_review": {
                "title": "QC Handoff",
                "format": "markdown",
                "content": (
                    "# QC Handoff\n\n"
                    "## Objective\nMove the approved draft into the local quality-control queue at top priority.\n\n"
                    "## Exit Condition\nThe draft is clean enough for final human review and live promotion."
                ),
            },
            "draft_to_live": {
                "title": "Draft To Live Decision",
                "format": "markdown",
                "content": (
                    "# Draft To Live Decision\n\n"
                    "## Final Checks\n"
                    "- All approved stages complete.\n"
                    "- QC pass recorded.\n"
                    "- Target-language integrity preserved.\n"
                    "- Human signoff ready.\n"
                ),
            },
        }

    def _creator_stage_contracts(self) -> dict[str, dict[str, Any]]:
        return {
            "research": {
                "owner": "drafter",
                "requiredKeys": ["title", "format", "content"],
                "optionalKeys": ["updatedAt", "provenance", "notes"],
                "rejectWhen": ["empty content", "mixed language", "missing source grounding"],
            },
            "blueprint": {
                "owner": "drafter",
                "requiredKeys": ["title", "format", "content"],
                "optionalKeys": ["updatedAt", "provenance", "notes"],
                "rejectWhen": ["non-30-day structure", "mixed language", "generic outline"],
            },
            "lesson_generation": {
                "owner": "writer",
                "requiredKeys": ["title", "format", "content", "emailSubject", "emailBody"],
                "optionalKeys": ["updatedAt", "provenance", "notes"],
                "rejectWhen": ["missing canonical blocks", "mixed language", "too short"],
            },
            "quiz_generation": {
                "owner": "writer",
                "requiredKeys": ["title", "format", "content"],
                "optionalKeys": ["updatedAt", "provenance", "notes"],
                "rejectWhen": ["weak distractors", "template leakage", "too short"],
            },
            "qc_review": {
                "owner": "judge",
                "requiredKeys": ["title", "format", "content"],
                "optionalKeys": ["generatedAt", "provenance", "notes", "qcPlan"],
                "rejectWhen": ["unvalidated handoff", "missing qc tasks", "empty review"],
            },
            "draft_to_live": {
                "owner": "judge",
                "requiredKeys": ["title", "format", "content"],
                "optionalKeys": ["generatedAt", "provenance", "notes", "draftToLiveJudge"],
                "rejectWhen": ["unfinished qc", "missing import status", "missing publish readiness"],
            },
        }

    def _creator_stage_retry_policy(self) -> dict[str, Any]:
        return {
            "maxAttempts": 5,
            "stopWhenNoProgress": True,
            "stopWhenFailureRepeats": True,
            "feedbackFlow": ["user->judge", "judge->writer", "writer->drafter"],
        }

    def create_creator_run(self, topic: str, target_language: str, research_mode: str) -> dict[str, Any]:
        clean_topic = topic.strip()
        clean_language = target_language.strip().lower()
        clean_research = research_mode.strip().lower()
        if not clean_topic:
            raise ValueError("Topic is required.")
        if not clean_language:
            raise ValueError("Target language is required.")
        if clean_research not in {"offline", "optional", "required"}:
            raise ValueError("Research mode must be one of: offline, optional, required.")
        run_id = f"creator-{sha256_text(clean_topic + utc_now())[:12]}"
        now = utc_now()
        stage_blueprint = {
            "research": {
                "goal": f"Build a source-aware research brief for '{clean_topic}' in {clean_language}.",
                "checkpoint": "User accepts, updates, or deletes the research brief.",
            },
            "blueprint": {
                "goal": "Turn the approved research brief into a course architecture aligned to Amanoba CCS and live Course/Lesson/QuizQuestion models.",
                "checkpoint": "User accepts, updates, or deletes the blueprint before lesson writing starts.",
            },
            "lesson_generation": {
                "goal": "Generate lesson content and email bodies in the target language only, with no mixed-language output.",
                "checkpoint": "User accepts, updates, or deletes the lesson batch before quiz generation starts.",
            },
            "quiz_generation": {
                "goal": "Generate application-first quiz questions aligned to lesson intent and Amanoba quiz rules.",
                "checkpoint": "User accepts, updates, or deletes the quiz batch before QC handoff.",
            },
            "qc_review": {
                "goal": "Inject the draft into the local QC pipeline at top priority for final quality improvement.",
                "checkpoint": "User reviews QC outcome and decides whether the draft is ready for live promotion.",
            },
            "draft_to_live": {
                "goal": "Prepare the draft for final promotion into the live Amanoba data path.",
                "checkpoint": "User explicitly promotes the draft to live or keeps it in draft state.",
            },
        }
        payload = {
            "stages": self._creator_stage_template(),
            "notes": [],
            "stageArtifacts": self._creator_stage_artifacts(clean_topic, clean_language, clean_research),
            "stageContracts": self._creator_stage_contracts(),
            "retryPolicy": self._creator_stage_retry_policy(),
            "stageAttempts": {},
            "draftSummary": {
                "courseTitleCandidate": clean_topic,
                "targetLanguage": clean_language,
                "researchMode": clean_research,
                "operatingModel": "Local amanoba_courses sovereign workflow with human checkpoints before QC and before live promotion.",
                "compatibilityContract": "docs/reference/sovereign-course-creator-compatibility-contract.md",
                "nextCheckpoint": "Research brief approval",
            },
            "stageBlueprint": stage_blueprint,
        }
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO creator_runs(
                    run_id, topic, target_language, research_mode, status, current_stage,
                    payload_json, created_at, updated_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    clean_topic,
                    clean_language,
                    clean_research,
                    "active",
                    "research",
                    json.dumps(payload, ensure_ascii=False),
                    now,
                    now,
                ),
            )
            self.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "topic_intake",
                    "create",
                    "Creator run opened from the local control center.",
                    json.dumps({"topic": clean_topic, "targetLanguage": clean_language, "researchMode": clean_research}, ensure_ascii=False),
                    now,
                ),
            )
            self.conn.commit()
        return self.creator_run_detail(run_id) or {}

    def _load_creator_payload(self, raw: str | None) -> dict[str, Any]:
        if not raw:
            return {"stages": self._creator_stage_template(), "notes": []}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {"stages": self._creator_stage_template(), "notes": []}
        if not isinstance(payload, dict):
            return {"stages": self._creator_stage_template(), "notes": []}
        payload.setdefault("stages", self._creator_stage_template())
        payload.setdefault("notes", [])
        return payload

    def _creator_row_to_summary(self, row: sqlite3.Row) -> dict[str, Any]:
        payload = self._load_creator_payload(row["payload_json"])
        stages = list(payload.get("stages") or self._creator_stage_template())
        notes = list(payload.get("notes") or [])
        draft_summary = payload.get("draftSummary") or {}
        active_stage = str(row["current_stage"] or "")
        if not active_stage:
            active_stage = next((str(item.get("key") or "") for item in stages if item.get("status") == "active"), "")
        artifact_summaries = self._creator_artifact_summaries(dict(payload.get("stageArtifacts") or {}))
        return {
            "runId": row["run_id"],
            "topic": row["topic"],
            "targetLanguage": row["target_language"],
            "researchMode": row["research_mode"],
            "status": row["status"],
            "currentStage": row["current_stage"],
            "activeStage": active_stage,
            "stages": stages,
            "notes": notes[-50:],
            "draftSummary": draft_summary,
            "artifactSummaries": artifact_summaries,
            "payload": payload,
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }

    def list_creator_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock:
            rows = self.conn.execute(
                "SELECT * FROM creator_runs ORDER BY updated_at DESC, created_at DESC LIMIT ?",
                (max(1, int(limit)),),
            ).fetchall()
        return [self._creator_row_to_summary(row) for row in rows]

    def creator_run_detail(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self.conn.execute("SELECT * FROM creator_runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None:
                return None
            events = self.conn.execute(
                "SELECT stage_key, action, comment, payload_json, created_at FROM creator_events WHERE run_id=? ORDER BY created_at DESC, id DESC",
                (run_id,),
            ).fetchall()
        summary = self._creator_row_to_summary(row)
        summary["events"] = [
            {
                "stageKey": item["stage_key"],
                "action": item["action"],
                "comment": item["comment"],
                "payload": self._load_creator_payload(item["payload_json"]) if item["payload_json"] else None,
                "createdAt": item["created_at"],
            }
            for item in events
        ]
        return summary

    def creator_save_artifact(self, run_id: str, content: str, stage_key: str | None = None) -> dict[str, Any]:
        clean_content = content.strip()
        with self._lock:
            row = self.conn.execute("SELECT * FROM creator_runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None:
                raise ValueError("Creator run not found.")
            payload = self._load_creator_payload(row["payload_json"])
            current_stage = str(stage_key or row["current_stage"] or "").strip()
            if not current_stage:
                raise ValueError("Creator run has no active stage.")
            artifacts = dict(payload.get("stageArtifacts") or {})
            artifact = dict(artifacts.get(current_stage) or {})
            artifact["content"] = clean_content
            artifact["updatedAt"] = utc_now()
            artifacts[current_stage] = artifact
            payload["stageArtifacts"] = artifacts
            draft_summary = dict(payload.get("draftSummary") or {})
            draft_summary["nextCheckpoint"] = self._creator_next_checkpoint(
                list(payload.get("stages") or self._creator_stage_template()),
                str(row["status"] or "active"),
            )
            payload["draftSummary"] = draft_summary
            notes = list(payload.get("notes") or [])
            notes.append(
                {
                    "type": "artifact-save",
                    "stageKey": current_stage,
                    "comment": f"Saved artifact for {current_stage}.",
                    "createdAt": artifact["updatedAt"],
                }
            )
            payload["notes"] = notes[-50:]
            self.conn.execute(
                "UPDATE creator_runs SET payload_json=?, updated_at=? WHERE run_id=?",
                (json.dumps(payload, ensure_ascii=False), artifact["updatedAt"], run_id),
            )
            self.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (run_id, current_stage, "save-artifact", "Artifact updated in local creator workspace.", json.dumps(payload, ensure_ascii=False), artifact["updatedAt"]),
            )
            self.conn.commit()
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found after save.")
        return detail

    def creator_action(self, run_id: str, action: str, comment: str = "") -> dict[str, Any]:
        clean_action = action.strip().lower()
        clean_comment = comment.strip()
        if clean_action not in {"accept", "update", "delete"}:
            raise ValueError("Unsupported creator action.")
        with self._lock:
            row = self.conn.execute("SELECT * FROM creator_runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None:
                raise ValueError("Creator run not found.")
            payload = self._load_creator_payload(row["payload_json"])
            stages = list(payload.get("stages") or self._creator_stage_template())
            current_stage = str(row["current_stage"] or "")
            stage_index = next((idx for idx, item in enumerate(stages) if item.get("key") == current_stage), None)
            if stage_index is None:
                stage_index = 0
                current_stage = str(stages[0].get("key") or "topic_intake")
            next_status = str(row["status"] or "active")
            next_stage = current_stage
            now = utc_now()
            if clean_action == "delete":
                next_status = "deleted"
                for item in stages:
                    if item.get("status") == "active":
                        item["status"] = "cancelled"
            elif clean_action == "update":
                stages[stage_index]["status"] = "needs-update"
                notes = list(payload.get("notes") or [])
                if clean_comment:
                    notes.append({"type": "human-update", "stageKey": current_stage, "comment": clean_comment, "createdAt": now})
                payload["notes"] = notes[-50:]
            elif clean_action == "accept":
                stages[stage_index]["status"] = "completed"
                next_index = stage_index + 1
                if next_index >= len(stages):
                    next_status = "completed"
                    next_stage = ""
                else:
                    stages[next_index]["status"] = "active"
                    next_stage = str(stages[next_index].get("key") or current_stage)
                notes = list(payload.get("notes") or [])
                if clean_comment:
                    notes.append({"type": "human-accept", "stageKey": current_stage, "comment": clean_comment, "createdAt": now})
                payload["notes"] = notes[-50:]
            draft_summary = dict(payload.get("draftSummary") or {})
            draft_summary["nextCheckpoint"] = self._creator_next_checkpoint(stages, next_status)
            payload["draftSummary"] = draft_summary
            self.conn.execute(
                """
                UPDATE creator_runs
                SET status=?, current_stage=?, payload_json=?, updated_at=?
                WHERE run_id=?
                """,
                (next_status, next_stage, json.dumps(payload, ensure_ascii=False), now, run_id),
            )
            self.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (run_id, current_stage, clean_action, clean_comment or None, json.dumps(payload, ensure_ascii=False), now),
            )
            self.conn.commit()
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found after update.")
        return detail

    def _creator_stage_label(self, key: str) -> str:
        return str(key or "").replace("_", " ").title()

    def _creator_next_checkpoint(self, stages: list[dict[str, Any]], run_status: str) -> str:
        if run_status == "completed":
            return "Lifecycle complete."
        if run_status == "ready-for-live":
            return "Draft To Live approval"
        for stage in stages:
            if str(stage.get("status") or "") == "active":
                return f"{self._creator_stage_label(str(stage.get('key') or 'stage'))} approval"
        return "No open checkpoint."

    def _creator_artifact_summaries(self, stage_artifacts: dict[str, Any]) -> dict[str, dict[str, Any]]:
        summaries: dict[str, dict[str, Any]] = {}
        research_content = str((stage_artifacts.get("research") or {}).get("content") or "").strip()
        if research_content:
            bullets = len(re.findall(r"^\s*-\s+", research_content, flags=re.MULTILINE))
            summaries["research"] = {
                "headline": f"Research brief with {bullets} captured bullets.",
                "stats": [f"Bullets {bullets}"],
            }
        blueprint_content = str((stage_artifacts.get("blueprint") or {}).get("content") or "").strip()
        if blueprint_content:
            day_rows = list(
                re.finditer(
                    r"^### Day (?P<day>\d{2}) — (?P<title>.+?)\n"
                    r"- Module: (?P<module>.+?)\n"
                    r"- Goal: (?P<goal>.+?)\n"
                    r"- Deliverable: (?P<deliverable>.+?)\n"
                    r"- Quiz focus: (?P<quiz_focus>.+?)(?:\n|$)",
                    blueprint_content,
                    flags=re.MULTILINE | re.DOTALL,
                )
            )
            modules = sorted({match.group("module").strip() for match in day_rows if match.group("module").strip()})
            summaries["blueprint"] = {
                "headline": f"{len(day_rows)} day architecture across {len(modules)} modules." if day_rows else "Blueprint saved.",
                "stats": [f"Days {len(day_rows)}", f"Modules {len(modules)}"],
                "samples": [match.group("title").strip() for match in day_rows[:3] if match.group("title").strip()],
            }
        lesson_content = str((stage_artifacts.get("lesson_generation") or {}).get("content") or "").strip()
        if lesson_content:
            lesson_rows = len(re.findall(r"^### Day\s+\d{2}\s+Lesson Draft$", lesson_content, flags=re.MULTILINE))
            email_rows = len(re.findall(r"^- Email subject:", lesson_content, flags=re.MULTILINE))
            lesson_titles = re.findall(r"^- Lesson title:\s+(.+)$", lesson_content, flags=re.MULTILINE)
            summaries["lesson_generation"] = {
                "headline": f"{lesson_rows} lesson batch drafts prepared." if lesson_rows else "Lesson batch saved.",
                "stats": [f"Lesson drafts {lesson_rows}", f"Email subjects {email_rows}"],
                "samples": lesson_titles[:3],
            }
        quiz_content = str((stage_artifacts.get("quiz_generation") or {}).get("content") or "").strip()
        if quiz_content:
            quiz_days = len(re.findall(r"^### Day\s+\d{2}\s+Quiz Draft$", quiz_content, flags=re.MULTILINE))
            question_drafts = len(re.findall(r"^#### Question\s+\d+$", quiz_content, flags=re.MULTILINE))
            summaries["quiz_generation"] = {
                "headline": f"{question_drafts} quiz draft prompts across {quiz_days} days." if question_drafts else "Quiz batch saved.",
                "stats": [f"Quiz days {quiz_days}", f"Question drafts {question_drafts}"],
            }
        return summaries

    def reset_running_tasks(self) -> None:
        with self._lock:
            self.conn.execute(
                "UPDATE tasks SET status='pending', started_at=NULL, updated_at=? WHERE status='running'",
                (utc_now(),),
            )
            self.conn.commit()

    def recover_stale_running_tasks(self, max_runtime_seconds: int, max_attempts: int) -> int:
        if max_runtime_seconds <= 0:
            return 0
        with self._lock:
            rows = self.conn.execute(
                "SELECT task_key, attempts, started_at, details_json FROM tasks WHERE status='running' AND started_at IS NOT NULL"
            ).fetchall()
            now_dt = datetime.now(timezone.utc)
            recovered = 0
            for row in rows:
                started_at = str(row["started_at"] or "").strip()
                if not started_at:
                    continue
                try:
                    started_dt = datetime.fromisoformat(started_at)
                except ValueError:
                    continue
                runtime_seconds = int((now_dt - started_dt).total_seconds())
                if runtime_seconds < max_runtime_seconds:
                    continue
                attempts = int(row["attempts"] or 0) + 1
                next_status = "failed" if attempts >= max_attempts else "pending"
                details: dict[str, Any] = {}
                if row["details_json"]:
                    try:
                        details = json.loads(row["details_json"])
                    except json.JSONDecodeError:
                        details = {"raw": row["details_json"]}
                recoveries = list(details.get("recoveries") or [])
                recoveries.append(
                    {
                        "type": "stale-running-timeout",
                        "runtimeSeconds": runtime_seconds,
                        "recoveredAt": utc_now(),
                    }
                )
                details["recoveries"] = recoveries[-20:]
                now = utc_now()
                self.conn.execute(
                    """
                    UPDATE tasks
                    SET status=?,
                        attempts=?,
                        last_error=?,
                        details_json=?,
                        started_at=NULL,
                        finished_at=?,
                        updated_at=?
                    WHERE task_key=?
                    """,
                    (
                        next_status,
                        attempts,
                        f"Recovered stale running task after {runtime_seconds} seconds.",
                        json.dumps(details, ensure_ascii=False),
                        now if next_status == "failed" else None,
                        now,
                        row["task_key"],
                    ),
                )
                recovered += 1
            self.conn.commit()
            return recovered

    def archive_non_english_tasks(self, allowed_language: str = "en") -> int:
        with self._lock:
            rows = self.conn.execute(
                "SELECT task_key, details_json FROM tasks WHERE lower(coalesce(language, '')) != ? AND status IN ('pending', 'running')",
                (allowed_language.lower(),),
            ).fetchall()
            if not rows:
                return 0
            now = utc_now()
            archived = 0
            for row in rows:
                details: dict[str, Any] = {}
                if row["details_json"]:
                    try:
                        loaded = json.loads(row["details_json"])
                        if isinstance(loaded, dict):
                            details = loaded
                    except json.JSONDecodeError:
                        details = {"raw": row["details_json"]}
                details["archivedByPolicy"] = {
                    "reason": f"English-only QC mode; skipped because language != {allowed_language}",
                    "archivedAt": now,
                }
                self.conn.execute(
                    """
                    UPDATE tasks
                    SET status='archived',
                        details_json=?,
                        last_error=?,
                        started_at=NULL,
                        finished_at=?,
                        updated_at=?
                    WHERE task_key=?
                    """,
                    (
                        json.dumps(details, ensure_ascii=False),
                        f"Archived by English-only QC mode: language != {allowed_language}",
                        now,
                        now,
                        row["task_key"],
                    ),
                )
                archived += 1
            self.conn.commit()
            return archived

    def save_package(self, path: str, fingerprint: str, course_id: str, language: str) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO packages(path, fingerprint, course_id, language, updated_at)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    fingerprint=excluded.fingerprint,
                    course_id=excluded.course_id,
                    language=excluded.language,
                    updated_at=excluded.updated_at
                """,
                (path, fingerprint, course_id, language, utc_now()),
            )
            self.conn.commit()

    def upsert_task(
        self,
        task_key: str,
        kind: str,
        package_path: str,
        course_id: str,
        language: str,
        lesson_id: str,
        question_uuid: str | None,
        question_index: int | None,
        source_hash: str,
        details: dict[str, Any],
        priority: int = 0,
    ) -> None:
        with self._lock:
            existing = self.conn.execute(
                "SELECT source_hash, status, created_at, attempts, started_at, finished_at, last_error, updated_at, details_json, priority FROM tasks WHERE task_key=?",
                (task_key,),
            ).fetchone()
            created_at = existing["created_at"] if existing and existing["created_at"] else utc_now()
            unchanged = bool(existing and existing["source_hash"] == source_hash)
            existing_details: dict[str, Any] = {}
            if existing and existing["details_json"]:
                try:
                    loaded = json.loads(existing["details_json"])
                    if isinstance(loaded, dict):
                        existing_details = loaded
                except json.JSONDecodeError:
                    existing_details = {}
            if unchanged and existing["status"] in {"completed", "failed", "running", "pending", "quarantined", "archived"}:
                next_status = str(existing["status"])
            elif existing and existing["status"] == "running":
                next_status = "running"
            else:
                next_status = "pending"
            attempts = int(existing["attempts"]) if existing and unchanged else 0
            started_at = existing["started_at"] if existing and next_status == "running" else None
            finished_at = existing["finished_at"] if existing and next_status in {"completed", "failed", "quarantined", "archived"} else None
            last_error = existing["last_error"] if existing and unchanged and existing["last_error"] else None
            updated_at = existing["updated_at"] if existing and unchanged and existing["updated_at"] else utc_now()
            task_priority = int(existing["priority"]) if existing and unchanged else int(priority)
            merged_details = dict(details)
            if unchanged and existing_details:
                merged_details.update(existing_details)
            self.conn.execute(
                """
                INSERT INTO tasks(
                    task_key, kind, package_path, course_id, language, lesson_id, question_uuid,
                    question_index, source_hash, status, attempts, last_error, details_json,
                    priority, created_at, started_at, finished_at, updated_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_key) DO UPDATE SET
                    package_path=excluded.package_path,
                    course_id=excluded.course_id,
                    language=excluded.language,
                    lesson_id=excluded.lesson_id,
                    question_uuid=excluded.question_uuid,
                    question_index=excluded.question_index,
                    source_hash=excluded.source_hash,
                    status=CASE
                        WHEN tasks.source_hash = excluded.source_hash AND tasks.status IN ('completed', 'failed', 'running', 'pending', 'quarantined', 'archived') THEN tasks.status
                        WHEN tasks.status = 'running' THEN 'running'
                        ELSE 'pending'
                    END,
                    attempts=CASE
                        WHEN tasks.source_hash = excluded.source_hash THEN tasks.attempts
                        WHEN tasks.status = 'running' THEN tasks.attempts
                        ELSE 0
                    END,
                    last_error=CASE
                        WHEN tasks.source_hash = excluded.source_hash THEN tasks.last_error
                        ELSE NULL
                    END,
                    details_json=excluded.details_json,
                    priority=excluded.priority,
                    created_at=COALESCE(tasks.created_at, excluded.created_at),
                    started_at=CASE
                        WHEN tasks.source_hash = excluded.source_hash AND tasks.status = 'running' THEN tasks.started_at
                        WHEN tasks.status = 'running' THEN tasks.started_at
                        ELSE NULL
                    END,
                    finished_at=CASE
                        WHEN tasks.source_hash = excluded.source_hash AND tasks.status IN ('completed', 'failed', 'quarantined', 'archived') THEN tasks.finished_at
                        ELSE NULL
                    END,
                    updated_at=CASE
                        WHEN tasks.source_hash = excluded.source_hash THEN tasks.updated_at
                        ELSE excluded.updated_at
                    END
                """,
                (
                    task_key,
                    kind,
                    package_path,
                    course_id,
                    language,
                    lesson_id,
                    question_uuid,
                    question_index,
                    source_hash,
                    next_status,
                    attempts,
                    last_error,
                    json.dumps(merged_details, ensure_ascii=False),
                    task_priority,
                    created_at,
                    started_at,
                    finished_at,
                    updated_at,
                ),
            )
            self.conn.commit()

    def claim_next_task(self, max_attempts: int) -> sqlite3.Row | None:
        with self._lock:
            now = utc_now()
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                running = self.conn.execute("SELECT 1 FROM tasks WHERE status='running' LIMIT 1").fetchone()
                if running is not None:
                    self.conn.commit()
                    return None
                task = self.conn.execute(
                    "SELECT task_key FROM tasks WHERE status='pending' AND attempts < ? AND lower(coalesce(language, ''))='en' ORDER BY priority DESC, attempts ASC, updated_at ASC, created_at ASC LIMIT 1",
                    (max_attempts,),
                ).fetchone()
                if task is None:
                    self.conn.commit()
                    return None
                cursor = self.conn.execute(
                    "UPDATE tasks SET status='running', started_at=?, updated_at=? WHERE task_key=? AND status='pending'",
                    (now, now, task["task_key"]),
                )
                if cursor.rowcount <= 0:
                    self.conn.commit()
                    return None
                row = self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task["task_key"],)).fetchone()
                self.conn.commit()
                return row
            except Exception:
                self.conn.rollback()
                raise

    def mark_running(self, task_key: str) -> sqlite3.Row | None:
        with self._lock:
            now = utc_now()
            self.conn.execute(
                "UPDATE tasks SET status='running', started_at=?, updated_at=? WHERE task_key=?",
                (now, now, task_key),
            )
            self.conn.commit()
            return self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task_key,)).fetchone()

    def ensure_running(self, task_key: str) -> sqlite3.Row | None:
        with self._lock:
            now = utc_now()
            row = self.conn.execute(
                "SELECT status, started_at, finished_at FROM tasks WHERE task_key=?",
                (task_key,),
            ).fetchone()
            if row is None:
                return None
            status = str(row["status"] or "").strip().lower()
            if status in {"completed", "failed", "quarantined", "archived"}:
                return self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            if status != "running" or not str(row["started_at"] or "").strip():
                self.conn.execute(
                    "UPDATE tasks SET status='running', started_at=COALESCE(started_at, ?), updated_at=? WHERE task_key=?",
                    (now, now, task_key),
                )
                self.conn.commit()
            return self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task_key,)).fetchone()

    def mark_completed(self, task_key: str, details: dict[str, Any]) -> None:
        with self._lock:
            now = utc_now()
            self.conn.execute(
                "UPDATE tasks SET status='completed', details_json=?, finished_at=?, last_error=NULL, updated_at=? WHERE task_key=?",
                (json.dumps(details, ensure_ascii=False), now, now, task_key),
            )
            self.conn.commit()

    def defer_task(self, task_key: str, details: dict[str, Any] | None = None) -> None:
        with self._lock:
            now = utc_now()
            existing = self.conn.execute("SELECT details_json FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            merged_details: dict[str, Any] = {}
            if existing and existing["details_json"]:
                try:
                    loaded = json.loads(existing["details_json"])
                    if isinstance(loaded, dict):
                        merged_details = loaded
                except json.JSONDecodeError:
                    merged_details = {}
            if isinstance(details, dict):
                merged_details.update(details)
            self.conn.execute(
                "UPDATE tasks SET status='pending', started_at=NULL, updated_at=?, details_json=? WHERE task_key=?",
                (now, json.dumps(merged_details, ensure_ascii=False), task_key),
            )
            self.conn.commit()

    def mark_failed(self, task_key: str, attempts: int, max_attempts: int, error: str, details: dict[str, Any]) -> None:
        with self._lock:
            now = utc_now()
            status = "failed" if attempts >= max_attempts else "pending"
            existing = self.conn.execute("SELECT details_json FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            merged_details: dict[str, Any] = {}
            if existing and existing["details_json"]:
                try:
                    loaded = json.loads(existing["details_json"])
                    if isinstance(loaded, dict):
                        merged_details.update(loaded)
                except json.JSONDecodeError:
                    pass
            merged_details.update(details)
            self.conn.execute(
                "UPDATE tasks SET status=?, attempts=?, last_error=?, details_json=?, started_at=NULL, finished_at=?, updated_at=? WHERE task_key=?",
                (status, attempts, error, json.dumps(merged_details, ensure_ascii=False), now if status == "failed" else None, now, task_key),
            )
            self.conn.commit()

    def mark_failed_with_policy(
        self,
        task_key: str,
        attempts: int,
        max_attempts: int,
        error: str,
        details: dict[str, Any],
        quarantine_after_failures: int,
        suppress_quarantine: bool = False,
    ) -> str:
        with self._lock:
            now = utc_now()
            if attempts >= max_attempts:
                status = "failed"
            elif (not suppress_quarantine) and quarantine_after_failures > 0 and attempts >= quarantine_after_failures:
                status = "quarantined"
            else:
                status = "pending"
            existing = self.conn.execute("SELECT details_json FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            merged_details: dict[str, Any] = {}
            if existing and existing["details_json"]:
                try:
                    loaded = json.loads(existing["details_json"])
                    if isinstance(loaded, dict):
                        merged_details.update(loaded)
                except json.JSONDecodeError:
                    pass
            merged_details.update(details)
            if status == "quarantined":
                merged_details["humanActionRequired"] = True
                merged_details["quarantine"] = {
                    "status": "active",
                    "reason": error,
                    "quarantinedAt": now,
                    "attempts": attempts,
                }
            self.conn.execute(
                "UPDATE tasks SET status=?, attempts=?, last_error=?, details_json=?, started_at=NULL, finished_at=?, updated_at=? WHERE task_key=?",
                (status, attempts, error, json.dumps(merged_details, ensure_ascii=False), now if status in {"failed", "quarantined"} else None, now, task_key),
            )
            self.conn.commit()
            return status

    def clear_pending_tasks(self, package_path: str | None = None) -> int:
        with self._lock:
            if package_path:
                cursor = self.conn.execute(
                    """
                    DELETE FROM tasks
                    WHERE status='pending'
                      AND package_path=?
                      AND COALESCE(attempts, 0) = 0
                      AND last_error IS NULL
                    """,
                    (package_path,),
                )
            else:
                cursor = self.conn.execute(
                    """
                    DELETE FROM tasks
                    WHERE status='pending'
                      AND COALESCE(attempts, 0) = 0
                      AND last_error IS NULL
                    """
                )
            self.conn.commit()
            return int(cursor.rowcount or 0)

    def counts(self) -> dict[str, int]:
        with self._lock:
            rows = self.conn.execute(
                "SELECT status, COUNT(*) AS count FROM tasks WHERE lower(coalesce(language, ''))='en' GROUP BY status"
            ).fetchall()
            return {row["status"]: int(row["count"]) for row in rows}

    def feed_snapshot(self, limit: int) -> dict[str, Any]:
        completed_count = self.count_by_status("completed", language="en")
        failed_rows = self._query_failed_column_rows(FAILED_COLUMN_LIMIT, language="en")
        quarantined_rows = self._query_tasks("quarantined", "updated_at DESC", QUARANTINED_COLUMN_LIMIT, language="en")
        return {
            "generatedAt": utc_now(),
            "counts": self.counts(),
            "queued": [self._row_to_summary(row) for row in self._query_tasks("pending", "updated_at ASC", limit, language="en")],
            "running": [self._row_to_summary(row) for row in self._query_tasks("running", "started_at ASC", limit, language="en")],
            "completed": [self._row_to_summary(row) for row in self._query_tasks("completed", "finished_at DESC", DONE_COLUMN_LIMIT, language="en")],
            "failed": [self._row_to_summary(row) for row in failed_rows],
            "failedCount": len(failed_rows),
            "quarantined": [self._row_to_summary(row) for row in quarantined_rows],
            "quarantinedCount": len(quarantined_rows),
            "archived": [self._row_to_summary(row) for row in self._query_tasks_offset("completed", "finished_at DESC", ARCHIVED_COLUMN_LIMIT, DONE_COLUMN_LIMIT, language="en")],
            "archivedCount": max(0, completed_count - DONE_COLUMN_LIMIT),
        }

    def count_by_status(self, status: str, language: str | None = None) -> int:
        with self._lock:
            if language is None:
                row = self.conn.execute("SELECT COUNT(*) AS count FROM tasks WHERE status=?", (status,)).fetchone()
            else:
                row = self.conn.execute(
                    "SELECT COUNT(*) AS count FROM tasks WHERE status=? AND lower(coalesce(language, ''))=?",
                    (status, language.lower()),
                ).fetchone()
            return int(row["count"]) if row else 0

    def _query_tasks(self, status: str, order_by: str, limit: int, language: str | None = None) -> list[sqlite3.Row]:
        if language is None:
            query = f"SELECT * FROM tasks WHERE status=? ORDER BY {order_by} LIMIT ?"
            params: tuple[Any, ...] = (status, limit)
        else:
            query = f"SELECT * FROM tasks WHERE status=? AND lower(coalesce(language, ''))=? ORDER BY {order_by} LIMIT ?"
            params = (status, language.lower(), limit)
        with self._lock:
            return self.conn.execute(query, params).fetchall()

    def _query_failed_column_rows(self, limit: int, language: str | None = None) -> list[sqlite3.Row]:
        with self._lock:
            if language is None:
                return self.conn.execute(
                """
                SELECT *
                FROM tasks
                WHERE status='failed'
                   OR (status='pending' AND last_error IS NOT NULL AND last_error NOT LIKE 'Reopened:%')
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return self.conn.execute(
                """
                SELECT *
                FROM tasks
                WHERE lower(coalesce(language, ''))=?
                  AND (
                       status='failed'
                   OR (status='pending' AND last_error IS NOT NULL AND last_error NOT LIKE 'Reopened:%')
                  )
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (language.lower(), limit),
            ).fetchall()

    def _query_tasks_offset(self, status: str, order_by: str, limit: int, offset: int, language: str | None = None) -> list[sqlite3.Row]:
        if language is None:
            query = f"SELECT * FROM tasks WHERE status=? ORDER BY {order_by} LIMIT ? OFFSET ?"
            params: tuple[Any, ...] = (status, limit, offset)
        else:
            query = f"SELECT * FROM tasks WHERE status=? AND lower(coalesce(language, ''))=? ORDER BY {order_by} LIMIT ? OFFSET ?"
            params = (status, language.lower(), limit, offset)
        with self._lock:
            return self.conn.execute(query, params).fetchall()

    def _row_to_summary(self, row: sqlite3.Row) -> dict[str, Any]:
        details: dict[str, Any] = {}
        if row["details_json"]:
            try:
                details = json.loads(row["details_json"])
            except json.JSONDecodeError:
                details = {"raw": row["details_json"]}
        return {
            "taskKey": row["task_key"],
            "kind": row["kind"],
            "courseId": row["course_id"],
            "language": row["language"],
            "lessonId": row["lesson_id"],
            "questionUuid": row["question_uuid"],
            "questionIndex": row["question_index"],
            "packagePath": row["package_path"],
            "status": row["status"],
            "displayStatus": (
                "rewriting"
                if row["status"] == "pending" and str(row["last_error"] or "").startswith("Reopened:")
                else (
                    "retry-failed"
                if row["status"] == "pending" and row["last_error"]
                else ("quarantined" if row["status"] == "quarantined" else row["status"])
                )
            ),
            "attempts": row["attempts"],
            "lastError": row["last_error"],
            "createdAt": row["created_at"],
            "startedAt": row["started_at"],
            "finishedAt": row["finished_at"],
            "updatedAt": row["updated_at"],
            "priority": int(row["priority"] or 0),
            "details": details,
        }

    def task_summaries_by_keys(self, task_keys: list[str]) -> list[dict[str, Any]]:
        if not task_keys:
            return []
        placeholders = ", ".join("?" for _ in task_keys)
        with self._lock:
            rows = self.conn.execute(
                f"SELECT * FROM tasks WHERE task_key IN ({placeholders})",
                tuple(task_keys),
            ).fetchall()
        order = {task_key: index for index, task_key in enumerate(task_keys)}
        summaries = [self._row_to_summary(row) for row in rows]
        summaries.sort(key=lambda item: order.get(str(item.get('taskKey') or ''), len(order)))
        return summaries

    def task_detail(self, task_key: str) -> dict[str, Any] | None:
        with self._lock:
            row = self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            if row is None:
                return None
            feedback_rows = self.conn.execute(
                "SELECT comment, created_at FROM task_feedback WHERE task_key=? ORDER BY created_at DESC",
                (task_key,),
            ).fetchall()
        summary = self._row_to_summary(row)
        summary["feedback"] = [{"comment": item["comment"], "createdAt": item["created_at"]} for item in feedback_rows]
        return summary

    def feedback_comments(self, task_key: str) -> list[str]:
        with self._lock:
            rows = self.conn.execute(
                "SELECT comment FROM task_feedback WHERE task_key=? ORDER BY created_at ASC",
                (task_key,),
            ).fetchall()
        return [str(row["comment"]) for row in rows]

    def related_lesson_task(self, package_path: str, course_id: str, lesson_id: str) -> sqlite3.Row | None:
        with self._lock:
            return self.conn.execute(
                """
                SELECT *
                FROM tasks
                WHERE package_path=?
                  AND course_id=?
                  AND lesson_id=?
                  AND kind IN ('lesson', 'creator_lesson')
                ORDER BY updated_at DESC, created_at DESC
                LIMIT 1
                """,
                (package_path, course_id, lesson_id),
            ).fetchone()

    def add_feedback_comment(self, task_key: str, comment: str) -> None:
        clean = comment.strip()
        if not clean:
            return
        with self._lock:
            self.conn.execute(
                "INSERT INTO task_feedback(task_key, comment, created_at) VALUES(?, ?, ?)",
                (task_key, clean, utc_now()),
            )
            self.conn.commit()

    def quarantine_repeated_failures(self, threshold: int) -> list[str]:
        if threshold <= 0:
            return []
        with self._lock:
            rows = self.conn.execute(
                """
                SELECT task_key, attempts, last_error, details_json
                FROM tasks
                WHERE status='pending'
                  AND last_error IS NOT NULL
                  AND attempts >= ?
                """,
                (threshold,),
            ).fetchall()
            now = utc_now()
            updated: list[str] = []
            for row in rows:
                details: dict[str, Any] = {}
                if row["details_json"]:
                    try:
                        loaded = json.loads(row["details_json"])
                        if isinstance(loaded, dict):
                            details = loaded
                    except json.JSONDecodeError:
                        details = {}
                details["humanActionRequired"] = True
                details["quarantine"] = {
                    "status": "active",
                    "reason": str(row["last_error"] or ""),
                    "quarantinedAt": now,
                    "attempts": int(row["attempts"] or 0),
                }
                self.conn.execute(
                    """
                    UPDATE tasks
                    SET status='quarantined',
                        details_json=?,
                        finished_at=COALESCE(finished_at, ?),
                        updated_at=?
                    WHERE task_key=?
                    """,
                    (json.dumps(details, ensure_ascii=False), now, now, row["task_key"]),
                )
                updated.append(str(row["task_key"]))
            self.conn.commit()
            return updated

    def quarantine_legacy_timeout_failures(self) -> list[str]:
        with self._lock:
            rows = self.conn.execute(
                """
                SELECT task_key, attempts, last_error, details_json
                FROM tasks
                WHERE status='pending'
                  AND attempts >= 1
                  AND last_error IS NOT NULL
                  AND lower(last_error) LIKE '%timeout%'
                """
            ).fetchall()
            now = utc_now()
            updated: list[str] = []
            for row in rows:
                details: dict[str, Any] = {}
                if row["details_json"]:
                    try:
                        loaded = json.loads(row["details_json"])
                        if isinstance(loaded, dict):
                            details = loaded
                    except json.JSONDecodeError:
                        details = {}
                details["humanActionRequired"] = True
                details["quarantine"] = {
                    "status": "active",
                    "reason": str(row["last_error"] or ""),
                    "quarantinedAt": now,
                    "attempts": int(row["attempts"] or 0),
                }
                self.conn.execute(
                    """
                    UPDATE tasks
                    SET status='quarantined',
                        details_json=?,
                        finished_at=COALESCE(finished_at, ?),
                        updated_at=?
                    WHERE task_key=?
                    """,
                    (json.dumps(details, ensure_ascii=False), now, now, row["task_key"]),
                )
                updated.append(str(row["task_key"]))
            self.conn.commit()
            return updated

    def search_completed(self, query: str, limit: int = ARCHIVED_COLUMN_LIMIT) -> list[dict[str, Any]]:
        q = f"%{query.strip()}%"
        with self._lock:
            rows = self.conn.execute(
                """
                SELECT * FROM tasks
                WHERE status='completed'
                  AND (
                    task_key LIKE ?
                    OR course_id LIKE ?
                    OR language LIKE ?
                    OR lesson_id LIKE ?
                    OR question_uuid LIKE ?
                    OR package_path LIKE ?
                    OR details_json LIKE ?
                  )
                ORDER BY finished_at DESC
                LIMIT ?
                """,
                (q, q, q, q, q, q, q, limit),
            ).fetchall()
        return [self._row_to_summary(row) for row in rows]

    def challenge_task(self, task_key: str, comment: str) -> dict[str, Any] | None:
        clean = comment.strip()
        if not clean:
            raise ValueError("Challenge comment is required.")
        with self._lock:
            row = self.conn.execute("SELECT * FROM tasks WHERE task_key=?", (task_key,)).fetchone()
            if row is None:
                return None
            now = utc_now()
            self.conn.execute(
                "INSERT INTO task_feedback(task_key, comment, created_at) VALUES(?, ?, ?)",
                (task_key, clean, now),
            )
            details = {}
            if row["details_json"]:
                try:
                    details = json.loads(row["details_json"])
                except json.JSONDecodeError:
                    details = {"raw": row["details_json"]}
            history = list(details.get("challengeHistory") or [])
            history.append({"comment": clean, "createdAt": now})
            details["challengeHistory"] = history[-20:]
            self.conn.execute(
                """
                UPDATE tasks
                SET status='pending',
                    attempts=0,
                    last_error=?,
                    started_at=NULL,
                    finished_at=NULL,
                    details_json=?,
                    updated_at=?
                WHERE task_key=?
                """,
                (f"Reopened: {clean}", json.dumps(details, ensure_ascii=False), now, task_key),
            )
            self.conn.commit()
        return self.task_detail(task_key)


class AmanobaLiveBridge:
    def __init__(self, app_root: Path, script_path: str, actor: str, timeout_seconds: int) -> None:
        self.app_root = app_root
        self.script_path = script_path
        self.actor = actor
        self.timeout_seconds = max(1, int(timeout_seconds))

    def scan(self) -> dict[str, Any]:
        return self._run(["scan"])

    def next_batch(self, limit: int) -> dict[str, Any]:
        return self._run(["next-batch", "--limit", str(limit)])

    def fetch(self, task_key: str) -> dict[str, Any]:
        return self._run(["fetch", "--task-key", task_key])

    def apply(self, task_key: str, payload: dict[str, Any]) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temp_path = handle.name
        try:
            return self._run(["apply", "--task-key", task_key, "--payload-file", temp_path, "--actor", self.actor])
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def mark_reviewed(self, task_key: str, result: str = "valid") -> dict[str, Any]:
        return self._run(["mark-reviewed", "--task-key", task_key, "--actor", self.actor, "--result", result])

    def mark_reviewed_batch(self, task_keys: list[str], result: str = "valid") -> dict[str, Any]:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump({"taskKeys": list(task_keys)}, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temp_path = handle.name
        try:
            return self._run(["mark-reviewed-batch", "--payload-file", temp_path, "--actor", self.actor, "--result", result])
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def stats(self) -> dict[str, Any]:
        return self._run(["stats"])

    def import_package(self, package_payload: dict[str, Any]) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
            json.dump(package_payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temp_path = handle.name
        try:
            return self._run(["import-package", "--payload-file", temp_path, "--actor", self.actor])
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def publish_course(self, course_id: str) -> dict[str, Any]:
        return self._run(["publish-course", "--course-id", course_id, "--actor", self.actor])

    def rollback_publish(self, course_id: str) -> dict[str, Any]:
        return self._run(["rollback-publish", "--course-id", course_id, "--actor", self.actor])

    def delete_imported_course(self, course_id: str) -> dict[str, Any]:
        return self._run(["delete-imported-course", "--course-id", course_id, "--actor", self.actor])

    def _run(self, args: list[str]) -> dict[str, Any]:
        tsx_path = self.app_root / "node_modules" / ".bin" / "tsx"
        if not tsx_path.exists():
            raise RuntimeError(f"tsx not found in app workspace: {tsx_path}")
        script = self.app_root / self.script_path
        if not script.exists():
            raise RuntimeError(f"Live bridge script not found: {script}")
        try:
            result = subprocess.run(
                [str(tsx_path), "--env-file=.env.local", str(script), *args],
                cwd=str(self.app_root),
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Live bridge command timed out after {self.timeout_seconds} seconds: {' '.join(args)}"
            ) from exc
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            detail = stderr or stdout or f"exit code {result.returncode}"
            raise RuntimeError(f"Live bridge command failed: {detail}")
        output = (result.stdout or "").strip()
        if not output:
            return {}
        return json.loads(output)


class CourseQualityDaemon:
    def __init__(self, config: Config, *, manage_worker_heartbeat: bool = False) -> None:
        self.config = config
        self.manage_worker_heartbeat = bool(manage_worker_heartbeat)
        self.state = StateStore(config.state_db_path)
        self.runtime = LocalRuntimeManager(config.runtime_config)
        self.live_bridge = (
            AmanobaLiveBridge(
                config.live_app_root,
                config.live_bridge_script or "scripts/course-quality-live-bridge.ts",
                config.live_actor,
                config.live_bridge_timeout_seconds,
            )
            if config.source_mode == "amanoba_live_db" and config.live_app_root is not None
            else None
        )
        self._process_lock = threading.Lock()
        self.runtime_dir = config.state_db_path.parent
        self.heartbeat_path = self.runtime_dir / "worker-heartbeat.json"
        self._heartbeat_lock = threading.Lock()
        self._heartbeat_stop: threading.Event | None = None
        self._heartbeat_thread: threading.Thread | None = None
        now = utc_now()
        self._heartbeat_state: dict[str, Any] = {
            "pid": os.getpid(),
            "phase": "idle",
            "taskKey": None,
            "message": "Worker initialized.",
            "heartbeatAt": now,
            "progressAt": now,
            "startedAt": now,
            "taskStartedAt": None,
        }
        self.config.backups_dir.mkdir(parents=True, exist_ok=True)
        self.config.reports_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        if self.manage_worker_heartbeat:
            self._write_heartbeat_file()

    def _creator_stage_template(self) -> list[dict[str, str]]:
        return self.state._creator_stage_template()

    def _creator_stage_artifacts(self, topic: str, target_language: str, research_mode: str) -> dict[str, dict[str, Any]]:
        return self.state._creator_stage_artifacts(topic, target_language, research_mode)

    def _creator_stage_contracts(self) -> dict[str, dict[str, Any]]:
        return self.state._creator_stage_contracts()

    def _creator_stage_retry_policy(self) -> dict[str, Any]:
        return self.state._creator_stage_retry_policy()

    def _write_json_atomic(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f"{path.suffix}.{os.getpid()}.{threading.get_ident()}.tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(path)

    def _write_heartbeat_file(self) -> None:
        if not self.manage_worker_heartbeat:
            return
        with self._heartbeat_lock:
            payload = dict(self._heartbeat_state)
            payload["heartbeatAt"] = utc_now()
            self._heartbeat_state["heartbeatAt"] = payload["heartbeatAt"]
        self._write_json_atomic(self.heartbeat_path, payload)

    def _set_heartbeat(
        self,
        phase: str,
        *,
        task_key: str | None = None,
        message: str | None = None,
        advance_progress: bool = False,
        extra: dict[str, Any] | None = None,
    ) -> None:
        now = utc_now()
        with self._heartbeat_lock:
            self._heartbeat_state["pid"] = os.getpid()
            self._heartbeat_state["phase"] = str(phase or "idle")
            self._heartbeat_state["taskKey"] = task_key
            self._heartbeat_state["message"] = str(message or self._heartbeat_state.get("message") or "")
            self._heartbeat_state["heartbeatAt"] = now
            if advance_progress:
                self._heartbeat_state["progressAt"] = now
            if task_key:
                if advance_progress or not self._heartbeat_state.get("taskStartedAt"):
                    self._heartbeat_state["taskStartedAt"] = now
            else:
                self._heartbeat_state["taskStartedAt"] = None
        if extra:
            self._heartbeat_state.update(extra)
        self._write_heartbeat_file()

    def _task_checkpoint(self, task_key: str | None, message: str) -> None:
        if task_key:
            try:
                self.state.ensure_running(task_key)
            except Exception:
                pass
        self._set_heartbeat(
            "processing",
            task_key=task_key,
            message=message,
            advance_progress=True,
        )

    def _start_task_progress_pulse(self, task_key: str | None, message: str, interval_seconds: int = 20) -> tuple[threading.Event, threading.Thread] | None:
        if not task_key:
            return None
        stop = threading.Event()

        def _loop() -> None:
            while not stop.wait(max(5, int(interval_seconds))):
                try:
                    self._task_checkpoint(task_key, message)
                except Exception:
                    continue

        thread = threading.Thread(target=_loop, name=f"course-quality-pulse-{task_key}", daemon=True)
        thread.start()
        return stop, thread

    def _stop_task_progress_pulse(self, pulse: tuple[threading.Event, threading.Thread] | None) -> None:
        if not pulse:
            return
        stop, thread = pulse
        stop.set()
        if thread.is_alive():
            thread.join(timeout=1)

    def _clear_heartbeat_task(self, phase: str, message: str) -> None:
        self._set_heartbeat(phase, task_key=None, message=message, advance_progress=True)

    def _start_heartbeat_loop(self) -> None:
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return
        self._heartbeat_stop = threading.Event()

        def _loop() -> None:
            while self._heartbeat_stop and not self._heartbeat_stop.wait(5):
                try:
                    self._write_heartbeat_file()
                except Exception:
                    continue

        self._heartbeat_thread = threading.Thread(target=_loop, name="course-quality-heartbeat", daemon=True)
        self._heartbeat_thread.start()

    def _stop_heartbeat_loop(self) -> None:
        if self._heartbeat_stop is not None:
            self._heartbeat_stop.set()
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=1)
        self._heartbeat_thread = None
        self._heartbeat_stop = None

    def worker_status_snapshot(self) -> dict[str, Any]:
        if self.heartbeat_path.exists():
            try:
                payload = json.loads(self.heartbeat_path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    return payload
            except json.JSONDecodeError:
                pass
        with self._heartbeat_lock:
            return dict(self._heartbeat_state)

    def _worker_state_snapshot(self) -> dict[str, Any]:
        worker = self.worker_status_snapshot()
        phase = str(worker.get("phase") or "").strip().lower() or "idle"
        task_key = str(worker.get("taskKey") or "").strip() or None
        heartbeat_at = str(worker.get("heartbeatAt") or "").strip()
        progress_at = str(worker.get("progressAt") or "").strip()
        state = "idle"
        stalled = False
        stalled_seconds = None
        if phase == "processing" and task_key:
            state = "working"
            if progress_at:
                try:
                    progress_dt = datetime.fromisoformat(progress_at.replace("Z", "+00:00"))
                    age = (datetime.now(timezone.utc) - progress_dt).total_seconds()
                    threshold = float(getattr(self.config, "worker_progress_timeout_seconds", 0) or 0)
                    if threshold <= 0:
                        try:
                            watchdog = json.loads(self.config.config_path.read_text(encoding="utf-8")).get("watchdog") or {}
                            threshold = float(watchdog.get("worker_progress_timeout_seconds") or 180)
                        except Exception:
                            threshold = 180.0
                    if age >= threshold:
                        stalled = True
                        state = "stalled"
                        stalled_seconds = int(age)
                except Exception:
                    pass
        return {
            "state": state,
            "stalled": stalled,
            "stalledSeconds": stalled_seconds,
            "phase": phase,
            "taskKey": task_key,
            "heartbeatAt": heartbeat_at,
            "progressAt": progress_at,
        }

    def _recover_orphan_running_tasks(self, *, reason: str) -> int:
        worker = self.worker_status_snapshot()
        phase = str(worker.get("phase") or "").strip().lower()
        active_task = str(worker.get("taskKey") or "").strip()
        progress_at = str(worker.get("progressAt") or "").strip()
        stalled_seconds = None
        if progress_at:
            try:
                progress_dt = datetime.fromisoformat(progress_at.replace("Z", "+00:00"))
                stalled_seconds = int((datetime.now(timezone.utc) - progress_dt).total_seconds())
            except Exception:
                stalled_seconds = None
        threshold = float(getattr(self.config, "worker_progress_timeout_seconds", 0) or 0)
        if threshold <= 0:
            try:
                watchdog = json.loads(self.config.config_path.read_text(encoding="utf-8")).get("watchdog") or {}
                threshold = float(watchdog.get("worker_progress_timeout_seconds") or 180)
            except Exception:
                threshold = 180.0
        if phase == "processing" and active_task and stalled_seconds is not None and stalled_seconds < threshold:
            return 0
        running = self.state.count_by_status("running")
        if running <= 0:
            return 0
        self.state.reset_running_tasks()
        return running

    def scan(self) -> dict[str, int]:
        self._set_heartbeat("scanning", message="Refreshing QC queue.", advance_progress=True)
        if self.config.source_mode == "amanoba_live_db":
            return self._scan_live()
        package_count = 0
        task_count = 0
        for path in self._iter_candidate_files():
            package = self._load_package(path)
            if package is None:
                continue
            self.state.clear_pending_tasks(str(path))
            package_count += 1
            task_count += self._enqueue_tasks(path, package)
        self._write_reports()
        return {"packages": package_count, "tasks": task_count}

    def _scan_live(self) -> dict[str, int]:
        if self.live_bridge is None:
            raise RuntimeError("Live DB mode is enabled but the live bridge is not configured.")
        pending_path = str(self.config.live_app_root or self.config.workspace_root)
        self.state.clear_pending_tasks(pending_path)
        payload = self.live_bridge.next_batch(self.config.live_batch_size)
        candidates = payload.get("candidates") or []
        created = 0
        reviewed_valid = 0
        valid_task_keys: list[str] = []
        for candidate in candidates:
            kind = str(candidate.get("kind") or "").strip().lower()
            if kind == "lesson":
                lesson = candidate.get("lesson") or {}
                lesson_payload = {
                    "title": lesson.get("title"),
                    "content": lesson.get("content"),
                    "emailSubject": lesson.get("emailSubject"),
                    "emailBody": lesson.get("emailBody"),
                }
                audit = audit_lesson(lesson_payload, str(lesson.get("language") or ""))
                task_key = f"lesson::{lesson['objectId']}"
                if audit.is_valid:
                    valid_task_keys.append(task_key)
                    continue
                created += 1
                human_course = str(lesson.get("courseName") or lesson.get("courseId") or "Unknown course")
                human_day = f"Day {lesson.get('dayNumber')}" if lesson.get("dayNumber") not in (None, "") else str(lesson.get("lessonId") or "-")
                self.state.upsert_task(
                    task_key=task_key,
                    kind="lesson",
                    package_path=pending_path,
                    course_id=str(lesson.get("courseId") or ""),
                    language=str(lesson.get("language") or ""),
                    lesson_id=str(lesson.get("lessonId") or ""),
                    question_uuid=None,
                    question_index=None,
                    source_hash=sha256_json({"lesson": lesson_payload}),
                    details={
                        "errors": audit.errors,
                        "warnings": audit.warnings,
                        "before": lesson_payload,
                        "displayTitle": str(lesson.get("title") or lesson.get("lessonId") or task_key),
                        "humanCourseName": human_course,
                        "humanDayLabel": human_day,
                        "humanLessonTitle": str(lesson.get("title") or lesson.get("lessonId") or "-"),
                        "judgement": confidence_for_validation("lesson", audit.errors, audit.warnings),
                    },
                )
                continue

            question = candidate.get("question") or {}
            question_payload = {
                "uuid": question.get("uuid"),
                "question": question.get("question"),
                "options": question.get("options") or [],
                "correctIndex": question.get("correctIndex"),
                "questionType": question.get("questionType"),
                "difficulty": question.get("difficulty"),
                "category": question.get("category"),
                "hashtags": question.get("hashtags") or [],
                "isActive": True,
            }
            validation = validate_question(question_payload, str(question.get("language") or ""))
            task_key = f"question::{question['objectId']}"
            if not self._lesson_ready_for_question_queue(
                package_path=pending_path,
                course_id=str(question.get("courseId") or ""),
                lesson_id=str(question.get("lessonId") or ""),
            ):
                continue
            if validation.is_valid:
                valid_task_keys.append(task_key)
                continue
            created += 1
            human_course = str(question.get("courseName") or question.get("courseId") or "Unknown course")
            human_day = f"Day {question.get('dayNumber')}" if question.get("dayNumber") not in (None, "") else str(question.get("lessonId") or "-")
            self.state.upsert_task(
                task_key=task_key,
                kind="question",
                package_path=pending_path,
                course_id=str(question.get("courseId") or ""),
                language=str(question.get("language") or ""),
                lesson_id=str(question.get("lessonId") or ""),
                question_uuid=str(question.get("uuid") or question.get("objectId") or ""),
                question_index=None,
                source_hash=sha256_json({"question": question_payload}),
                details={
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                    "before": question_payload,
                    "displayTitle": str(question.get("question") or question.get("uuid") or task_key),
                    "humanCourseName": human_course,
                    "humanDayLabel": human_day,
                    "humanLessonTitle": str(question.get("lessonTitle") or question.get("lessonId") or "-"),
                    "judgement": confidence_for_validation("question", validation.errors, validation.warnings),
                },
            )
        if valid_task_keys:
            self.live_bridge.mark_reviewed_batch(valid_task_keys, result="already-valid")
            reviewed_valid = len(valid_task_keys)
        self._write_reports()
        return {
            "packages": int((payload.get("counts") or {}).get("courses") or 0),
            "tasks": created,
            "reviewedValid": reviewed_valid,
            "batchSize": len(candidates),
        }

    def process_one(self) -> str:
        with self._process_lock:
            self._set_heartbeat("selecting", message="Selecting next QC task.", advance_progress=True)
            recovered = self._recover_orphan_running_tasks(reason="before-claim")
            if recovered:
                self._set_heartbeat("selecting", message=f"Recovered {recovered} orphan running task(s) before selection.", advance_progress=True)
            archived = self.state.archive_non_english_tasks("en")
            if archived:
                self._set_heartbeat("selecting", message=f"Archived {archived} non-English QC task(s) in English-only mode.", advance_progress=True)
            self.state.quarantine_repeated_failures(self.config.quarantine_after_failures)
            self.state.quarantine_legacy_timeout_failures()
            task = self._claim_next_eligible_task(self.config.max_attempts_per_task)
            if task is None and self.config.source_mode == "amanoba_live_db":
                for _ in range(max(1, self.config.live_batch_passes)):
                    self._set_heartbeat("scanning", message="Scanning live DB for more QC work.", advance_progress=True)
                    try:
                        scan_result = self._scan_live()
                    except Exception as exc:
                        self._set_heartbeat(
                            "waiting-dependency",
                            message=f"Live QC scan blocked: {exc}",
                            advance_progress=True,
                        )
                        self._write_reports()
                        return "blocked"
                    self.state.quarantine_repeated_failures(self.config.quarantine_after_failures)
                    self.state.quarantine_legacy_timeout_failures()
                    task = self._claim_next_eligible_task(self.config.max_attempts_per_task)
                    if task is not None:
                        break
                    if int(scan_result.get("batchSize") or 0) <= 0:
                        break
            if task is None:
                recovered = self._recover_orphan_running_tasks(reason="after-scan")
                if recovered:
                    self._set_heartbeat("selecting", message=f"Recovered {recovered} orphan running task(s) after scan.", advance_progress=True)
                    task = self._claim_next_eligible_task(self.config.max_attempts_per_task)
            if task is None:
                self._clear_heartbeat_task("idle", "No QC task available.")
                self._write_reports()
                return "idle"
            if self._question_task_waits_on_lesson(task):
                self.state.defer_task(
                    str(task["task_key"]),
                    details={
                        "waitingOnLessonQc": True,
                        "waitingOnLessonId": str(task["lesson_id"] or ""),
                    },
                )
                self._clear_heartbeat_task("idle", f"Deferred {task['task_key']} until lesson QC passes.")
                self._write_reports()
                return f"deferred:{task['task_key']}"
            self._set_heartbeat(
                "processing",
                task_key=str(task["task_key"]),
                message=f"Processing {task['task_key']}.",
                advance_progress=True,
            )
            self._write_reports()
            try:
                result = self._process_task_with_timeout(task)
                self.state.mark_completed(task["task_key"], result)
                self._clear_heartbeat_task("idle", f"Completed {task['task_key']}.")
                self._write_reports()
                return task["task_key"]
            except Exception as exc:
                attempts = int(task["attempts"]) + 1
                existing_details: dict[str, Any] = {}
                if task["details_json"]:
                    try:
                        loaded = json.loads(task["details_json"])
                        if isinstance(loaded, dict):
                            existing_details = loaded
                    except json.JSONDecodeError:
                        existing_details = {}
                partial_details = getattr(exc, "details", None)
                if isinstance(partial_details, dict):
                    existing_details.update(partial_details)
                incident = self._build_failure_incident(task, exc, attempts, existing_details)
                rca_type = str((incident.get("rca") or {}).get("type") or "").strip().lower()
                quarantine_after_failures = self.config.quarantine_after_failures
                if rca_type in {"timeout", "live-bridge-timeout"}:
                    quarantine_after_failures = 1
                next_status = self.state.mark_failed_with_policy(
                    task["task_key"],
                    attempts=attempts,
                    max_attempts=self.config.max_attempts_per_task,
                    error=str(exc),
                    quarantine_after_failures=quarantine_after_failures,
                    details=incident,
                    suppress_quarantine=rca_type == "repairable-content",
                )
                self._record_system_feedback(task["task_key"], incident, next_status)
                self._clear_heartbeat_task("idle", f"{task['task_key']} moved to {next_status}.")
                self._write_reports()
                return f"failed:{task['task_key']}"

    def _build_failure_incident(
        self,
        task: sqlite3.Row,
        exc: Exception,
        attempts: int,
        existing_details: dict[str, Any],
    ) -> dict[str, Any]:
        error = str(exc).strip()
        classification = self._classify_failure(error)
        history = list(existing_details.get("failureHistory") or [])
        event = {
            "at": utc_now(),
            "error": error,
            "attempt": attempts,
            "type": classification["type"],
            "component": classification["component"],
            "playbook": classification["playbook"],
        }
        watchdog_report = None
        if classification["type"] in {"timeout", "live-bridge-timeout"}:
            watchdog_report = self._run_watchdog_incident(
                {
                    "type": classification["type"],
                    "taskKey": str(task["task_key"]),
                    "kind": str(task["kind"]),
                    "attempt": attempts,
                    "error": error,
                    "component": classification["component"],
                }
            )
            if watchdog_report:
                event["watchdog"] = {
                    "generatedAt": watchdog_report.get("generatedAt"),
                    "actions": watchdog_report.get("actions") or [],
                    "dashboardHealthy": watchdog_report.get("dashboardHealthy"),
                    "ollamaHealthy": watchdog_report.get("ollamaHealthy"),
                }
        history.append(event)
        details = dict(existing_details)
        details.update(
            {
                "error": error,
                "attempts": attempts,
                "failureHistory": history[-20:],
                "rca": {
                    "type": classification["type"],
                    "component": classification["component"],
                    "summary": classification["summary"],
                    "playbook": classification["playbook"],
                    "lastUpdatedAt": utc_now(),
                },
            }
        )
        if watchdog_report:
            details["lastWatchdogIncident"] = watchdog_report
        return details

    def _classify_failure(self, error: str) -> dict[str, Any]:
        message = error.strip()
        lower = message.lower()
        if (
            "does not show clear" in lower
            or "mixes languages" in lower
            or "meta distractor" in lower
            or "rejected invalid question draft" in lower
            or "rejected invalid lesson draft" in lower
        ):
            return {
                "type": "repairable-content",
                "component": "writer",
                "summary": "The draft is weak or linguistically inconsistent, but this is a repairable content problem.",
                "playbook": [
                    "Do not quarantine early.",
                    "Retry through the writer path first.",
                    "Prefer course-writer reconstruction for language and distractor quality defects.",
                    "Escalate only after the full repair budget is exhausted.",
                ],
            }
        if "timed out" in lower and "live bridge" in lower:
            return {
                "type": "live-bridge-timeout",
                "component": "live-bridge",
                "summary": "The live Amanoba bridge exceeded its response window.",
                "playbook": [
                    "Run the watchdog incident cycle immediately.",
                    "Check dashboard, worker, and Ollama health.",
                    "Restart the affected component if unhealthy.",
                    "Kick the worker again only after the queue is healthy.",
                ],
            }
        if "timed out" in lower:
            return {
                "type": "timeout",
                "component": "worker",
                "summary": "The task exceeded the allowed processing time.",
                "playbook": [
                    "Run the watchdog incident cycle immediately.",
                    "Kill stale worker processes and clear stale locks.",
                    "Verify dashboard and provider health.",
                    "Restart only the unhealthy service, or the full stack if recovery fails.",
                ],
            }
        if "did not return json" in lower:
            return {
                "type": "provider-json",
                "component": "runtime-provider",
                "summary": "The rewrite provider returned an invalid payload shape.",
                "playbook": [
                    "Preserve the card in Failed for review.",
                    "Retry once through the normal queue.",
                    "Quarantine after repeated bounces for human review.",
                ],
            }
        if "still failed validation" in lower:
            return {
                "type": "validation-regression",
                "component": "validator",
                "summary": "The rewritten content still failed Amanoba validation rules.",
                "playbook": [
                    "Keep the card visible in Failed.",
                    "Retry once with the accumulated history and human feedback.",
                    "Quarantine after repeated bounces for human review.",
                ],
            }
        return {
            "type": "unknown",
            "component": "worker",
            "summary": "The task failed with an uncategorized worker error.",
            "playbook": [
                "Record the error and keep the card visible.",
                "Retry once through the queue.",
                "Quarantine after repeated bounces for human review.",
            ],
        }

    def _run_watchdog_incident(self, incident: dict[str, Any]) -> dict[str, Any] | None:
        try:
            from .watchdog import CourseQualityWatchdog

            return CourseQualityWatchdog(self.config).run_once(incident=incident)
        except Exception as exc:
            return {
                "generatedAt": utc_now(),
                "incident": incident,
                "actions": [],
                "error": f"Watchdog incident handling failed: {exc}",
            }

    def _record_system_feedback(self, task_key: str, incident: dict[str, Any], next_status: str) -> None:
        rca = dict(incident.get("rca") or {})
        summary = str(rca.get("summary") or "Task failure recorded.").strip()
        playbook = ", ".join(str(item) for item in (rca.get("playbook") or []))
        if next_status == "quarantined":
            self.state.add_feedback_comment(
                task_key,
                f"[system] Quarantined after repeated bounce-backs. RCA: {summary} Proven recovery: {playbook}",
            )
            return
        if rca.get("type") in {"timeout", "live-bridge-timeout"}:
            self.state.add_feedback_comment(
                task_key,
                f"[system] Timeout RCA captured. Watchdog incident run triggered. Proven recovery: {playbook}",
            )

    def _process_task_with_timeout(self, task: sqlite3.Row) -> dict[str, Any]:
        timeout_seconds = max(1, int(self.config.max_task_runtime_seconds))
        try:
            is_main_thread = threading.current_thread() is threading.main_thread()
        except Exception:
            is_main_thread = False
        if not is_main_thread or not hasattr(signal, "SIGALRM"):
            return self._process_task(task)

        class _TaskTimeout(Exception):
            pass

        def _handler(signum: int, frame: Any) -> None:
            raise _TaskTimeout()

        previous = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, _handler)
        signal.alarm(timeout_seconds)
        try:
            return self._process_task(task)
        except _TaskTimeout as exc:
            raise RuntimeError(f"Task timed out after {timeout_seconds} seconds.") from exc
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous)

    def trigger_processing(self, max_items: int = 1) -> dict[str, Any]:
        return {
            "accepted": False,
            "reason": "single-process-worker",
            "summary": self.action_snapshot(),
        }

    def action_snapshot(self) -> dict[str, Any]:
        feed = self.feed_snapshot(limit=self.config.action_feed_limit)
        return {
            "generatedAt": feed["generatedAt"],
            "counts": feed["counts"],
            "queued": feed["queued"],
            "running": feed["running"],
            "completed": feed["completed"],
            "failed": feed["failed"],
        }

    def power_profiles(self) -> dict[str, dict[str, int | float]]:
        return {
            "gentle": {"temperature": 0.1, "num_predict": 256, "num_ctx": 1536, "num_thread": 1},
            "balanced": {"temperature": 0.1, "num_predict": 384, "num_ctx": 2048, "num_thread": 2},
            "fast": {"temperature": 0.15, "num_predict": 512, "num_ctx": 3072, "num_thread": 4},
        }

    def _power_profile_with_effective_limits(self, profile: dict[str, int | float]) -> dict[str, int | float]:
        enriched = dict(profile)
        enriched["lesson_rewrite_predict"] = int(enriched.get("lesson_num_predict") or enriched.get("num_predict") or 0)
        enriched["question_rewrite_predict"] = int(enriched.get("question_num_predict") or enriched.get("num_predict") or 0)
        return enriched

    def current_power_mode(self) -> str:
        if self.config.power_mode in self.power_profiles():
            return self.config.power_mode
        ollama = dict(self.config.runtime_config.get("ollama") or {})
        active = {
            "temperature": float(ollama.get("temperature") or 0.1),
            "num_predict": int(ollama.get("num_predict") or 384),
            "num_ctx": int(ollama.get("num_ctx") or 2048),
            "num_thread": int(ollama.get("num_thread") or 2),
        }
        for name, profile in self.power_profiles().items():
            if active == profile:
                return name
        return "custom"

    def set_power_mode(self, mode: str) -> dict[str, Any]:
        profiles = self.power_profiles()
        if mode not in profiles:
            raise ValueError(f"Unsupported power mode: {mode}")
        raw = json.loads(self.config.config_path.read_text(encoding="utf-8"))
        runtime = dict(raw.get("runtime") or {})
        ollama = dict(runtime.get("ollama") or {})
        ollama.update(profiles[mode])
        runtime["ollama"] = ollama
        raw["runtime"] = runtime
        raw["power_mode"] = mode
        temp_path = self.config.config_path.with_suffix(self.config.config_path.suffix + ".tmp")
        temp_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp_path.replace(self.config.config_path)
        self.config.power_mode = mode
        self.config.runtime_config = runtime
        self.runtime = LocalRuntimeManager(self.config.runtime_config)
        self._restart_launch_agent("com.amanoba.coursequality.worker")
        return {
            "mode": mode,
            "profile": self._power_profile_with_effective_limits(profiles[mode]),
            "summary": self.action_snapshot(),
        }

    def _restart_launch_agent(self, label: str) -> None:
        uid = str(os.getuid())
        try:
            subprocess.run(["launchctl", "kickstart", "-k", f"gui/{uid}/{label}"], check=False, capture_output=True)
        except Exception:
            return

    def _bootout_launch_agent(self, label: str) -> None:
        uid = str(os.getuid())
        try:
            subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"], check=False, capture_output=True)
        except Exception:
            return

    def _launch_agent_path(self, label: str) -> Path | None:
        launch_dir = Path.home() / "Library" / "LaunchAgents"
        candidate = launch_dir / f"{label}.plist"
        return candidate if candidate.exists() else None

    def restart_services(self, reason: str | None = None) -> dict[str, Any]:
        labels = [
            "com.amanoba.coursequality.worker",
            "com.amanoba.coursequality.dashboard",
            "com.amanoba.coursequality.watchdog",
            "com.amanoba.coursequality.ollama",
        ]
        actions: list[dict[str, Any]] = []
        for label in labels:
            self._bootout_launch_agent(label)
            actions.append({"label": label, "action": "bootout"})
        for label in labels:
            plist = self._launch_agent_path(label)
            if plist is None:
                actions.append({"label": label, "action": "bootstrap", "status": "skipped"})
                continue
            try:
                subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist)], check=False, capture_output=True)
                subprocess.run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{label}"], check=False, capture_output=True)
                actions.append({"label": label, "action": "bootstrap", "status": "ok"})
            except Exception as exc:
                actions.append({"label": label, "action": "bootstrap", "status": "error", "error": str(exc)})
        return {
            "ok": True,
            "reason": reason or "restart-services",
            "actions": actions,
        }

    def shutdown_services(self, reason: str | None = None) -> dict[str, Any]:
        labels = [
            "com.amanoba.coursequality.worker",
            "com.amanoba.coursequality.dashboard",
            "com.amanoba.coursequality.watchdog",
            "com.amanoba.coursequality.ollama",
        ]
        actions: list[dict[str, Any]] = []
        for label in labels:
            self._bootout_launch_agent(label)
            actions.append({"label": label, "action": "bootout"})
        return {
            "ok": True,
            "reason": reason or "shutdown-services",
            "actions": actions,
        }

    def run_daemon(self) -> None:
        self._set_heartbeat("starting", message="Starting single-process QC worker.", advance_progress=True)
        self._start_heartbeat_loop()
        next_scan_at = 0.0
        try:
            while True:
                now = time.time()
                if now >= next_scan_at:
                    try:
                        self.scan()
                    except Exception as exc:
                        self._set_heartbeat(
                            "waiting-dependency",
                            message=f"QC scan blocked: {exc}",
                            advance_progress=True,
                        )
                    next_scan_at = now + self.config.scan_interval_seconds
                recovered = self._recover_orphan_running_tasks(reason="daemon-loop")
                if recovered:
                    self._set_heartbeat("selecting", message=f"Recovered {recovered} orphan running task(s) in daemon loop.", advance_progress=True)
                archived = self.state.archive_non_english_tasks("en")
                if archived:
                    self._set_heartbeat("selecting", message=f"Archived {archived} non-English QC task(s) in English-only mode.", advance_progress=True)
                self.state.recover_stale_running_tasks(
                    max_runtime_seconds=self.config.max_task_runtime_seconds,
                    max_attempts=self.config.max_attempts_per_task,
                )
                process_result = None
                if self.state.counts().get("running", 0) <= 0:
                    process_result = self.process_one()
                if process_result == "blocked":
                    time.sleep(self.config.queue_check_interval_seconds)
                    continue
                self._set_heartbeat("sleeping", message="Waiting for next QC cycle.", advance_progress=False)
                time.sleep(self.config.queue_check_interval_seconds)
        finally:
            self._clear_heartbeat_task("stopped", "QC worker stopped.")
            self._stop_heartbeat_loop()

    def feed_snapshot(self, limit: int | None = None) -> dict[str, Any]:
        feed = self.state.feed_snapshot(limit or self.config.feed_limit)
        feed["inventory"] = self._cached_inventory_counts()
        for key in ["queued", "running", "completed", "failed", "quarantined", "archived"]:
            feed[key] = [self._enrich_task_summary(item) for item in feed.get(key, [])]
        return feed

    def task_detail(self, task_key: str) -> dict[str, Any] | None:
        task = self.state.task_detail(task_key)
        if task is None:
            return None
        return self._enrich_task_summary(task)

    def health_snapshot(self) -> dict[str, Any]:
        profiles = {name: self._power_profile_with_effective_limits(profile) for name, profile in self.power_profiles().items()}
        active_profile = self._power_profile_with_effective_limits(dict(self.config.runtime_config.get("ollama") or {}))
        worker_state = self._worker_state_snapshot()
        resident_roles = self.resident_role_snapshot()
        return {
            "version": AMANOBA_VERSION,
            "generatedAt": utc_now(),
            "runtime": self.runtime.health_snapshot(),
            "system": {
                "residentRoles": resident_roles,
            },
            "power": {
                "mode": self.current_power_mode(),
                "profiles": profiles,
                "profile": active_profile,
            },
            "counts": self.state.counts(),
            "inventory": self.live_inventory_counts(),
            "worker": self.worker_status_snapshot(),
            "workerState": worker_state,
            "roles": self._role_status_snapshot(worker_state, resident_roles),
            "creatorPipeline": self._creator_pipeline_manifest(),
            "dashboard": {
                "host": self.config.dashboard_host,
                "port": self.config.dashboard_port,
                "url": f"http://{self.config.dashboard_host}:{self.config.dashboard_port}",
            },
        }

    def dashboard_health_snapshot(self) -> dict[str, Any]:
        cached: dict[str, Any] = {}
        report_path = self.config.reports_dir / "health.json"
        if report_path.exists():
            try:
                loaded = json.loads(report_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    cached = loaded
            except json.JSONDecodeError:
                cached = {}
        runtime_snapshot = dict(cached.get("runtime") or {})
        if not runtime_snapshot:
            runtime_snapshot = self.runtime.health_snapshot()
        power_snapshot = dict(cached.get("power") or {})
        if not power_snapshot:
            profiles = {name: self._power_profile_with_effective_limits(profile) for name, profile in self.power_profiles().items()}
            active_profile = self._power_profile_with_effective_limits(dict(self.config.runtime_config.get("ollama") or {}))
            power_snapshot = {
                "mode": self.current_power_mode(),
                "profiles": profiles,
                "profile": active_profile,
            }
        resident_roles = self.resident_role_snapshot()
        system_snapshot = {
            "residentRoles": resident_roles,
        }
        counts_snapshot = self.state.counts()
        worker_state = self._worker_state_snapshot()
        return {
            "version": str(cached.get("version") or AMANOBA_VERSION),
            "generatedAt": utc_now(),
            "runtime": runtime_snapshot,
            "system": system_snapshot,
            "power": power_snapshot,
            "counts": counts_snapshot,
            "inventory": dict(cached.get("inventory") or {}),
            "worker": self.worker_status_snapshot(),
            "workerState": worker_state,
            "roles": self._role_status_snapshot(worker_state, resident_roles),
            "dashboard": {
                "host": self.config.dashboard_host,
                "port": self.config.dashboard_port,
                "url": f"http://{self.config.dashboard_host}:{self.config.dashboard_port}",
            },
            "creatorPipeline": self._creator_pipeline_manifest(),
        }

    def _creator_pipeline_manifest(self) -> dict[str, Any]:
        runtime_cfg = dict(self.config.runtime_config or {})
        configured = dict(runtime_cfg.get("creator_pipeline") or {})
        resident_roles = list(runtime_cfg.get("resident_creator_roles") or DEFAULT_RESIDENT_CREATOR_ROLES)
        resident_by_role: dict[str, dict[str, Any]] = {}
        for raw in resident_roles:
            item = dict(raw or {})
            role_name = str(item.get("name") or "").strip().lower()
            if role_name:
                resident_by_role[role_name] = item
        manifest: dict[str, Any] = {}
        for role, defaults in DEFAULT_CREATOR_PIPELINE.items():
            role_config = dict(configured.get(role) or {})
            resident_config = dict(resident_by_role.get(role) or {})
            configured_model = str(role_config.get("model") or resident_config.get("model_label") or defaults["model"]).strip()
            provider = str(role_config.get("provider") or defaults.get("provider") or "").strip().lower()
            install_target = str(resident_config.get("model") or role_config.get("model") or configured_model).strip()
            installed, location = self._creator_model_install_status(install_target, provider)
            server_host = str(role_config.get("server_host") or resident_config.get("host") or defaults.get("server_host") or "127.0.0.1")
            try:
                server_port = int(role_config.get("server_port") or resident_config.get("port") or defaults.get("server_port") or 0)
            except (TypeError, ValueError):
                server_port = 0
            resident_server = bool(role_config.get("resident_server", defaults.get("resident_server", bool(resident_config))))
            reachable = False
            if resident_server and server_port > 0:
                try:
                    with socket.create_connection((server_host, server_port), timeout=1.0):
                        reachable = True
                except OSError:
                    reachable = False
            state = "available" if installed and (reachable or not resident_server) else ("degraded" if installed else "missing")
            manifest[role] = {
                "tool": str(role_config.get("tool") or defaults["tool"]),
                "model": configured_model,
                "label": str(role_config.get("label") or resident_config.get("model_label") or defaults.get("label") or configured_model),
                "provider": provider,
                "statusLabel": str(role_config.get("statusLabel") or defaults["statusLabel"]),
                "description": str(role_config.get("description") or defaults["description"]),
                "installed": installed,
                "resident_server": resident_server,
                "server_host": server_host,
                "server_port": server_port,
                "launch_label": str(resident_config.get("launch_label") or ""),
                "reachable": reachable,
                "location": location,
                "state": state,
            }
        return manifest

    def _creator_model_install_status(self, model_name: str, provider: str | None) -> tuple[bool, str]:
        normalized = str(model_name or "").strip()
        if not normalized:
            return False, ""
        provider_name = str(provider or "").strip().lower()
        if provider_name == "mlx":
            path = resolve_mlx_model_path(normalized, base_dir=self.config.workspace_root, label=normalized)
            if path.exists():
                return True, str(path)
            return False, str(path)
        if provider_name == "worker":
            return True, "course_quality_daemon worker"
        if provider_name == "validator":
            return True, "local validator"
        # generic local cache lookup for named models
        cache_root = Path.home() / ".cache" / "huggingface" / "hub"
        matches = list(cache_root.glob(f"models--*--{normalized}"))
        if matches:
            return True, str(matches[0])
        return False, ""

    def _role_status_snapshot(self, worker_state: dict[str, Any], resident_snapshot: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        pipeline = self._creator_pipeline_manifest()
        resident_roles = {
            str(item.get("name") or "").strip().lower(): dict(item or {})
            for item in (resident_snapshot or self.resident_role_snapshot())
        }
        worker_phase = str(worker_state.get("phase") or "idle").strip().lower() or "idle"
        worker_label = "working" if worker_state.get("state") == "working" else ("stalled" if worker_state.get("stalled") else "idle")
        role_names = ("drafter", "writer", "judge")

        def _role_snapshot(role: str) -> dict[str, Any]:
            pipeline_item = dict(pipeline.get(role) or {})
            resident_item = dict(resident_roles.get(role) or {})
            health = dict(self.runtime.creator_role_health(role) or {})
            requested_model = str(pipeline_item.get("label") or pipeline_item.get("model") or "").strip()
            runtime_model = str(health.get("resolvedModel") or health.get("configuredModel") or "").strip()
            runtime_provider = str(health.get("provider") or pipeline_item.get("provider") or "").strip()
            installed = bool(pipeline_item.get("installed"))
            available = bool(health.get("available"))
            status = str(health.get("status") or ("MISSING" if not installed else "UNKNOWN")).upper()
            resident_reachable = bool(resident_item.get("reachable"))
            if resident_reachable:
                runtime_provider = runtime_provider or str(pipeline_item.get("provider") or "mlx")
                runtime_model = runtime_model or requested_model or str(resident_item.get("modelLabel") or "").strip()
                available = True
                if status in {"STANDBY", "UNKNOWN", "UNAVAILABLE", ""}:
                    status = "HEALTHY"
            if not installed:
                status = "MISSING"
            detail_bits = [str(health.get("detail") or "").strip()]
            resident_detail = str(resident_item.get("detail") or "").strip()
            if resident_reachable and resident_detail:
                detail_bits = [resident_detail]
            if requested_model and runtime_model and requested_model != runtime_model:
                detail_bits.append(f"runtime: {runtime_model}")
            elif runtime_model and not detail_bits[0]:
                detail_bits.append(f"runtime: {runtime_model}")
            detail_bits = [bit for bit in detail_bits if bit]
            detail = " | ".join(detail_bits) or str(pipeline_item.get("description") or "")
            state = "available" if installed and available else ("missing" if not installed else ("degraded" if status in {"DEGRADED", "UNAVAILABLE"} else "available"))
            return {
                "provider": runtime_provider or str(pipeline_item.get("provider") or ""),
                "status": status,
                "detail": detail,
                "available": installed and available,
                "tool": pipeline_item.get("tool"),
                "model": requested_model,
                "label": requested_model,
                "runtimeProvider": runtime_provider,
                "runtimeModel": runtime_model,
                "recommendedModel": requested_model,
                "installed": installed,
                "location": str(pipeline_item.get("location") or runtime_model or requested_model or ""),
                "state": state,
                "description": pipeline_item.get("description"),
            }

        def _judge_snapshot() -> dict[str, Any]:
            snapshot = _role_snapshot("judge")
            if worker_state.get("stalled"):
                snapshot["status"] = "DEGRADED"
                snapshot["detail"] = "QC worker stalled."
                snapshot["available"] = False
                snapshot["state"] = "degraded"
            return snapshot

        return {
            "drafter": _role_snapshot("drafter") | {
                "workerPhase": worker_phase,
                "workerState": worker_label,
            },
            "writer": _role_snapshot("writer"),
            "judge": _judge_snapshot(),
            "pipeline": pipeline,
        }

    def resident_role_snapshot(self) -> list[dict[str, Any]]:
        runtime_cfg = dict(self.config.runtime_config or {})
        roles = list(runtime_cfg.get("resident_creator_roles") or DEFAULT_RESIDENT_CREATOR_ROLES)
        snapshot: list[dict[str, Any]] = []
        for raw in roles:
            item = dict(raw or {})
            name = str(item.get("name") or "ROLE").strip().upper()
            host = str(item.get("host") or "127.0.0.1").strip()
            try:
                port = int(item.get("port") or 0)
            except (TypeError, ValueError):
                port = 0
            reachable = False
            status = "UNAVAILABLE"
            detail = f"{host}:{port}" if port > 0 else host
            if port > 0:
                try:
                    with socket.create_connection((host, port), timeout=1.5):
                        reachable = True
                    detail = f"reachable on {host}:{port}"
                except OSError as exc:
                    detail = f"unreachable on {host}:{port} ({exc.__class__.__name__})"
            payload = _resident_role_health_payload(host, port) if reachable and port > 0 else None
            model_label = str(item.get("model_label") or (payload or {}).get("modelLabel") or "").strip()
            launch_label = str(item.get("launch_label") or "").strip()
            if payload:
                health_status = str(payload.get("status") or "").strip().upper()
                if health_status:
                    detail = f"{detail}; {health_status.lower()}"
                    status = "HEALTHY" if health_status in {"HEALTHY", "WARM"} else health_status
            elif reachable:
                status = "HEALTHY"
            snapshot.append(
                {
                    "name": name,
                    "host": host,
                    "port": port,
                    "status": status,
                    "reachable": reachable,
                    "detail": detail,
                    "modelLabel": model_label,
                    "launchLabel": launch_label,
                }
            )
        return snapshot

    def creator_runs_snapshot(self, limit: int = 12) -> dict[str, Any]:
        runs = [self._enrich_creator_run(self._creator_repair_progression_if_needed(run)) for run in self.state.list_creator_runs(limit=limit)]
        active = sum(1 for run in runs if run.get("status") in {"active", "ready-for-live"})
        return {
            "generatedAt": utc_now(),
            "count": len(runs),
            "activeCount": active,
            "runs": runs,
        }

    def creator_run_detail(self, run_id: str) -> dict[str, Any] | None:
        detail = self.state.creator_run_detail(run_id)
        if detail is None:
            return None
        repaired = self._creator_repair_progression_if_needed(detail)
        return self._enrich_creator_run(repaired)

    def create_creator_run(self, topic: str, target_language: str, research_mode: str) -> dict[str, Any]:
        created = self.state.create_creator_run(topic, target_language, research_mode)
        return self._enrich_creator_run(created)

    def creator_save_source(self, run_id: str, source: dict[str, Any]) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        payload = dict(detail.get("payload") or {})
        source_pack = list(payload.get("sourcePack") or [])
        clean_title = str(source.get("title") or "").strip()
        clean_url = str(source.get("url") or "").strip()
        clean_type = str(source.get("sourceType") or "manual").strip() or "manual"
        clean_snippet = str(source.get("snippet") or "").strip()
        if not clean_title and not clean_url:
            raise ValueError("Source needs at least a title or URL.")
        try:
            clean_score = int(float(str(source.get("score") or "50").strip()))
        except ValueError:
            clean_score = 50
        clean_score = max(0, min(clean_score, 100))
        source_id = str(source.get("sourceId") or "").strip() or f"src-{sha256_json({'title': clean_title, 'url': clean_url, 'snippet': clean_snippet})[:12]}"
        domain = ""
        if clean_url.startswith("http"):
            domain = urllib.parse.urlparse(clean_url).netloc.lower().removeprefix("www.")
        review_status = str(source.get("reviewStatus") or "neutral").strip() or "neutral"
        new_item = {
            "sourceId": source_id,
            "title": clean_title,
            "url": clean_url,
            "sourceType": clean_type,
            "score": str(clean_score),
            "snippet": clean_snippet,
            "domain": domain,
            "fetchedAt": utc_now(),
            "reviewStatus": review_status,
        }
        replaced = False
        for index, item in enumerate(source_pack):
            if str(item.get("sourceId") or "") == source_id:
                source_pack[index] = {**item, **new_item}
                replaced = True
                break
        if not replaced:
            source_pack.append(new_item)
        return self._creator_store_source_pack(detail, source_pack, "source-save", f"Saved source {clean_title or clean_url or source_id}.")

    def creator_delete_source(self, run_id: str, source_id: str) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        source_pack = list(((detail.get("payload") or {}).get("sourcePack") or []))
        filtered = [item for item in source_pack if str(item.get("sourceId") or "") != source_id]
        return self._creator_store_source_pack(detail, filtered, "source-delete", f"Deleted source {source_id}.")

    def creator_set_source_status(self, run_id: str, source_id: str, review_status: str) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        status = str(review_status or "neutral").strip().lower()
        if status not in {"preferred", "neutral", "rejected"}:
            raise ValueError("Source status must be preferred, neutral, or rejected.")
        source_pack = list(((detail.get("payload") or {}).get("sourcePack") or []))
        updated = False
        for item in source_pack:
            if str(item.get("sourceId") or "") == source_id:
                item["reviewStatus"] = status
                updated = True
                break
        if not updated:
            raise ValueError("Source not found.")
        return self._creator_store_source_pack(detail, source_pack, "source-status", f"Marked source {source_id} as {status}.")

    def creator_refresh_sources(self, run_id: str) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        payload = dict(detail.get("payload") or {})
        existing = list(payload.get("sourcePack") or [])
        refreshed = self._creator_collect_sources(
            topic=str(detail.get("topic") or ""),
            target_language=str(detail.get("targetLanguage") or ""),
            existing=existing,
        )
        return self._creator_store_source_pack(detail, refreshed, "source-refresh", f"Refreshed source pack. {len(refreshed)} sources available.")

    def _creator_store_source_pack(
        self,
        detail: dict[str, Any],
        source_pack: list[dict[str, Any]],
        action: str,
        comment: str,
    ) -> dict[str, Any]:
        run_id = str(detail.get("runId") or "")
        if not run_id:
            raise ValueError("Creator run is missing run id.")
        payload = dict(detail.get("payload") or {})
        now = utc_now()
        sanitized: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for item in source_pack:
            title = str(item.get("title") or "").strip()
            url = str(item.get("url") or "").strip()
            snippet = str(item.get("snippet") or "").strip()
            source_type = str(item.get("sourceType") or "manual").strip() or "manual"
            if not title and not url and not snippet:
                continue
            source_id = str(item.get("sourceId") or "").strip()
            if not source_id:
                source_id = f"src-{sha256_json({'title': title, 'url': url, 'snippet': snippet, 'type': source_type})[:12]}"
            if source_id in seen_ids:
                continue
            seen_ids.add(source_id)
            review_status = str(item.get("reviewStatus") or "neutral").strip().lower() or "neutral"
            if review_status not in {"preferred", "neutral", "rejected"}:
                review_status = "neutral"
            score_raw = str(item.get("score") or "0").strip() or "0"
            try:
                score = max(0, min(100, int(float(score_raw))))
            except ValueError:
                score = 0
            domain = str(item.get("domain") or "").strip()
            if not domain and url.startswith("http"):
                domain = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
            sanitized.append(
                {
                    "sourceId": source_id,
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "sourceType": source_type,
                    "domain": domain,
                    "score": str(score),
                    "fetchedAt": str(item.get("fetchedAt") or now),
                    "reviewStatus": review_status,
                    "topicMatches": list(item.get("topicMatches") or []),
                }
            )
        payload["sourcePack"] = sanitized
        payload["draftSummary"] = self._creator_refresh_draft_summary(
            {**detail, "payload": payload},
            payload,
        )
        notes = list(payload.get("notes") or [])
        notes.append(
            {
                "type": action,
                "stageKey": str(detail.get("activeStage") or detail.get("currentStage") or ""),
                "comment": comment,
                "createdAt": now,
            }
        )
        payload["notes"] = notes[-50:]
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET payload_json=?, updated_at=? WHERE run_id=?",
                (json.dumps(payload, ensure_ascii=False), now, run_id),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    str(detail.get("activeStage") or detail.get("currentStage") or ""),
                    action,
                    comment,
                    json.dumps(payload, ensure_ascii=False),
                    now,
                ),
            )
            self.state.conn.commit()
        refreshed = self.state.creator_run_detail(run_id)
        if refreshed is None:
            raise ValueError("Creator run not found after source update.")
        return self._enrich_creator_run(refreshed)

    def creator_action(self, run_id: str, action: str, comment: str = "") -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        active_stage = str(detail.get("activeStage") or detail.get("currentStage") or "").strip()
        clean_action = action.strip().lower()
        clean_comment = str(comment or "").strip()
        if clean_action == "accept":
            self._creator_assert_stage_acceptance_ready(detail, active_stage)
        if clean_action == "accept" and active_stage == "qc_review":
            qc_status = dict(((detail.get("payload") or {}).get("qcStatus") or {}))
            total = int(qc_status.get("total") or 0)
            if total <= 0:
                raise ValueError("Inject the approved draft into QC before accepting QC Review.")
            if int(qc_status.get("completed") or 0) < total:
                raise ValueError("QC Review cannot be accepted until all injected QC tasks are completed.")
            if int(qc_status.get("failed") or 0) > 0 or int(qc_status.get("quarantined") or 0) > 0:
                raise ValueError("QC Review cannot be accepted while failed or quarantined QC tasks remain.")
        if clean_action == "accept" and active_stage == "draft_to_live":
            promotion = dict(((detail.get("payload") or {}).get("promotion") or {}))
            package_path = str(promotion.get("packagePath") or "").strip()
            if not package_path:
                raise ValueError("Generate the draft package before accepting Draft To Live.")
            import_status = dict(((detail.get("payload") or {}).get("importStatus") or {}))
            if not str(import_status.get("courseId") or "").strip():
                raise ValueError("Import the draft package into Amanoba before accepting Draft To Live.")
            publish_status = dict(((detail.get("payload") or {}).get("publishStatus") or {}))
            if publish_status.get("status") != "published-live":
                raise ValueError("Publish the imported draft in Amanoba before accepting Draft To Live.")
        if clean_action == "delete":
            updated = self.state.creator_action(run_id, action, clean_comment)
            return self._enrich_creator_run(updated)
        if clean_action == "accept":
            updated = self.state.creator_action(run_id, action, clean_comment)
            enriched = self._enrich_creator_run(updated)
            next_stage = str(enriched.get("activeStage") or "").strip()
            if next_stage and next_stage in {"blueprint", "lesson_generation", "quiz_generation", "qc_review", "draft_to_live"}:
                try:
                    return self.creator_generate_artifact(run_id, next_stage, "")
                except Exception:
                    return self.creator_run_detail(run_id) or enriched
            return enriched
        if clean_action == "update":
            target_stage = self._creator_previous_stage_key(detail, active_stage)
            rewound = self._creator_rewind_to_stage(detail, target_stage, clean_comment)
            try:
                return self.creator_generate_artifact(run_id, target_stage, clean_comment)
            except Exception:
                return rewound
        updated = self.state.creator_action(run_id, action, clean_comment)
        return self._enrich_creator_run(updated)

    def _creator_previous_stage_key(self, detail: dict[str, Any], active_stage: str) -> str:
        stages = list((detail.get("payload") or {}).get("stages") or detail.get("stages") or self.state._creator_stage_template())
        order = [str(item.get("key") or "") for item in stages if str(item.get("key") or "")]
        if active_stage not in order:
            return "research"
        index = order.index(active_stage)
        if index <= 1:
            return "research"
        return order[index - 1]

    def _creator_rewind_to_stage(self, detail: dict[str, Any], target_stage: str, comment: str) -> dict[str, Any]:
        run_id = str(detail.get("runId") or "")
        payload = dict(detail.get("payload") or {})
        stages = list(payload.get("stages") or detail.get("stages") or [])
        target_index = next((idx for idx, item in enumerate(stages) if str(item.get("key") or "") == target_stage), None)
        if target_index is None:
            raise ValueError("Cannot move creator run back because the target stage does not exist.")
        now = utc_now()
        for idx, stage in enumerate(stages):
            if idx < target_index:
                stage["status"] = "completed"
            elif idx == target_index:
                stage["status"] = "active"
            else:
                stage["status"] = "blocked"
            stage["updatedAt"] = now
        payload["stages"] = stages
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        clear_keys = [str(item.get("key") or "") for item in stages[target_index:]]
        for key in clear_keys:
            stage_artifacts.pop(key, None)
        payload["stageArtifacts"] = stage_artifacts
        if target_index <= 4:
            payload.pop("qcStatus", None)
            payload.pop("qcPlan", None)
            payload.pop("qcPayload", None)
        if target_index <= 5:
            payload.pop("promotion", None)
            payload.pop("importStatus", None)
            payload.pop("publishStatus", None)
            payload.pop("rollbackStatus", None)
            payload.pop("deleteStatus", None)
        notes = list(payload.get("notes") or [])
        if comment:
            notes.append(
                {
                    "type": "human-update",
                    "stageKey": target_stage,
                    "comment": comment,
                    "createdAt": now,
                }
            )
        notes.append(
            {
                "type": "system-rework",
                "stageKey": target_stage,
                "comment": f"Run moved back to {self._creator_stage_label(target_stage)} for rework.",
                "createdAt": now,
            }
        )
        payload["notes"] = notes[-50:]
        payload["draftSummary"] = self._creator_refresh_draft_summary(
            {**detail, "payload": payload, "stages": stages, "status": "active", "currentStage": target_stage},
            payload,
        )
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET status=?, current_stage=?, payload_json=?, updated_at=? WHERE run_id=?",
                ("active", target_stage, json.dumps(payload, ensure_ascii=False), now, run_id),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    target_stage,
                    "modify",
                    comment or f"Moved back to {self._creator_stage_label(target_stage)} for rework.",
                    json.dumps(payload, ensure_ascii=False),
                    now,
                ),
            )
            self.state.conn.commit()
        refreshed = self.state.creator_run_detail(run_id)
        if refreshed is None:
            raise ValueError("Creator run not found after moving back for rework.")
        return self._enrich_creator_run(refreshed)

    def creator_save_artifact(self, run_id: str, content: str, stage_key: str | None = None) -> dict[str, Any]:
        updated = self.state.creator_save_artifact(run_id, content, stage_key)
        return self._enrich_creator_run(updated)

    def creator_generate_artifact(self, run_id: str, stage_key: str | None = None, feedback_comment: str = "") -> dict[str, Any]:
        detail = self.state.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        active_stage = str(stage_key or detail.get("activeStage") or detail.get("currentStage") or "").strip()
        if not active_stage:
            raise ValueError("Creator run has no active stage.")
        payload = detail.get("payload") or {}
        retry_policy = dict(payload.get("retryPolicy") or self._creator_stage_retry_policy())
        stage_attempts = dict(payload.get("stageAttempts") or {})
        stage_attempts[active_stage] = int(stage_attempts.get(active_stage) or 0) + 1
        max_attempts = int(retry_policy.get("maxAttempts") or 5)
        if stage_attempts[active_stage] > max_attempts:
            raise ValueError(f"{self._creator_stage_label(active_stage)} reached the global Trinity attempt cap of {max_attempts}.")
        stage_artifacts = payload.get("stageArtifacts") or {}
        stages = list(detail.get("stages") or [])
        self._creator_assert_stage_prerequisites(active_stage, stages)
        current_artifact = self._creator_stage_seed_artifact(detail, active_stage, stage_artifacts)
        context_artifacts = {
            key: str((value or {}).get("content") or "")
            for key, value in (stage_artifacts or {}).items()
        }
        revision_request = self._creator_generation_feedback(detail, active_stage, feedback_comment)
        source_pack: list[dict[str, str]] = list(payload.get("sourcePack") or [])
        if active_stage == "research" and str(detail.get("researchMode") or "") != "offline":
            source_pack = self._creator_collect_sources(
                topic=str(detail.get("topic") or ""),
                target_language=str(detail.get("targetLanguage") or ""),
                existing=source_pack,
            )
        if active_stage == "qc_review":
            self._creator_assert_qc_handoff_ready(detail)
            qc_handoff = self._creator_enqueue_qc_review(detail)
            result = {
                "provider": "creator-qc-handoff",
                "role": "judge",
                "content": qc_handoff["content"],
                "warning": "",
            }
            generated_content = result["content"]
            updated = self.state.creator_save_artifact(run_id, result["content"], active_stage)
            updated_payload = updated.get("payload") or {}
            updated_payload["qcPlan"] = qc_handoff["plan"]
            updated_payload["qcJudge"] = {
                "provider": result["provider"],
                "role": "judge",
                "model": "",
                "content": result["content"],
                "generatedAt": utc_now(),
                "provenance": self._creator_stage_provenance(detail, active_stage, result, revision_request),
            }
        elif active_stage == "draft_to_live":
            draft_summary_content = self._creator_build_draft_to_live_summary(detail)
            result = {
                "provider": "creator-draft-summary",
                "role": "judge",
                "content": draft_summary_content,
                "warning": "",
            }
            generated_content = result["content"]
            updated = self.state.creator_save_artifact(run_id, draft_summary_content, active_stage)
            updated_payload = updated.get("payload") or {}
            updated_payload["draftToLiveJudge"] = {
                "provider": result["provider"],
                "role": "judge",
                "model": "",
                "content": draft_summary_content,
                "generatedAt": utc_now(),
                "provenance": self._creator_stage_provenance(detail, active_stage, result, revision_request),
            }
        else:
            result = self.runtime.generate_creator_stage(
                stage_key=active_stage,
                topic=str(detail.get("topic") or ""),
                target_language=str(detail.get("targetLanguage") or ""),
                research_mode=str(detail.get("researchMode") or ""),
                current_artifact=current_artifact,
                context_artifacts=context_artifacts,
                source_pack=source_pack,
                revision_request=revision_request,
            )
            generated_content = str(result.get("content") or "")
            stage_role = "drafter" if active_stage == "research" else "writer"
            result["role"] = stage_role
            result["status"] = str(result.get("status") or "").strip() or "HEALTHY"
            valid, validation_detail = self._creator_validate_stage_artifact(active_stage, generated_content)
            if not valid:
                fallback_content = self._creator_stage_seed_artifact_fresh(detail, active_stage)
                fallback_valid, _ = self._creator_validate_stage_artifact(active_stage, fallback_content)
                if fallback_valid:
                    generated_content = fallback_content
                    warning_prefix = f"Generated draft rejected: {validation_detail}"
                    warning_suffix = str(result.get("warning") or "").strip()
                    result["provider"] = f"{result.get('provider') or 'generator'} -> seed-fallback"
                    result["warning"] = warning_prefix + (f" | {warning_suffix}" if warning_suffix else "")
                else:
                    raise ValueError(validation_detail)
            updated = self.state.creator_save_artifact(run_id, generated_content, active_stage)
            updated_payload = updated.get("payload") or {}
        updated_payload["sourcePack"] = source_pack
        updated_enriched = self._enrich_creator_run({**updated, "payload": updated_payload})
        updated_payload = updated_enriched.get("payload") or updated_payload
        updated_payload["draftSummary"] = self._creator_refresh_draft_summary(updated_enriched, updated_payload)
        generated_at = utc_now()
        stage_artifacts = dict(updated_payload.get("stageArtifacts") or {})
        stage_artifact = dict(stage_artifacts.get(active_stage) or {})
        stage_artifact["content"] = generated_content
        stage_artifact["updatedAt"] = generated_at
        stage_artifact["provenance"] = self._creator_stage_provenance(detail, active_stage, result, revision_request)
        stage_artifacts[active_stage] = stage_artifact
        updated_payload["stageArtifacts"] = stage_artifacts
        updated_payload["retryPolicy"] = retry_policy
        updated_payload["stageAttempts"] = stage_attempts
        notes = list(updated_payload.get("notes") or [])
        warning = str(result.get("warning") or "").strip()
        provider = str(result.get("provider") or "-")
        if revision_request:
            notes.append(
                {
                    "type": "human-feedback-used",
                    "stageKey": active_stage,
                    "comment": revision_request,
                    "createdAt": generated_at,
                }
            )
        notes.append(
            {
                "type": "stage-generate",
                "stageKey": active_stage,
                "comment": (
                    f"Generated draft via {provider} ({str(result.get('role') or 'writer')})."
                    + (" Used human feedback." if revision_request else "")
                    + (f" Warning: {warning}" if warning else "")
                ),
                "createdAt": generated_at,
            }
        )
        updated_payload["notes"] = notes[-50:]
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET payload_json=?, updated_at=? WHERE run_id=?",
                (json.dumps(updated_payload, ensure_ascii=False), generated_at, run_id),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    active_stage,
                    "generate-artifact",
                    (
                        f"Generated draft via {provider} ({str(result.get('role') or 'writer')})."
                        + (" Used human feedback." if revision_request else "")
                        + (f" Warning: {warning}" if warning else "")
                    ),
                    json.dumps(updated_payload, ensure_ascii=False),
                    generated_at,
                ),
            )
            self.state.conn.commit()
        final = self.state.creator_run_detail(run_id)
        if final is None:
            raise ValueError("Creator run not found after generation.")
        return self._enrich_creator_run(final)

    def _creator_generation_feedback(self, detail: dict[str, Any], stage_key: str, feedback_comment: str) -> str:
        explicit = str(feedback_comment or "").strip()
        if explicit:
            return explicit
        notes = list(((detail.get("payload") or {}).get("notes") or detail.get("notes") or []))
        for note in reversed(notes):
            if str(note.get("stageKey") or "") != stage_key:
                continue
            if str(note.get("type") or "") not in {"human-update", "human-feedback-used"}:
                continue
            comment = str(note.get("comment") or "").strip()
            if comment:
                return comment
        return ""

    def _creator_assert_stage_acceptance_ready(self, detail: dict[str, Any], stage_key: str) -> None:
        if not stage_key or stage_key in {"topic_intake", "draft_to_live", "qc_review"}:
            return
        if not self._creator_stage_has_material_artifact(detail, stage_key):
            raise ValueError(
                f"{self._creator_stage_label(stage_key)} cannot be accepted yet because it does not contain a usable artifact. "
                "Generate or save the stage content first."
            )

    def _creator_assert_qc_handoff_ready(self, detail: dict[str, Any]) -> None:
        handoff = self._creator_handoff_status(detail)
        missing = [self._creator_stage_label(item) for item in list(handoff.get("missingStages") or [])]
        if missing:
            label = ", ".join(missing)
            raise ValueError(
                f"QC handoff cannot start because these required stages are still empty or invalid: {label}. "
                "Go back to the first missing stage and generate a real artifact before starting QC."
            )

    def _creator_stage_has_material_artifact(self, detail: dict[str, Any], stage_key: str) -> bool:
        payload = dict(detail.get("payload") or {})
        structured = self._creator_structured_artifacts(detail)
        if stage_key in {"research", "blueprint", "lesson_generation", "quiz_generation"}:
            return bool((structured.get(stage_key) or {}).get("ready"))
        if stage_key == "qc_review":
            qc_status = dict(payload.get("qcStatus") or {})
            return int(qc_status.get("total") or 0) > 0
        if stage_key == "draft_to_live":
            promotion = dict(payload.get("promotion") or {})
            return bool(str(promotion.get("packagePath") or "").strip())
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        content = str((stage_artifacts.get(stage_key) or {}).get("content") or "").strip()
        return bool(content)

    def _creator_first_missing_stage(self, detail: dict[str, Any]) -> str:
        for stage_key in ("research", "blueprint", "lesson_generation", "quiz_generation", "qc_review", "draft_to_live"):
            if not self._creator_stage_has_material_artifact(detail, stage_key):
                return stage_key
        return ""

    def _creator_repair_progression_if_needed(self, detail: dict[str, Any]) -> dict[str, Any]:
        missing_stage = self._creator_first_missing_stage(detail)
        if not missing_stage:
            return detail
        payload = dict(detail.get("payload") or {})
        stages = list(payload.get("stages") or detail.get("stages") or [])
        if not stages:
            return detail
        missing_index = next((idx for idx, item in enumerate(stages) if str(item.get("key") or "") == missing_stage), None)
        if missing_index is None:
            return detail
        current_stage = str(detail.get("currentStage") or "")
        current_index = next((idx for idx, item in enumerate(stages) if str(item.get("key") or "") == current_stage), -1)
        if current_index >= 0 and current_index <= missing_index and str(detail.get("status") or "") == "active":
            return detail
        now = utc_now()
        for idx, stage in enumerate(stages):
            if idx < missing_index:
                stage["status"] = "completed"
            elif idx == missing_index:
                stage["status"] = "active"
            else:
                stage["status"] = "blocked"
            stage["updatedAt"] = now
        payload["stages"] = stages
        notes = list(payload.get("notes") or [])
        notes.append(
            {
                "type": "system-repair",
                "stageKey": missing_stage,
                "comment": f"Creator run was reset to {self._creator_stage_label(missing_stage)} because later stages were recorded without valid artifacts.",
                "createdAt": now,
            }
        )
        payload["notes"] = notes[-50:]
        payload["draftSummary"] = self._creator_refresh_draft_summary(
            {**detail, "stages": stages, "status": "active", "currentStage": missing_stage, "payload": payload},
            payload,
        )
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET status=?, current_stage=?, payload_json=?, updated_at=? WHERE run_id=?",
                ("active", missing_stage, json.dumps(payload, ensure_ascii=False), now, str(detail.get("runId") or "")),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    str(detail.get("runId") or ""),
                    missing_stage,
                    "system-repair",
                    f"Reset creator run to {self._creator_stage_label(missing_stage)} because required artifacts were missing.",
                    json.dumps(payload, ensure_ascii=False),
                    now,
                ),
            )
            self.state.conn.commit()
        repaired = self.state.creator_run_detail(str(detail.get("runId") or ""))
        return repaired or detail

    def creator_promote_draft(self, run_id: str) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        active_stage = str(detail.get("activeStage") or detail.get("currentStage") or "").strip()
        if active_stage != "draft_to_live":
            raise ValueError("Promotion is only available during Draft To Live.")
        payload = dict(detail.get("payload") or {})
        qc_status = dict(payload.get("qcStatus") or {})
        total = int(qc_status.get("total") or 0)
        if total <= 0:
            raise ValueError("No QC-reviewed draft is available to promote.")
        if int(qc_status.get("completed") or 0) < total:
            raise ValueError("Complete all QC tasks before promoting the draft package.")
        if int(qc_status.get("failed") or 0) > 0 or int(qc_status.get("quarantined") or 0) > 0:
            raise ValueError("Resolve failed or quarantined QC tasks before promoting the draft package.")
        package = self._creator_build_course_package(detail)
        export_dir = self.config.reports_dir / "creator-exports" / str(detail.get("runId") or "run")
        export_dir.mkdir(parents=True, exist_ok=True)
        package_path = export_dir / "course-package.json"
        package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        promotion = {
            "status": "draft-package-generated",
            "packagePath": str(package_path),
            "generatedAt": utc_now(),
            "courseId": str((package.get("course") or {}).get("courseId") or ""),
            "lessonCount": len(package.get("lessons") or []),
            "questionCount": sum(len((lesson.get("quizQuestions") or [])) for lesson in (package.get("lessons") or [])),
        }
        draft_artifact = dict((payload.get("stageArtifacts") or {}).get("draft_to_live") or {})
        draft_artifact["content"] = self._creator_build_draft_to_live_summary({**detail, "payload": {**payload, "promotion": promotion}})
        draft_artifact["updatedAt"] = promotion["generatedAt"]
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        stage_artifacts["draft_to_live"] = draft_artifact
        payload["stageArtifacts"] = stage_artifacts
        payload["promotion"] = promotion
        payload["draftSummary"] = self._creator_refresh_draft_summary({**detail, "payload": payload}, payload)
        notes = list(payload.get("notes") or [])
        notes.append(
            {
                "type": "promotion",
                "stageKey": "draft_to_live",
                "comment": f"Draft package exported to {package_path}.",
                "createdAt": promotion["generatedAt"],
            }
        )
        payload["notes"] = notes[-50:]
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET payload_json=?, updated_at=? WHERE run_id=?",
                (json.dumps(payload, ensure_ascii=False), promotion["generatedAt"], run_id),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "draft_to_live",
                    "promote-draft",
                    f"Draft package exported to {package_path}.",
                    json.dumps(payload, ensure_ascii=False),
                    promotion["generatedAt"],
                ),
            )
            self.state.conn.commit()
        final = self.state.creator_run_detail(run_id)
        if final is None:
            raise ValueError("Creator run not found after promotion.")
        return self._enrich_creator_run(final)

    def creator_import_draft(self, run_id: str) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        if self.live_bridge is None:
            raise ValueError("Live Amanoba bridge is not configured.")
        active_stage = str(detail.get("activeStage") or detail.get("currentStage") or "").strip()
        run_status = str(detail.get("status") or "")
        if active_stage != "draft_to_live" and run_status != "completed":
            raise ValueError("Draft import is only available during Draft To Live.")
        payload = dict(detail.get("payload") or {})
        promotion = dict(payload.get("promotion") or {})
        package_path = str(promotion.get("packagePath") or "").strip()
        if not package_path:
            raise ValueError("Generate the draft package before importing into Amanoba.")
        package_file = Path(package_path)
        if not package_file.exists():
            raise ValueError(f"Draft package file is missing: {package_file}")
        package_payload = json.loads(package_file.read_text(encoding="utf-8"))
        result = self.live_bridge.import_package(package_payload)
        imported_course = dict(result.get("course") or {})
        import_status = {
            "status": "draft-imported",
            "importedAt": utc_now(),
            "courseId": str(imported_course.get("courseId") or (package_payload.get("course") or {}).get("courseId") or ""),
            "objectId": str(imported_course.get("objectId") or ""),
            "isDraft": bool(imported_course.get("isDraft", True)),
            "isActive": bool(imported_course.get("isActive", False)),
            "counts": dict(result.get("counts") or {}),
            "existed": bool(result.get("existed")),
        }
        payload["importStatus"] = import_status
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        draft_artifact = dict(stage_artifacts.get("draft_to_live") or {})
        draft_artifact["content"] = self._creator_build_draft_to_live_summary({**detail, "payload": {**payload}})
        draft_artifact["updatedAt"] = import_status["importedAt"]
        stage_artifacts["draft_to_live"] = draft_artifact
        payload["stageArtifacts"] = stage_artifacts
        payload["draftSummary"] = self._creator_refresh_draft_summary({**detail, "payload": payload}, payload)
        notes = list(payload.get("notes") or [])
        notes.append(
            {
                "type": "draft-import",
                "stageKey": "draft_to_live",
                "comment": f"Imported draft package into Amanoba as draft course {import_status['courseId']}.",
                "createdAt": import_status["importedAt"],
            }
        )
        payload["notes"] = notes[-50:]
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET payload_json=?, updated_at=? WHERE run_id=?",
                (json.dumps(payload, ensure_ascii=False), import_status["importedAt"], run_id),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "draft_to_live",
                    "import-draft",
                    f"Imported draft package into Amanoba as draft course {import_status['courseId']}.",
                    json.dumps(payload, ensure_ascii=False),
                    import_status["importedAt"],
                ),
            )
            self.state.conn.commit()
        final = self.state.creator_run_detail(run_id)
        if final is None:
            raise ValueError("Creator run not found after draft import.")
        return self._enrich_creator_run(final)

    def creator_publish_draft(self, run_id: str) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        if self.live_bridge is None:
            raise ValueError("Live Amanoba bridge is not configured.")
        active_stage = str(detail.get("activeStage") or detail.get("currentStage") or "").strip()
        run_status = str(detail.get("status") or "")
        if active_stage != "draft_to_live" and run_status != "completed":
            raise ValueError("Live publish is only available during Draft To Live.")
        payload = dict(detail.get("payload") or {})
        import_status = dict(payload.get("importStatus") or {})
        course_id = str(import_status.get("courseId") or "")
        if not course_id:
            raise ValueError("Import the draft into Amanoba before publishing.")
        result = self.live_bridge.publish_course(course_id)
        published_course = dict(result.get("course") or {})
        publish_status = {
            "status": "published-live",
            "publishedAt": utc_now(),
            "courseId": str(published_course.get("courseId") or course_id),
            "objectId": str(published_course.get("objectId") or ""),
            "isDraft": bool(published_course.get("isDraft", False)),
            "isActive": bool(published_course.get("isActive", True)),
            "counts": dict(result.get("counts") or {}),
        }
        payload["publishStatus"] = publish_status
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        draft_artifact = dict(stage_artifacts.get("draft_to_live") or {})
        draft_artifact["content"] = self._creator_build_draft_to_live_summary({**detail, "payload": {**payload}})
        draft_artifact["updatedAt"] = publish_status["publishedAt"]
        stage_artifacts["draft_to_live"] = draft_artifact
        payload["stageArtifacts"] = stage_artifacts
        payload["draftSummary"] = self._creator_refresh_draft_summary({**detail, "payload": payload}, payload)
        notes = list(payload.get("notes") or [])
        notes.append(
            {
                "type": "live-publish",
                "stageKey": "draft_to_live",
                "comment": f"Published course {publish_status['courseId']} live in Amanoba.",
                "createdAt": publish_status["publishedAt"],
            }
        )
        payload["notes"] = notes[-50:]
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET payload_json=?, updated_at=? WHERE run_id=?",
                (json.dumps(payload, ensure_ascii=False), publish_status["publishedAt"], run_id),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "draft_to_live",
                    "publish-live",
                    f"Published course {publish_status['courseId']} live in Amanoba.",
                    json.dumps(payload, ensure_ascii=False),
                    publish_status["publishedAt"],
                ),
            )
            self.state.conn.commit()
        final = self.state.creator_run_detail(run_id)
        if final is None:
            raise ValueError("Creator run not found after publish.")
        return self._enrich_creator_run(final)

    def creator_rollback_publish(self, run_id: str) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        if self.live_bridge is None:
            raise ValueError("Live Amanoba bridge is not configured.")
        payload = dict(detail.get("payload") or {})
        publish_status = dict(payload.get("publishStatus") or {})
        course_id = str(publish_status.get("courseId") or ((payload.get("importStatus") or {}).get("courseId") or ""))
        if not course_id:
            raise ValueError("No imported Amanoba draft is attached to this creator run.")
        result = self.live_bridge.rollback_publish(course_id)
        rolled_course = dict(result.get("course") or {})
        rollback_status = {
            "status": "rolled-back-to-draft",
            "rolledBackAt": utc_now(),
            "courseId": str(rolled_course.get("courseId") or course_id),
            "objectId": str(rolled_course.get("objectId") or ""),
            "isDraft": bool(rolled_course.get("isDraft", True)),
            "isActive": bool(rolled_course.get("isActive", False)),
            "counts": dict(result.get("counts") or {}),
        }
        payload["rollbackStatus"] = rollback_status
        payload["publishStatus"] = {
            **publish_status,
            "status": "rolled-back",
            "rolledBackAt": rollback_status["rolledBackAt"],
        } if publish_status else {"status": "rolled-back", "rolledBackAt": rollback_status["rolledBackAt"], "courseId": rollback_status["courseId"]}
        stages = list(payload.get("stages") or detail.get("stages") or [])
        for stage in stages:
            if str(stage.get("key") or "") == "draft_to_live":
                stage["status"] = "active"
                stage["updatedAt"] = rollback_status["rolledBackAt"]
        payload["stages"] = stages
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        draft_artifact = dict(stage_artifacts.get("draft_to_live") or {})
        draft_artifact["content"] = self._creator_build_draft_to_live_summary({**detail, "payload": {**payload}})
        draft_artifact["updatedAt"] = rollback_status["rolledBackAt"]
        stage_artifacts["draft_to_live"] = draft_artifact
        payload["stageArtifacts"] = stage_artifacts
        payload["draftSummary"] = self._creator_refresh_draft_summary({**detail, "payload": payload}, payload)
        notes = list(payload.get("notes") or [])
        notes.append(
            {
                "type": "rollback-publish",
                "stageKey": "draft_to_live",
                "comment": f"Rolled back live publish for course {rollback_status['courseId']} to draft/inactive.",
                "createdAt": rollback_status["rolledBackAt"],
            }
        )
        payload["notes"] = notes[-50:]
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET status=?, current_stage=?, payload_json=?, updated_at=? WHERE run_id=?",
                ("active", "draft_to_live", json.dumps(payload, ensure_ascii=False), rollback_status["rolledBackAt"], run_id),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "draft_to_live",
                    "rollback-publish",
                    f"Rolled back live publish for course {rollback_status['courseId']} to draft/inactive.",
                    json.dumps(payload, ensure_ascii=False),
                    rollback_status["rolledBackAt"],
                ),
            )
            self.state.conn.commit()
        final = self.state.creator_run_detail(run_id)
        if final is None:
            raise ValueError("Creator run not found after rollback.")
        return self._enrich_creator_run(final)

    def creator_delete_import(self, run_id: str) -> dict[str, Any]:
        detail = self.creator_run_detail(run_id)
        if detail is None:
            raise ValueError("Creator run not found.")
        if self.live_bridge is None:
            raise ValueError("Live Amanoba bridge is not configured.")
        payload = dict(detail.get("payload") or {})
        publish_status = dict(payload.get("publishStatus") or {})
        if str(publish_status.get("status") or "") == "published-live":
            raise ValueError("Rollback the live publish before deleting the imported Amanoba draft.")
        import_status = dict(payload.get("importStatus") or {})
        course_id = str(import_status.get("courseId") or "")
        if not course_id:
            raise ValueError("No imported Amanoba draft is attached to this creator run.")
        result = self.live_bridge.delete_imported_course(course_id)
        delete_status = {
            "status": "import-deleted",
            "deletedAt": utc_now(),
            "courseId": course_id,
            "objectId": str((result.get("course") or {}).get("objectId") or ""),
            "counts": dict(result.get("counts") or {}),
        }
        payload["deleteStatus"] = delete_status
        payload["importStatus"] = {
            **import_status,
            "status": "import-deleted",
            "deletedAt": delete_status["deletedAt"],
        } if import_status else {"status": "import-deleted", "deletedAt": delete_status["deletedAt"], "courseId": course_id}
        payload["publishStatus"] = {}
        stages = list(payload.get("stages") or detail.get("stages") or [])
        for stage in stages:
            if str(stage.get("key") or "") == "draft_to_live":
                stage["status"] = "active"
                stage["updatedAt"] = delete_status["deletedAt"]
        payload["stages"] = stages
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        draft_artifact = dict(stage_artifacts.get("draft_to_live") or {})
        draft_artifact["content"] = self._creator_build_draft_to_live_summary({**detail, "payload": {**payload}})
        draft_artifact["updatedAt"] = delete_status["deletedAt"]
        stage_artifacts["draft_to_live"] = draft_artifact
        payload["stageArtifacts"] = stage_artifacts
        payload["draftSummary"] = self._creator_refresh_draft_summary({**detail, "payload": payload}, payload)
        notes = list(payload.get("notes") or [])
        notes.append(
            {
                "type": "delete-import",
                "stageKey": "draft_to_live",
                "comment": f"Deleted imported Amanoba draft course {course_id}.",
                "createdAt": delete_status["deletedAt"],
            }
        )
        payload["notes"] = notes[-50:]
        with self.state._lock:
            self.state.conn.execute(
                "UPDATE creator_runs SET status=?, current_stage=?, payload_json=?, updated_at=? WHERE run_id=?",
                ("active", "draft_to_live", json.dumps(payload, ensure_ascii=False), delete_status["deletedAt"], run_id),
            )
            self.state.conn.execute(
                """
                INSERT INTO creator_events(run_id, stage_key, action, comment, payload_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    "draft_to_live",
                    "delete-import",
                    f"Deleted imported Amanoba draft course {course_id}.",
                    json.dumps(payload, ensure_ascii=False),
                    delete_status["deletedAt"],
                ),
            )
            self.state.conn.commit()
        final = self.state.creator_run_detail(run_id)
        if final is None:
            raise ValueError("Creator run not found after import deletion.")
        return self._enrich_creator_run(final)

    def _creator_stage_seed_artifact(
        self,
        detail: dict[str, Any],
        stage_key: str,
        stage_artifacts: dict[str, Any],
    ) -> str:
        existing = str((stage_artifacts.get(stage_key) or {}).get("content") or "").strip()
        if existing and not self._creator_is_placeholder_artifact(stage_key, existing):
            return existing
        topic = str(detail.get("topic") or "").strip()
        target_language = str(detail.get("targetLanguage") or "").strip()
        research_artifact = str((stage_artifacts.get("research") or {}).get("content") or "").strip()
        blueprint_artifact = str((stage_artifacts.get("blueprint") or {}).get("content") or "").strip()
        lesson_artifact = str((stage_artifacts.get("lesson_generation") or {}).get("content") or "").strip()
        source_pack = list((detail.get("payload") or {}).get("sourcePack") or [])
        if stage_key == "blueprint":
            return self._creator_build_blueprint_seed(topic, target_language, research_artifact, source_pack)
        if stage_key == "lesson_generation":
            return self._creator_build_lesson_batch_seed(topic, target_language, blueprint_artifact)
        if stage_key == "quiz_generation":
            return self._creator_build_quiz_batch_seed(topic, target_language, lesson_artifact)
        return ""

    def _creator_stage_seed_artifact_fresh(
        self,
        detail: dict[str, Any],
        stage_key: str,
    ) -> str:
        topic = str(detail.get("topic") or "").strip()
        target_language = str(detail.get("targetLanguage") or "").strip()
        payload = dict(detail.get("payload") or {})
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        research_artifact = str((stage_artifacts.get("research") or {}).get("content") or "").strip()
        blueprint_artifact = str((stage_artifacts.get("blueprint") or {}).get("content") or "").strip()
        lesson_artifact = str((stage_artifacts.get("lesson_generation") or {}).get("content") or "").strip()
        source_pack = list(payload.get("sourcePack") or [])
        if stage_key == "blueprint":
            return self._creator_build_blueprint_seed(topic, target_language, research_artifact, source_pack)
        if stage_key == "lesson_generation":
            return self._creator_build_lesson_batch_seed(topic, target_language, blueprint_artifact)
        if stage_key == "quiz_generation":
            return self._creator_build_quiz_batch_seed(topic, target_language, lesson_artifact)
        return ""

    def _creator_stage_provenance(
        self,
        detail: dict[str, Any],
        stage_key: str,
        result: dict[str, Any],
        revision_request: str,
    ) -> dict[str, Any]:
        return {
            "stageKey": stage_key,
            "role": str(result.get("role") or ""),
            "provider": str(result.get("provider") or ""),
            "model": str(result.get("model") or ""),
            "status": str(result.get("status") or ""),
            "revisionRequest": revision_request.strip(),
            "topic": str(detail.get("topic") or ""),
            "targetLanguage": str(detail.get("targetLanguage") or ""),
            "generatedAt": utc_now(),
        }

    def _creator_public_course_title(self, topic: str) -> str:
        text = re.sub(r"\s+", " ", str(topic or "").strip()).strip(" ,.-")
        if not text:
            return "Untitled course"
        match = re.match(r"^(?P<subject>.+?)\s+for\s+beginners,\s*how\s+to\s+(?P<action>.+)$", text, flags=re.I)
        if match:
            subject = match.group("subject").strip()
            action = match.group("action").strip().rstrip(".")
            return f"{subject} for Beginners: How to {action[:1].lower() + action[1:] if action else action}"
        return text

    def _creator_public_course_description(
        self,
        topic: str,
        research_sections: dict[str, list[str]],
        blueprint_rows: list[dict[str, str]],
    ) -> str:
        outcomes = [item.strip() for item in (research_sections.get("Outcome Hypotheses") or []) if item.strip()]
        if outcomes:
            first = outcomes[0]
            if not _creator_has_leakage(first):
                return first
        if blueprint_rows:
            first = blueprint_rows[0]
            deliverable = str(first.get("deliverable") or "").strip()
            title = str(first.get("title") or "").strip()
            if deliverable and title:
                return f"Learn {title} through practical exercises and build {deliverable} as your first concrete output."
        title = self._creator_public_course_title(topic)
        return f"A practical Amanoba course to build real skill in {title} through guided lessons, application-focused quizzes, and measurable outputs."

    def _creator_public_lesson_title(self, lesson_title: str, fallback: str) -> str:
        candidate = str(lesson_title or "").strip()
        if not candidate or _creator_has_leakage(candidate):
            return str(fallback or "Lesson").strip()
        return candidate

    def _creator_strip_optional_empty_sections(self, text: str) -> str:
        cleaned = str(text or "")
        cleaned = re.sub(
            r"\n## Bibliography \(sources used\)\s*(?:\n(?:\.\.\.|[-*]\s*)\s*)*(?=\n## |\Z)",
            "\n",
            cleaned,
            flags=re.DOTALL,
        )
        cleaned = re.sub(
            r"\n## Read more \(optional\)\s*(?:\n(?:\.\.\.|[-*]\s*)\s*)*(?=\n## |\Z)",
            "\n",
            cleaned,
            flags=re.DOTALL,
        )
        return re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    def _creator_render_public_lesson_content(
        self,
        title: str,
        goal: str,
        deliverable: str,
        lesson_title: str,
        source_rows: list[dict[str, str]],
    ) -> str:
        safe_goal = str(goal or "").strip().rstrip(".")
        safe_title = str(title or lesson_title or "Lesson").strip()
        safe_deliverable = str(deliverable or "a concrete output").strip()
        title_context = safe_title.lower()
        domain_noun = "project"
        decision_noun = "decision"
        if re.search(r"\bagency\b", title_context, flags=re.I):
            domain_noun = "service offer"
            decision_noun = "client-facing decision"
        elif re.search(r"\bpower bi\b|\bdashboard\b|\breport", title_context, flags=re.I):
            domain_noun = "dashboard"
            decision_noun = "reporting decision"
        elif re.search(r"\bsales\b|\bclosing\b|\bproposal\b", title_context, flags=re.I):
            domain_noun = "sales asset"
            decision_noun = "buyer decision"
        goal_sentence = safe_goal or f"produce {safe_deliverable}"
        lines = [
            f"# {safe_title}",
            "",
            "## Learning Goal",
            f"Use this lesson to build a practical first version of {safe_deliverable}. By the end, you should be able to {goal_sentence} in one realistic situation.",
            "",
            "## Who",
            "This lesson is for a beginner operator who needs one clear, usable result instead of a broad theoretical overview.",
            "",
            "## What",
            f"You will create {safe_deliverable} and use it to support one concrete business need.",
            "",
            "## Where",
            "Use this in the real environment where the work will be reviewed, shared, or handed to another person.",
            "",
            "## When",
            "Work on this lesson when you have one concrete use case in front of you and can keep the first version intentionally small.",
            "",
            "## Why It Matters",
            f"A beginner-friendly starting point matters because {safe_title} becomes useful only when one specific business problem is turned into one usable {domain_noun} that supports a real {decision_noun}.",
            "",
            "## How",
            f"Start with one audience, one decision, and one narrowly scoped outcome. Build the smallest version of {safe_deliverable} that would still be useful in practice, then improve only after that first version works.",
            "",
            "## Example",
            f"Imagine you need one working version of {safe_deliverable}. The strongest first move is to choose one audience, one decision, and one narrowly scoped outcome instead of trying to solve the whole problem at once.",
            "",
            "## Guided Exercise",
            f"Choose one realistic beginner use case, define the audience, list the minimum inputs needed, and create the first usable version of {safe_deliverable}. Keep the scope intentionally small and practical.",
            "",
            "## Independent Exercise",
            f"Adapt the same pattern to your own context. Replace the sample use case with a real need and create your own version of {safe_deliverable}.",
            "",
            "## Self-Check",
            f"Check whether your draft is specific, useful, and clearly tied to one real decision. If a stakeholder saw it, would they understand what it is for and what action it supports?",
        ]
        if source_rows:
            lines.extend(["", "## Bibliography (sources used)"])
            for item in source_rows[:5]:
                title_value = str(item.get("title") or "").strip()
                url_value = str(item.get("url") or "").strip()
                if title_value and url_value:
                    lines.append(f"- [{title_value}]({url_value})")
                elif title_value:
                    lines.append(f"- {title_value}")
                elif url_value:
                    lines.append(f"- {url_value}")
        return self._creator_strip_optional_empty_sections("\n".join(lines))

    def _creator_render_public_email_subject(self, title: str, day: int) -> str:
        safe_title = str(title or "Lesson").strip()
        return f"Day {day:02d} — {safe_title}"

    def _creator_render_public_email_body(self, title: str, deliverable: str) -> str:
        safe_title = str(title or "Lesson").strip()
        safe_deliverable = str(deliverable or "a usable output").strip()
        return (
            f"Today you will use {safe_title} to build {safe_deliverable}. "
            "Keep the first version practical, small in scope, and ready for review."
        )

    def _creator_render_public_question_from_row(
        self,
        row: dict[str, str],
        target_language: str,
        question_uuid: str,
    ) -> dict[str, Any]:
        lesson_title = str(row.get("lesson_title") or "").strip() or "Lesson"
        deliverable = str(row.get("deliverable") or "").strip() or lesson_title.lower()
        focus = str(row.get("quiz_focus") or "").strip()
        focus_sentence = re.sub(r"\s+", " ", focus).strip().rstrip(".")
        if not focus_sentence:
            focus_sentence = f"make {deliverable} useful in one real situation"
        question = (
            f"A beginner is building {deliverable} for {lesson_title}. They need a first version they can use in a real situation this week. "
            f"Which next step is strongest if the goal is to {focus_sentence[:1].lower() + focus_sentence[1:] if focus_sentence else focus_sentence}?"
        )
        correct = (
            f"Choose one real buyer problem first. Define the decision {deliverable} must support. Build the smallest version that can be reviewed today."
        )
        options = [
            correct,
            f"Expand {deliverable} to cover multiple audiences first. Delay testing until it tries to solve every use case at once.",
            f"Copy another example into {deliverable} first. Postpone the real buyer problem until after the first draft is finished.",
            f"Polish the presentation of {deliverable} first. Delay the hard decision about audience scope and outcome.",
        ]
        if "metric" in focus.lower():
            options[3] = f"Choose attractive visuals for {deliverable} first. Postpone metric definitions until after the first version is already built."
        elif "pricing" in focus.lower() or "offer" in focus.lower():
            options[2] = f"Copy another agency's pricing or offer structure into {deliverable}. Check the buyer problem only after the first draft exists."
        elif "client" in focus.lower() or "buyer" in focus.lower():
            options[1] = f"Keep {deliverable} broad enough to serve every possible client. Avoid choosing one buyer problem first."
        return {
            "uuid": question_uuid,
            "question": question,
            "options": options,
            "correctIndex": 0,
            "questionType": "application",
            "difficulty": "MEDIUM",
            "category": "Course Specific",
            "hashtags": [f"#{target_language}", "#creator-final", "#application"],
            "isActive": True,
            "language": target_language,
            "lessonTitle": lesson_title,
        }

    def _creator_validate_stage_artifact(self, stage_key: str, content: str) -> tuple[bool, str]:
        normalized = str(content or "").strip()
        if not normalized:
            return False, "The generated artifact is empty."
        if self._creator_is_placeholder_artifact(stage_key, normalized):
            return False, "The generated artifact is still only a placeholder."
        if stage_key == "research":
            sections = self._creator_parse_research_sections(normalized)
            required = [
                "Learner Problem",
                "Audience",
                "Outcomes",
                "Scope Boundaries",
                "Evidence Needs",
            ]
            missing = [heading for heading in required if not sections.get(heading)]
            if missing:
                return False, f"Research must include usable sections for: {', '.join(missing)}."
            if normalized.count("# Research Artifact Draft") > 1:
                return False, "Research repeats the same draft block instead of producing one clean brief."
            keywords = self._topic_keywords(" ".join(sections.get("Learner Problem", []) + sections.get("Outcomes", [])))
            if not keywords and len(normalized) < 600:
                return False, "Research is too thin and generic to drive the next stage."
        if stage_key == "blueprint":
            rows = self._creator_parse_blueprint_days(normalized)
            if len(rows) < 30:
                return False, f"Blueprint must contain 30 day rows in the required format, but only {len(rows)} were parsed."
            short_topic = self._creator_topic_short_title(re.search(r"## Working Title\n(.+?)\n", normalized, flags=re.DOTALL).group(1).strip() if re.search(r"## Working Title\n(.+?)\n", normalized, flags=re.DOTALL) else "")
            generic_deliverables = 0
            repetitive_titles = 0
            for row in rows:
                title = str(row.get("title") or "").strip()
                deliverable = str(row.get("deliverable") or "").strip().lower()
                if short_topic and title.lower().startswith(short_topic.lower() + ":"):
                    repetitive_titles += 1
                if re.search(r"\bdeliverable\b.*\bday\b", deliverable):
                    generic_deliverables += 1
            if repetitive_titles > 10:
                return False, "Blueprint still repeats the course title too heavily in daily lesson titles."
            if generic_deliverables > 3:
                return False, "Blueprint still contains generic day-based deliverables instead of concrete outputs."
        elif stage_key == "lesson_generation":
            rows = self._creator_parse_lesson_batch_rows(normalized)
            if len(rows) < 30:
                return False, f"Lesson generation must contain 30 lesson draft rows in the required format, but only {len(rows)} were parsed."
            weak_rows = 0
            for row in rows:
                lesson_body = str(row.get("lesson_body") or "")
                email_body = str(row.get("email_body") or "")
                if lesson_body.count("## ") < 4 or len(email_body.strip()) < 40:
                    weak_rows += 1
            if weak_rows > 2:
                return False, "Lesson generation still contains too many weak lesson or email drafts."
        elif stage_key == "quiz_generation":
            rows = self._creator_parse_quiz_batch_rows(normalized)
            if len(rows) < 30:
                return False, f"Quiz generation must contain structured quiz rows in the required format, but only {len(rows)} were parsed."
            day_counts: dict[str, int] = {}
            weak_rows = 0
            for row in rows:
                day = str(row.get("day") or "")
                day_counts[day] = day_counts.get(day, 0) + 1
                stem = str(row.get("stem_focus") or "").strip()
                distractors = str(row.get("distractor_themes") or "").strip().lower()
                if len(stem) < 40 or "generic action" in distractors and "theory without execution" in distractors:
                    weak_rows += 1
            if len(day_counts) < 30 or any(count < 7 for count in day_counts.values()):
                return False, "Quiz generation must contain 7 usable question drafts for each of the 30 days."
            if weak_rows > 10:
                return False, "Quiz generation still contains too many weak or generic question intents."
        return True, ""

    def _creator_structured_artifacts(self, detail: dict[str, Any]) -> dict[str, Any]:
        payload = dict(detail.get("payload") or {})
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        structured: dict[str, Any] = {}
        for stage_key, artifact in stage_artifacts.items():
            content = str((artifact or {}).get("content") or "").strip()
            if not content:
                structured[stage_key] = {"ready": False, "count": 0, "items": [], "reason": "empty"}
                continue
            if self._creator_is_placeholder_artifact(stage_key, content):
                structured[stage_key] = {"ready": False, "count": 0, "items": [], "reason": "placeholder"}
                continue
            if stage_key == "research":
                sections = self._creator_parse_research_sections(content)
                items = [{"heading": heading, "rows": rows} for heading, rows in sections.items()]
                structured[stage_key] = {
                    "ready": bool(items),
                    "count": len(items),
                    "items": items,
                    "reason": "" if items else "unstructured",
                }
            elif stage_key == "blueprint":
                items = self._creator_parse_blueprint_days(content)
                structured[stage_key] = {
                    "ready": len(items) >= 30,
                    "count": len(items),
                    "items": items,
                    "reason": "" if len(items) >= 30 else "missing-days",
                }
            elif stage_key == "lesson_generation":
                items = self._creator_parse_lesson_batch_rows(content)
                structured[stage_key] = {
                    "ready": len(items) >= 30,
                    "count": len(items),
                    "items": items,
                    "reason": "" if len(items) >= 30 else "missing-lessons",
                }
            elif stage_key == "quiz_generation":
                items = self._creator_parse_quiz_batch_rows(content)
                day_count = len({str(item.get("day") or "") for item in items if str(item.get("day") or "")})
                structured[stage_key] = {
                    "ready": len(items) >= 30 and day_count >= 30,
                    "count": len(items),
                    "items": items,
                    "dayCount": day_count,
                    "reason": "" if len(items) >= 30 and day_count >= 30 else "missing-quizzes",
                }
            else:
                structured[stage_key] = {"ready": True, "count": 1, "items": [], "reason": ""}
        return structured

    def _creator_handoff_status(self, detail: dict[str, Any]) -> dict[str, Any]:
        payload = dict(detail.get("payload") or {})
        structured = self._creator_structured_artifacts(detail)
        blueprint = dict(structured.get("blueprint") or {})
        lessons = dict(structured.get("lesson_generation") or {})
        quizzes = dict(structured.get("quiz_generation") or {})
        missing: list[str] = []
        if not bool(blueprint.get("ready")):
            missing.append("blueprint")
        if not bool(lessons.get("ready")):
            missing.append("lesson_generation")
        if not bool(quizzes.get("ready")):
            missing.append("quiz_generation")
        qc_status = dict(payload.get("qcStatus") or {})
        return {
            "readyForQc": not missing,
            "missingStages": missing,
            "blueprintDays": int(blueprint.get("count") or 0),
            "lessonDrafts": int(lessons.get("count") or 0),
            "quizDrafts": int(quizzes.get("count") or 0),
            "qcTasks": int(qc_status.get("total") or 0),
            "status": "ready" if not missing else f"missing:{','.join(missing)}",
        }

    def _creator_is_placeholder_artifact(self, stage_key: str, content: str) -> bool:
        normalized = str(content or "").strip()
        if not normalized:
            return True
        if stage_key == "blueprint":
            return "## Course Structure" in normalized and "### Day 01 —" not in normalized
        if stage_key == "lesson_generation":
            return "# Lesson Generation Workbench" in normalized and "### Day 01 Lesson Draft" not in normalized
        if stage_key == "quiz_generation":
            return "# Quiz Generation Workbench" in normalized and "### Day 01 Quiz Draft" not in normalized
        return False

    def _creator_assert_stage_prerequisites(self, stage_key: str, stages: list[dict[str, Any]]) -> None:
        requirements = {
            "blueprint": ["research"],
            "lesson_generation": ["blueprint"],
            "quiz_generation": ["lesson_generation"],
            "qc_review": ["quiz_generation"],
            "draft_to_live": ["qc_review"],
        }
        missing = [key for key in requirements.get(stage_key) or [] if not self._creator_stage_is_completed(stages, key)]
        if missing:
            label = ", ".join(self._creator_stage_label(key) for key in missing)
            raise ValueError(f"Approve {label} before generating {self._creator_stage_label(stage_key)}.")

    def _creator_stage_is_completed(self, stages: list[dict[str, Any]], key: str) -> bool:
        for stage in stages:
            if str(stage.get("key") or "") == key:
                return str(stage.get("status") or "") == "completed"
        return False

    def _creator_stage_label(self, key: str) -> str:
        return str(key or "").replace("_", " ").title()

    def _creator_next_checkpoint(self, stages: list[dict[str, Any]], run_status: str) -> str:
        if run_status == "ready-for-live":
            return "Draft To Live approval"
        for stage in stages:
            if str(stage.get("status") or "") == "active":
                return f"{self._creator_stage_label(str(stage.get('key') or 'stage'))} approval"
        return "No open checkpoint."

    def _creator_refresh_draft_summary(self, detail: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
        summary = dict(payload.get("draftSummary") or detail.get("draftSummary") or {})
        summary["courseTitleCandidate"] = summary.get("courseTitleCandidate") or detail.get("topic") or ""
        summary["targetLanguage"] = summary.get("targetLanguage") or detail.get("targetLanguage") or ""
        summary["researchMode"] = summary.get("researchMode") or detail.get("researchMode") or ""
        summary["nextCheckpoint"] = self._creator_next_checkpoint(
            list(payload.get("stages") or detail.get("stages") or []),
            str(detail.get("status") or "active"),
        )
        artifact_summaries = self._creator_artifact_summaries(dict(payload.get("stageArtifacts") or {}))
        blueprint_summary = artifact_summaries.get("blueprint") or {}
        lesson_summary = artifact_summaries.get("lesson_generation") or {}
        if blueprint_summary.get("headline"):
            summary["blueprintCoverage"] = blueprint_summary["headline"]
        if lesson_summary.get("headline"):
            summary["lessonBatchCoverage"] = lesson_summary["headline"]
        qc_status = dict(payload.get("qcStatus") or {})
        if qc_status:
            summary["qcProgress"] = (
                f"{int(qc_status.get('completed') or 0)}/{int(qc_status.get('total') or 0)} completed"
                f" · failed {int(qc_status.get('failed') or 0)}"
                f" · quarantined {int(qc_status.get('quarantined') or 0)}"
            )
        promotion = dict(payload.get("promotion") or {})
        if promotion:
            summary["draftPackageStatus"] = str(promotion.get("status") or "draft-package-generated")
            summary["draftPackagePath"] = str(promotion.get("packagePath") or "")
        import_status = dict(payload.get("importStatus") or {})
        if import_status:
            summary["amanobaDraftImportStatus"] = str(import_status.get("status") or "draft-imported")
            summary["amanobaDraftCourseId"] = str(import_status.get("courseId") or "")
        publish_status = dict(payload.get("publishStatus") or {})
        if publish_status:
            summary["amanobaLiveStatus"] = str(publish_status.get("status") or "published-live")
            summary["amanobaLiveCourseId"] = str(publish_status.get("courseId") or "")
        handoff_status = dict(payload.get("handoffStatus") or {})
        if handoff_status:
            if bool(handoff_status.get("readyForQc")):
                summary["handoffReadiness"] = (
                    f"QC handoff ready · {int(handoff_status.get('lessonDrafts') or 0)} lesson drafts"
                    f" · {int(handoff_status.get('quizDrafts') or 0)} quiz drafts"
                )
            else:
                missing = ", ".join(self._creator_stage_label(item) for item in list(handoff_status.get("missingStages") or []))
                summary["handoffReadiness"] = f"QC handoff blocked · missing {missing or 'required stages'}"
        rollback_status = dict(payload.get("rollbackStatus") or {})
        if rollback_status:
            summary["amanobaRollbackStatus"] = str(rollback_status.get("status") or "rolled-back-to-draft")
        delete_status = dict(payload.get("deleteStatus") or {})
        if delete_status:
            summary["amanobaDeleteStatus"] = str(delete_status.get("status") or "import-deleted")
        return summary

    def _enrich_creator_run(self, detail: dict[str, Any]) -> dict[str, Any]:
        payload = dict(detail.get("payload") or {})
        payload["structuredArtifacts"] = self._creator_structured_artifacts({**detail, "payload": payload})
        qc_plan = dict(payload.get("qcPlan") or {})
        if qc_plan:
            qc_status = self._creator_qc_status(qc_plan)
            payload["qcStatus"] = qc_status
            stage_artifacts = dict(payload.get("stageArtifacts") or {})
            qc_artifact = dict(stage_artifacts.get("qc_review") or {})
            qc_artifact["content"] = self._creator_qc_review_markdown(qc_plan, qc_status, payload)
            qc_artifact["updatedAt"] = qc_status.get("generatedAt")
            stage_artifacts["qc_review"] = qc_artifact
            payload["stageArtifacts"] = stage_artifacts
        payload["handoffStatus"] = self._creator_handoff_status({**detail, "payload": payload})
        enriched = dict(detail)
        enriched["payload"] = payload
        enriched["artifactSummaries"] = self._creator_artifact_summaries(dict(payload.get("stageArtifacts") or {}))
        enriched["draftSummary"] = self._creator_refresh_draft_summary(enriched, payload)
        return enriched

    def _creator_qc_status(self, qc_plan: dict[str, Any]) -> dict[str, Any]:
        task_keys = [str(item) for item in (qc_plan.get("taskKeys") or []) if str(item)]
        summaries = self.state.task_summaries_by_keys(task_keys)
        counts = {
            "queued": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "quarantined": 0,
            "archived": 0,
        }
        for summary in summaries:
            display_status = str(summary.get("displayStatus") or summary.get("status") or "")
            if display_status == "retry-failed":
                counts["failed"] += 1
            elif display_status in counts:
                counts[display_status] += 1
            elif str(summary.get("status") or "") == "pending":
                counts["queued"] += 1
        recent_completed = [
            str(item.get("humanTitle") or item.get("details", {}).get("displayTitle") or item.get("taskKey") or "")
            for item in summaries
            if str(item.get("status") or "") == "completed"
        ][:5]
        recent_failed = [
            str(item.get("humanTitle") or item.get("details", {}).get("displayTitle") or item.get("taskKey") or "")
            for item in summaries
            if str(item.get("displayStatus") or "") in {"retry-failed", "failed", "quarantined"}
        ][:5]
        return {
            "generatedAt": utc_now(),
            "total": len(task_keys),
            "lessons": int(qc_plan.get("lessonCount") or 0),
            "questions": int(qc_plan.get("questionCount") or 0),
            **counts,
            "recentCompleted": recent_completed,
            "recentFailed": recent_failed,
        }

    def _creator_qc_review_markdown(self, qc_plan: dict[str, Any], qc_status: dict[str, Any], payload: dict[str, Any]) -> str:
        topic = str(payload.get("draftSummary", {}).get("courseTitleCandidate") or "Draft")
        lines = [
            "# QC Review",
            "",
            f"## Topic\n{topic}",
            "",
            "## Queue Summary",
            f"- Total QC tasks: {int(qc_status.get('total') or 0)}",
            f"- Lesson tasks: {int(qc_status.get('lessons') or 0)}",
            f"- Question tasks: {int(qc_status.get('questions') or 0)}",
            f"- Queued: {int(qc_status.get('queued') or 0)}",
            f"- Running: {int(qc_status.get('running') or 0)}",
            f"- Completed: {int(qc_status.get('completed') or 0)}",
            f"- Failed: {int(qc_status.get('failed') or 0)}",
            f"- Quarantined: {int(qc_status.get('quarantined') or 0)}",
            "",
            "## Exit Condition",
            "All injected creator QC tasks must complete successfully before QC Review can be accepted.",
        ]
        if qc_status.get("recentCompleted"):
            lines.extend(["", "## Recent Completed Drafts"])
            lines.extend(f"- {item}" for item in list(qc_status.get("recentCompleted") or []))
        if qc_status.get("recentFailed"):
            lines.extend(["", "## Human Attention Needed"])
            lines.extend(f"- {item}" for item in list(qc_status.get("recentFailed") or []))
        return "\n".join(lines).strip() + "\n"

    def _creator_build_draft_to_live_summary(self, detail: dict[str, Any]) -> str:
        payload = dict(detail.get("payload") or {})
        qc_status = dict(payload.get("qcStatus") or {})
        promotion = dict(payload.get("promotion") or {})
        import_status = dict(payload.get("importStatus") or {})
        publish_status = dict(payload.get("publishStatus") or {})
        rollback_status = dict(payload.get("rollbackStatus") or {})
        delete_status = dict(payload.get("deleteStatus") or {})
        return (
            "# Draft To Live Decision\n\n"
            f"## Topic\n{str(detail.get('topic') or '')}\n\n"
            "## Final Checks\n"
            f"- QC completed: {int(qc_status.get('completed') or 0)} / {int(qc_status.get('total') or 0)}\n"
            f"- Failed tasks: {int(qc_status.get('failed') or 0)}\n"
            f"- Quarantined tasks: {int(qc_status.get('quarantined') or 0)}\n"
            f"- Draft package exported: {str(promotion.get('packagePath') or 'not yet generated')}\n"
            f"- Draft imported into Amanoba: {str(import_status.get('courseId') or 'not yet imported')}\n"
            f"- Live publish status: {str(publish_status.get('status') or 'not yet published')}\n"
            f"- Rollback status: {str(rollback_status.get('status') or 'not used')}\n"
            f"- Delete-import status: {str(delete_status.get('status') or 'not used')}\n"
            "- Human signoff still required before any live promotion.\n"
        )

    def _creator_enqueue_qc_review(self, detail: dict[str, Any]) -> dict[str, Any]:
        payload = dict(detail.get("payload") or {})
        structured = self._creator_structured_artifacts(detail)
        lesson_rows = list((structured.get("lesson_generation") or {}).get("items") or [])
        quiz_rows = list((structured.get("quiz_generation") or {}).get("items") or [])
        source_rows = list(payload.get("sourcePack") or [])
        if not lesson_rows:
            raise ValueError("Approved lesson generation artifact does not contain lesson drafts to inject into QC.")
        run_id = str(detail.get("runId") or "")
        topic = str(detail.get("topic") or "")
        target_language = str(detail.get("targetLanguage") or "")
        task_keys: list[str] = []
        for index, row in enumerate(lesson_rows):
            day = str(row.get("day") or f"{index + 1:02d}")
            lesson_id = f"day-{day}"
            before = {
                "title": row.get("lesson_title") or f"{topic} day {day}",
                "content": row.get("lesson_body") or "",
                "emailSubject": row.get("email_subject") or f"{topic} day {day}",
                "emailBody": row.get("email_body") or "",
            }
            context = {
                "previousLesson": {"title": lesson_rows[index - 1].get("lesson_title")} if index > 0 else {},
                "nextLesson": {"title": lesson_rows[index + 1].get("lesson_title")} if index + 1 < len(lesson_rows) else {},
            }
            audit = audit_lesson(before, target_language)
            task_key = f"creator-lesson::{run_id}::{day}"
            self.state.upsert_task(
                task_key=task_key,
                kind="creator_lesson",
                package_path=f"creator::{run_id}",
                course_id=run_id,
                language=target_language,
                lesson_id=lesson_id,
                question_uuid=None,
                question_index=None,
                source_hash=sha256_json({"before": before, "context": context}),
                details={
                    "origin": "creator",
                    "runId": run_id,
                    "creatorStage": "qc_review",
                    "creatorDay": day,
                    "before": before,
                    "lessonRow": row,
                    "sourceRows": source_rows,
                    "context": context,
                    "displayTitle": str(before.get("title") or lesson_id),
                    "humanCourseName": topic,
                    "humanDayLabel": f"Day {int(day)}",
                    "humanLessonTitle": str(before.get("title") or lesson_id),
                    "errors": audit.errors,
                    "warnings": audit.warnings,
                    "judgement": confidence_for_validation("lesson", audit.errors, audit.warnings),
                },
                priority=CREATOR_QC_PRIORITY,
            )
            task_keys.append(task_key)
        for row in quiz_rows:
            day = str(row.get("day") or "00")
            question_number = str(row.get("question_number") or "0")
            question_uuid = f"{run_id}-d{day}-q{question_number}"
            before = self._creator_seed_question_from_quiz_row(row, target_language, question_uuid)
            validation = validate_question(before, target_language)
            task_key = f"creator-question::{run_id}::{day}::{question_number}"
            self.state.upsert_task(
                task_key=task_key,
                kind="creator_question",
                package_path=f"creator::{run_id}",
                course_id=run_id,
                language=target_language,
                lesson_id=f"day-{day}",
                question_uuid=question_uuid,
                question_index=int(question_number) - 1 if question_number.isdigit() else None,
                source_hash=sha256_json({"before": before}),
                details={
                    "origin": "creator",
                    "runId": run_id,
                    "creatorStage": "qc_review",
                    "creatorDay": day,
                    "before": before,
                    "quizRow": row,
                    "displayTitle": str(before.get("question") or question_uuid),
                    "humanCourseName": topic,
                    "humanDayLabel": f"Day {int(day)}",
                    "humanLessonTitle": str(row.get("lesson_title") or f"Day {day}"),
                    "errors": validation.errors,
                    "warnings": validation.warnings,
                    "judgement": confidence_for_validation("question", validation.errors, validation.warnings),
                },
                priority=CREATOR_QC_PRIORITY,
            )
            task_keys.append(task_key)
        plan = {
            "taskKeys": task_keys,
            "lessonCount": len(lesson_rows),
            "questionCount": len(quiz_rows),
            "injectedAt": utc_now(),
        }
        content = self._creator_qc_review_markdown(plan, self._creator_qc_status(plan), payload)
        return {"plan": plan, "content": content}

    def _creator_slug(self, value: str) -> str:
        compact = re.sub(r"[^A-Za-z0-9]+", "_", str(value or "").strip().upper()).strip("_")
        return compact or "COURSE"

    def _creator_parse_research_sections(self, markdown: str) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {}
        if not markdown.strip():
            return sections
        for match in re.finditer(r"##\s+(.+?)\n(.*?)(?=\n##\s+|\Z)", markdown, flags=re.DOTALL):
            heading = str(match.group(1) or "").strip()
            body = str(match.group(2) or "")
            rows: list[str] = []
            for line in body.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                stripped = re.sub(r"^[-*]\s+", "", stripped)
                if stripped:
                    rows.append(stripped)
            sections[heading] = rows
        return sections

    def _creator_clean_public_rows(self, rows: list[str], topic: str, limit: int = 4) -> list[str]:
        cleaned: list[str] = []
        keywords = self._topic_keywords(topic)
        for row in rows:
            text = str(row or "").strip()
            lowered = text.lower()
            if not text or _creator_has_leakage(text):
                continue
            if text.startswith("### ") or text.endswith(":"):
                continue
            if "what specific" in lowered or "what decisions" in lowered or "what topics" in lowered:
                continue
            if keywords and not any(keyword in lowered for keyword in keywords):
                generic_ok = any(
                    phrase in lowered
                    for phrase in ("learner", "dashboard", "report", "analysis", "data", "decision", "metric", "visual")
                )
                if not generic_ok:
                    continue
            cleaned.append(text)
        return cleaned[:limit]

    def _creator_build_course_package(self, detail: dict[str, Any]) -> dict[str, Any]:
        payload = dict(detail.get("payload") or {})
        stage_artifacts = dict(payload.get("stageArtifacts") or {})
        qc_payload = dict(payload.get("qcPayload") or {})
        blueprint_rows = self._creator_parse_blueprint_days(str((stage_artifacts.get("blueprint") or {}).get("content") or ""))
        lesson_rows = self._creator_parse_lesson_batch_rows(str((stage_artifacts.get("lesson_generation") or {}).get("content") or ""))
        quiz_rows = self._creator_parse_quiz_batch_rows(str((stage_artifacts.get("quiz_generation") or {}).get("content") or ""))
        lessons_by_key = dict(qc_payload.get("lessons") or {})
        questions_by_key = dict(qc_payload.get("questions") or {})
        if not blueprint_rows or not lesson_rows:
            raise ValueError("Blueprint and lesson generation artifacts must exist before building a draft package.")
        target_language = str(detail.get("targetLanguage") or "en").strip().lower()
        topic = str(detail.get("topic") or "Untitled course").strip()
        public_title = self._creator_public_course_title(topic)
        course_id_base = self._creator_slug(topic)
        course_id = f"{course_id_base}_{target_language.upper()}"
        research_markdown = str((stage_artifacts.get("research") or {}).get("content") or "")
        research_sections = self._creator_parse_research_sections(research_markdown)
        source_pack = list(payload.get("sourcePack") or [])
        source_rows = [
            {"title": str(item.get("title") or "").strip(), "url": str(item.get("url") or "").strip()}
            for item in source_pack
            if str(item.get("title") or "").strip() or str(item.get("url") or "").strip()
        ]
        blueprint_map = {f"{int(row['day']):02d}": row for row in blueprint_rows if row.get("day")}
        lesson_map = {f"{int(row['day']):02d}": row for row in lesson_rows if row.get("day")}
        quiz_rows_by_day: dict[str, list[dict[str, str]]] = {}
        for row in quiz_rows:
            day = f"{int(str(row.get('day') or '0') or '0'):02d}" if str(row.get("day") or "").strip().isdigit() else str(row.get("day") or "").strip()
            if not day:
                continue
            quiz_rows_by_day.setdefault(day, []).append(row)
        package_lessons: list[dict[str, Any]] = []
        canonical_lessons: list[dict[str, Any]] = []
        for day in range(1, 31):
            day_key = f"{day:02d}"
            blueprint = blueprint_map.get(day_key) or {}
            lesson_row = lesson_map.get(day_key) or {}
            qc_lesson = lessons_by_key.get(f"day-{day_key}") or {}
            fallback_title = str(blueprint.get("title") or lesson_row.get("lesson_title") or f"Day {day_key}")
            lesson_title = self._creator_public_lesson_title(str((qc_lesson or {}).get("title") or lesson_row.get("lesson_title") or blueprint.get("title") or fallback_title), fallback_title)
            rendered_content = self._creator_render_public_lesson_content(
                lesson_title,
                str(blueprint.get("goal") or lesson_row.get("goal") or ""),
                str(blueprint.get("deliverable") or lesson_row.get("deliverable") or ""),
                str(lesson_row.get("lesson_title") or lesson_title),
                source_rows,
            )
            rendered_email_subject = self._creator_render_public_email_subject(lesson_title, day)
            rendered_email_body = self._creator_render_public_email_body(
                lesson_title,
                str(blueprint.get("deliverable") or lesson_row.get("deliverable") or ""),
            )
            qc_lesson_candidate = {
                "title": str((qc_lesson or {}).get("title") or ""),
                "content": str((qc_lesson or {}).get("content") or ""),
                "emailSubject": str((qc_lesson or {}).get("emailSubject") or ""),
                "emailBody": str((qc_lesson or {}).get("emailBody") or ""),
            }
            qc_lesson_audit = audit_lesson(qc_lesson_candidate, target_language) if any(qc_lesson_candidate.values()) else None
            use_qc_lesson = bool(
                qc_lesson_audit
                and qc_lesson_audit.is_valid
                and not any(_creator_has_leakage(value) for value in qc_lesson_candidate.values())
            )
            lesson_content = str(qc_lesson_candidate.get("content") or rendered_content) if use_qc_lesson else rendered_content
            email_subject = str(qc_lesson_candidate.get("emailSubject") or rendered_email_subject) if use_qc_lesson else rendered_email_subject
            email_body = str(qc_lesson_candidate.get("emailBody") or rendered_email_body) if use_qc_lesson else rendered_email_body
            quiz_questions: list[dict[str, Any]] = []
            for row in list(quiz_rows_by_day.get(day_key) or []):
                question_number = str(row.get("question_number") or "0").strip()
                question_uuid = f"{detail.get('runId')}-d{day_key}-q{question_number}"
                qc_question = questions_by_key.get(question_uuid) or {}
                qc_question_candidate = dict(qc_question) if isinstance(qc_question, dict) else {}
                qc_question_audit = validate_question(qc_question_candidate, target_language) if qc_question_candidate else None
                use_qc_question = bool(
                    qc_question_audit
                    and qc_question_audit.is_valid
                    and not _creator_has_leakage(str(qc_question_candidate.get("question") or ""))
                    and not any(_creator_has_leakage(str(option or "")) for option in list(qc_question_candidate.get("options") or []))
                )
                quiz_questions.append(
                    qc_question_candidate if use_qc_question else self._creator_render_public_question_from_row(row, target_language, question_uuid)
                )
            package_lessons.append(
                {
                    "lessonId": f"{course_id}_DAY_{day_key}",
                    "dayNumber": day,
                    "language": target_language,
                    "title": lesson_title,
                    "content": lesson_content,
                    "emailSubject": email_subject,
                    "emailBody": email_body,
                    "quizConfig": {
                        "enabled": True,
                        "successThreshold": 80,
                        "questionCount": len(quiz_questions) or 7,
                        "poolSize": len(quiz_questions) or 7,
                        "required": True,
                    },
                    "unlockConditions": {},
                    "pointsReward": 10,
                    "xpReward": 10,
                    "isActive": False,
                    "displayOrder": day,
                    "metadata": {"creatorRunId": str(detail.get("runId") or "")},
                    "quizQuestions": quiz_questions,
                }
            )
            canonical_lessons.append(
                {
                    "dayNumber": day,
                    "canonicalTitle": str(blueprint.get("title") or lesson_title),
                    "objective": str(blueprint.get("goal") or lesson_row.get("goal") or ""),
                    "keyConcepts": [str(blueprint.get("module") or "").strip(), str(blueprint.get("quiz_focus") or "").strip()],
                    "exercise": str(lesson_row.get("guided_focus") or blueprint.get("deliverable") or ""),
                    "deliverable": str(blueprint.get("deliverable") or lesson_row.get("deliverable") or ""),
                    "sources": source_rows[:5],
                }
            )
        publish_title = str(research_sections.get("Core Learner Problem", [public_title])[0] if research_sections.get("Core Learner Problem") else public_title)
        if _creator_has_leakage(publish_title):
            publish_title = public_title
        description = self._creator_public_course_description(public_title, research_sections, blueprint_rows)
        clean_audience = self._creator_clean_public_rows(list(research_sections.get("Primary Audience Hypotheses") or []), public_title, 3)
        clean_outcomes = self._creator_clean_public_rows(list(research_sections.get("Outcome Hypotheses") or []), public_title, 4)
        clean_scope = self._creator_clean_public_rows(list(research_sections.get("Scope Boundaries") or []), public_title, 3)
        clean_non_goals = clean_scope[1:4] if len(clean_scope) > 1 else []
        course_idea_summary = (
            f"# {public_title}\n\n"
            f"## Public Summary\n{description}\n\n"
            "## Audience\n"
            + ("\n".join(f"- {item}" for item in clean_audience) if clean_audience else "- Beginner learners who need practical results quickly.")
            + "\n\n## Outcomes\n"
            + ("\n".join(f"- {item}" for item in clean_outcomes) if clean_outcomes else "- Build one usable reporting output from a real beginner use case.")
            + "\n"
        )
        canonical_json = {
            "schemaVersion": "1.0",
            "courseIdBase": course_id_base,
            "courseName": public_title,
            "version": utc_now()[:10],
            "language": target_language,
            "metadata": {
                "publish": {
                    "tagline": publish_title,
                    "publicDescription": description,
                    "whoItsFor": clean_audience,
                    "prerequisites": [],
                    "whatYouShip": [str(item.get("deliverable") or "") for item in canonical_lessons[:6] if str(item.get("deliverable") or "").strip()],
                    "useAndShareNote": "Draft package exported from the local sovereign creator workflow.",
                    "licenseNote": "Draft creator package. Review before any live promotion.",
                }
            },
            "intent": {
                "oneSentence": description,
                "outcomes": clean_outcomes,
                "nonGoals": clean_non_goals,
            },
            "qualityGates": {
                "lessonLengthMinutes": [20, 30],
                "quizQuestions": 7,
                "applicationMinimum": 5,
                "criticalMinimum": 2,
                "recallAllowed": False,
            },
            "concepts": [str(item.get("module") or "").strip() for item in blueprint_rows[:8] if str(item.get("module") or "").strip()],
            "procedures": (research_sections.get("Scope Boundaries") or [])[:3],
            "assessmentBlueprint": {
                "midCourse": {
                    "day": 15,
                    "deliverable": str(canonical_lessons[14].get("deliverable") or "") if len(canonical_lessons) >= 15 else "",
                    "evaluation": "Mid-course draft review",
                },
                "final": {
                    "day": 30,
                    "deliverable": str(canonical_lessons[-1].get("deliverable") or "") if canonical_lessons else "",
                    "evaluation": "Final creator QC review",
                },
            },
            "lessons": canonical_lessons,
        }
        ccs_md = (
            f"# {public_title}\n\n"
            f"Language: {target_language}\n\n"
            "## 30-Day Architecture\n\n"
            + "\n".join(
                f"- Day {int(row['day']):02d}: {row.get('title') or ''} — {row.get('goal') or ''}"
                for row in blueprint_rows
            )
            + "\n"
        )
        return {
            "packageVersion": "2.0",
            "exportedAt": utc_now(),
            "exportedBy": self.config.live_actor,
            "course": {
                "courseId": course_id,
                "name": public_title,
                "description": description,
                "language": target_language,
                "durationDays": 30,
                "isActive": False,
                "requiresPremium": False,
                "ccsId": course_id_base,
                "discussionEnabled": True,
                "leaderboardEnabled": True,
                "studyGroupsEnabled": False,
                "quizMaxWrongAllowed": 2,
                "metadata": {
                    "creatorRunId": str(detail.get("runId") or ""),
                    "creatorWorkflow": "sovereign-course-creator",
                    "draftOnly": True,
                },
            },
            "lessons": package_lessons,
            "canonicalSpec": {
                "json": canonical_json,
                "ccsMd": ccs_md,
            },
            "courseIdea": course_idea_summary,
        }

    def _creator_build_blueprint_seed(
        self,
        topic: str,
        target_language: str,
        research_artifact: str,
        source_pack: list[dict[str, str]],
    ) -> str:
        audience = self._creator_filter_blueprint_bullets(self._creator_extract_bullets(research_artifact, "Primary Audience Hypotheses", 3), topic)
        outcomes = self._creator_filter_blueprint_bullets(self._creator_extract_bullets(research_artifact, "Outcome Hypotheses", 4), topic)
        scope = self._creator_filter_blueprint_bullets(self._creator_extract_bullets(research_artifact, "Scope Boundaries", 3), topic)
        risks = self._creator_filter_blueprint_bullets(self._creator_extract_bullets(research_artifact, "Risks To Prevent", 4), topic)
        source_titles = [str(item.get("title") or item.get("url") or "").strip() for item in source_pack[:5] if str(item.get("title") or item.get("url") or "").strip()]
        modules = [
            "Foundations and context",
            "Mental models and diagnosis",
            "Workflow design and practice",
            "Scenarios, decisions, and feedback",
            "Systems, quality, and scale",
            "Integration, capstone, and transfer",
        ]
        day_entries: list[str] = []
        for day in range(1, 31):
            module_index = min((day - 1) // 5, len(modules) - 1)
            title = self._creator_day_title(topic, day)
            outcome = outcomes[(day - 1) % len(outcomes)] if outcomes else f"Apply {topic} in a practical context."
            deliverable = self._creator_day_deliverable(topic, day)
            quiz_focus = self._creator_day_quiz_focus(day, topic)
            day_entries.append(
                f"### Day {day:02d} — {title}\n"
                f"- Module: {modules[module_index]}\n"
                f"- Goal: {outcome}\n"
                f"- Deliverable: {deliverable}\n"
                f"- Quiz focus: {quiz_focus}\n"
            )
        source_section = "\n".join(f"- {item}" for item in source_titles) or "- No external research titles captured yet."
        return (
            f"# Course Blueprint\n\n"
            f"## Working Title\n{topic}\n\n"
            f"## Language\n{target_language}\n\n"
            f"## Course Promise\n"
            f"This 30-day course turns '{topic}' into a practical operating skill with repeatable exercises, measurable outputs, and application-first quiz checks.\n\n"
            f"## Audience Signals\n"
            + ("\n".join(f"- {item}" for item in audience) if audience else "- Audience still needs refinement from the approved research brief.")
            + "\n\n## Outcome Signals\n"
            + ("\n".join(f"- {item}" for item in outcomes) if outcomes else f"- Learners should be able to apply {topic} in real work or life contexts.")
            + "\n\n## Scope Boundaries\n"
            + ("\n".join(f"- {item}" for item in scope) if scope else "- Scope boundaries still need confirmation from the approved research brief.")
            + "\n\n## Quality Risks To Guard Against\n"
            + ("\n".join(f"- {item}" for item in risks) if risks else "- Mixed language output\n- Generic lesson titles\n- Recall-only quizzes")
            + "\n\n## Source Signals Used\n"
            + source_section
            + "\n\n## 30-Day Architecture\n\n"
            + "\n".join(day_entries)
            + "\n## Lesson Contract\n"
            + "- Every day must produce a named deliverable.\n"
            + "- Every lesson must include guided exercise, independent exercise, and self-check.\n"
            + "- Every lesson must stay in the target language only.\n\n"
            + "## Quiz Contract\n"
            + "- Every day should have application-first quiz checks.\n"
            + "- Distractors must be plausible.\n"
            + "- Questions must be standalone and answerable without lesson context.\n"
        )

    def _creator_filter_blueprint_bullets(self, bullets: list[str], topic: str) -> list[str]:
        filtered: list[str] = []
        keywords = self._topic_keywords(topic)
        for bullet in bullets:
            clean = str(bullet or "").strip()
            if not clean:
                continue
            lower = clean.lower()
            if "http://" in lower or "https://" in lower or "domain=" in lower or "wikipedia" in lower:
                continue
            if clean.startswith("Source:") or clean.startswith("Title:"):
                continue
            if keywords and not any(keyword in lower for keyword in keywords):
                generic_ok = any(
                    phrase in lower
                    for phrase in (
                        "learner",
                        "learners",
                        "outcome",
                        "scope",
                        "risk",
                        "quiz",
                        "lesson",
                        "dashboard",
                        "report",
                        "analysis",
                        "data",
                        "business",
                        "visual",
                    )
                )
                if not generic_ok:
                    continue
            filtered.append(clean)
        return filtered[:4]

    def _creator_build_lesson_batch_seed(
        self,
        topic: str,
        target_language: str,
        blueprint_artifact: str,
    ) -> str:
        day_rows = self._creator_parse_blueprint_days(blueprint_artifact)
        if not day_rows:
            return (
                f"# Lesson Generation Batch\n\n"
                f"## Topic\n{topic}\n\n"
                f"## Language\n{target_language}\n\n"
                f"Blueprint parsing did not find day rows yet. Confirm the blueprint first, then regenerate this stage.\n"
            )
        pack = self._creator_copy_pack(target_language)
        lesson_entries: list[str] = []
        for row in day_rows:
            day = int(row["day"])
            title = row["title"]
            goal = row["goal"]
            deliverable = row["deliverable"]
            quiz_focus = row["quiz_focus"]
            module = row["module"]
            previous_title = day_rows[day - 2]["title"] if day > 1 else pack["onramp"]
            next_title = day_rows[day]["title"] if day < len(day_rows) else pack["capstone"]
            guided_exercise = self._creator_sentence(pack["guided_exercise"], title=title, deliverable=deliverable, topic=topic)
            independent_exercise = self._creator_sentence(pack["independent_exercise"], title=title, deliverable=deliverable, topic=topic)
            self_check = self._creator_sentence(pack["self_check"], title=title, deliverable=deliverable, topic=topic)
            intro = self._creator_sentence(pack["lesson_intro"], title=title, goal=goal, topic=topic)
            why = self._creator_sentence(pack["lesson_why"], title=title, goal=goal, topic=topic, module=module)
            explanation = self._creator_sentence(pack["lesson_explanation"], title=title, goal=goal, topic=topic, deliverable=deliverable)
            example = self._creator_sentence(pack["lesson_example"], title=title, deliverable=deliverable, topic=topic)
            guided_body = self._creator_sentence(pack["lesson_guided"], title=title, deliverable=deliverable, topic=topic)
            independent_body = self._creator_sentence(pack["lesson_independent"], title=title, deliverable=deliverable, topic=topic)
            self_check_body = self._creator_sentence(pack["lesson_self_check"], title=title, deliverable=deliverable, topic=topic)
            email_subject = self._creator_sentence(pack["email_subject"], day=f"{day:02d}", title=title, topic=topic)
            email_body = self._creator_sentence(pack["email_body"], title=title, goal=goal, deliverable=deliverable, topic=topic)
            lesson_entries.append(
                f"### Day {day:02d} Lesson Draft\n"
                f"- Lesson title: {title}\n"
                f"- Learning goal: {goal}\n"
                f"- Deliverable: {deliverable}\n"
                f"- Email subject: {email_subject}\n"
                f"- Guided exercise focus: {guided_exercise}\n"
                f"- Independent exercise focus: {independent_exercise}\n"
                f"- Self-check focus: {self_check}\n"
                f"- Quiz focus: {quiz_focus}\n"
                f"\n#### Lesson Body Draft\n"
                f"## {pack['learning_goal_heading']}\n{intro}\n\n"
                f"## {pack['why_heading']}\n{why}\n\n"
                f"## {pack['explanation_heading']}\n{explanation}\n\n"
                f"{self._creator_sentence(pack['lesson_context'], previous=previous_title, next=next_title, topic=topic)}\n\n"
                f"## {pack['example_heading']}\n{example}\n\n"
                f"## {pack['guided_heading']}\n{guided_body}\n\n"
                f"## {pack['independent_heading']}\n{independent_body}\n\n"
                f"## {pack['self_check_heading']}\n{self_check_body}\n\n"
                f"#### Email Body Draft\n"
                f"## {pack['today_heading']}\n{email_body}\n"
            )
        return (
            f"# Lesson Generation Batch\n\n"
            f"## Topic\n{topic}\n\n"
            f"## Language\n{target_language}\n\n"
            f"## Batch Rule\n"
            f"Generate lesson drafts from the approved blueprint only. Keep the target language pure and the exercises application-first.\n\n"
            + "\n".join(lesson_entries)
        )

    def _creator_build_quiz_batch_seed(
        self,
        topic: str,
        target_language: str,
        lesson_artifact: str,
    ) -> str:
        day_rows = self._creator_parse_lesson_batch_rows(lesson_artifact)
        if not day_rows:
            return (
                f"# Quiz Generation Batch\n\n"
                f"## Topic\n{topic}\n\n"
                f"## Language\n{target_language}\n\n"
                f"Lesson batch parsing did not find day lesson drafts yet. Confirm the lesson batch first, then regenerate this stage.\n"
            )
        pack = self._creator_copy_pack(target_language)
        entries: list[str] = []
        for row in day_rows:
            day = int(row["day"])
            lesson_title = row["lesson_title"]
            goal = row["goal"]
            deliverable = row["deliverable"]
            quiz_focus = row["quiz_focus"]
            entries.append(
                f"### Day {day:02d} Quiz Draft\n"
                f"- Lesson title: {lesson_title}\n"
                f"- Deliverable: {deliverable}\n"
                f"- Quiz focus: {quiz_focus}\n"
                f"- Batch target: 7 application-first questions\n"
            )
            for question_number in range(1, 8):
                entries.append(
                    f"#### Question {question_number}\n"
                    f"- Stem focus: {self._creator_sentence(pack['quiz_stem_focus'], title=lesson_title, deliverable=deliverable, quiz_focus=quiz_focus, question_number=str(question_number), topic=topic)}\n"
                    f"- Correct answer intent: {self._creator_sentence(pack['quiz_correct_intent'], title=lesson_title, goal=goal, deliverable=deliverable, topic=topic)}\n"
                    f"- Distractor themes: {self._creator_sentence(pack['quiz_distractors'], title=lesson_title, goal=goal, deliverable=deliverable, topic=topic)}\n"
                    f"- Question type: application\n"
                )
        return (
            f"# Quiz Generation Batch\n\n"
            f"## Topic\n{topic}\n\n"
            f"## Language\n{target_language}\n\n"
            f"## Batch Rule\n"
            f"Generate quiz drafts from the approved lesson batch only. Keep the target language pure, application-first, and aligned to the lesson deliverable.\n\n"
            + "\n".join(entries)
        )

    def _creator_extract_bullets(self, markdown: str, heading: str, limit: int) -> list[str]:
        if not markdown.strip():
            return []
        pattern = rf"##\s+{re.escape(heading)}\s*(.*?)(?:\n##\s+|\Z)"
        match = re.search(pattern, markdown, flags=re.DOTALL)
        if not match:
            return []
        body = match.group(1)
        rows = []
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("###"):
                continue
            stripped = re.sub(r"^[-*]\s+", "", stripped)
            lowered = stripped.lower()
            if not stripped:
                continue
            if stripped.endswith(":"):
                continue
            if stripped.endswith("?"):
                continue
            if lowered.startswith("what ") or lowered.startswith("identify ") or lowered.startswith("define "):
                continue
            if lowered.startswith("prevent ") and "mixed-language" in lowered:
                continue
            if lowered.startswith("prevent ") and "generic lesson titles" in lowered:
                continue
            if lowered.startswith("scope boundaries still need"):
                continue
            if lowered.startswith("audience still needs"):
                continue
            if stripped:
                rows.append(stripped)
            if len(rows) >= limit:
                break
        return rows

    def _creator_topic_short_title(self, topic: str) -> str:
        clean = re.sub(r"\s+", " ", str(topic or "").strip()).strip(" .,:;")
        if not clean:
            return "the topic"
        primary = clean.split(",")[0].strip()
        primary = re.sub(r"\bhow to\b.*$", "", primary, flags=re.IGNORECASE).strip(" .,:;")
        primary = re.sub(r"\bfor beginners\b", "", primary, flags=re.IGNORECASE).strip(" .,:;")
        primary = re.sub(r"\bfor beginner\b", "", primary, flags=re.IGNORECASE).strip(" .,:;")
        if primary:
            return primary
        words = [word for word in re.split(r"\s+", clean) if word]
        return " ".join(words[:3]) if words else "the topic"

    def _creator_day_title(self, topic: str, day: int) -> str:
        phases = [
            "orientation and baseline",
            "audience and context",
            "core concepts",
            "diagnosis and friction",
            "success metrics",
            "principles and models",
            "mistakes and risks",
            "decision criteria",
            "workflow design",
            "tools and setup",
            "daily operating rhythm",
            "weekly review cadence",
            "communication and stakeholders",
            "easy-case scenario",
            "messy-case scenario",
            "recovery and iteration",
            "templates and checklists",
            "measurement loops",
            "collaboration patterns",
            "quality standards",
            "optimization patterns",
            "automation opportunities",
            "exceptions and constraints",
            "adaptation strategies",
            "scaling the practice",
            "capstone framing",
            "capstone build",
            "capstone review",
            "transfer and maintenance",
            "final integration",
        ]
        suffix = phases[(day - 1) % len(phases)]
        title_base = self._creator_topic_short_title(topic)
        return f"{title_base}: {suffix}".strip()

    def _creator_day_deliverable(self, topic: str, day: int) -> str:
        title_base = self._creator_topic_short_title(topic)
        deliverables = [
            "baseline dashboard sketch",
            "learner use-case map",
            "data model checklist",
            "visual design rule set",
            "first working report page",
            "filter and slicer plan",
            "stakeholder question map",
            "metric definition sheet",
            "cleaned import workflow",
            "report navigation draft",
            "daily analysis routine",
            "weekly review template",
            "storytelling page draft",
            "easy-case walkthrough",
            "messy-case recovery plan",
            "iteration checklist",
            "report template v1",
            "quality review scorecard",
            "collaboration handoff note",
            "design QA checklist",
            "optimization test plan",
            "automation shortlist",
            "exception handling note",
            "adaptation playbook",
            "scaling checklist",
            "capstone brief",
            "capstone first draft",
            "capstone review notes",
            "maintenance checklist",
            "final report package",
        ]
        item = deliverables[(day - 1) % len(deliverables)]
        return f"{title_base} {item}"

    def _creator_day_quiz_focus(self, day: int, topic: str) -> str:
        title_base = self._creator_topic_short_title(topic)
        if day <= 5:
            return f"Identify the right beginner use case and starting baseline for {title_base}."
        if day <= 15:
            return f"Choose the best workflow or decision pattern while building with {title_base}."
        if day <= 25:
            return f"Apply {title_base} under realistic constraints and tradeoffs."
        return f"Integrate {title_base} into a complete working reporting routine and review outcomes."

    def _creator_parse_blueprint_days(self, markdown: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        pattern = re.compile(
            r"### Day (?P<day>\d{2}) — (?P<title>.+?)\n"
            r"- Module: (?P<module>.+?)\n"
            r"- Goal: (?P<goal>.+?)\n"
            r"- Deliverable: (?P<deliverable>.+?)\n"
            r"- Quiz focus: (?P<quiz_focus>.+?)(?:\n|$)",
            flags=re.DOTALL,
        )
        for match in pattern.finditer(markdown):
            rows.append({key: value.strip() for key, value in match.groupdict().items()})
        return rows

    def _creator_parse_lesson_batch_rows(self, markdown: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        pattern = re.compile(
            r"### Day (?P<day>\d{2}) Lesson Draft\n"
            r"- Lesson title: (?P<lesson_title>.+?)\n"
            r"- Learning goal: (?P<goal>.+?)\n"
            r"- Deliverable: (?P<deliverable>.+?)\n"
            r"- Email subject: (?P<email_subject>.+?)\n"
            r"- Guided exercise focus: (?P<guided_focus>.+?)\n"
            r"- Independent exercise focus: (?P<independent_focus>.+?)\n"
            r"- Self-check focus: (?P<self_check_focus>.+?)\n"
            r"- Quiz focus: (?P<quiz_focus>.+?)\n"
            r"\n#### Lesson Body Draft\n(?P<lesson_body>.*?)\n\n#### Email Body Draft\n(?P<email_body>.*?)(?=\n### Day |\Z)",
            flags=re.DOTALL,
        )
        for match in pattern.finditer(markdown):
            rows.append({key: value.strip() for key, value in match.groupdict().items()})
        return rows

    def _creator_parse_quiz_batch_rows(self, markdown: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        day_pattern = re.compile(
            r"### Day (?P<day>\d{2}) Quiz Draft\n"
            r"- Lesson title: (?P<lesson_title>.+?)\n"
            r"- Deliverable: (?P<deliverable>.+?)\n"
            r"- Quiz focus: (?P<quiz_focus>.+?)\n"
            r"- Batch target: (?P<batch_target>.+?)\n"
            r"(?P<body>.*?)(?=\n### Day |\Z)",
            flags=re.DOTALL,
        )
        question_pattern = re.compile(
            r"#### Question (?P<question_number>\d+)\n"
            r"- Stem focus: (?P<stem_focus>.+?)\n"
            r"- Correct answer intent: (?P<correct_intent>.+?)\n"
            r"- Distractor themes: (?P<distractor_themes>.+?)\n"
            r"- Question type: (?P<question_type>.+?)(?:\n|$)",
            flags=re.DOTALL,
        )
        for day_match in day_pattern.finditer(markdown):
            base = {key: value.strip() for key, value in day_match.groupdict().items() if key != "body"}
            body = day_match.group("body")
            for question_match in question_pattern.finditer(body):
                row = dict(base)
                row.update({key: value.strip() for key, value in question_match.groupdict().items()})
                rows.append(row)
        return rows

    def _creator_copy_pack(self, language_code: str) -> dict[str, str]:
        code = str(language_code or "").strip().lower()
        packs: dict[str, dict[str, str]] = {
            "en": {
                "learning_goal_heading": "Learning Goal",
                "why_heading": "Why It Matters",
                "explanation_heading": "Explanation",
                "example_heading": "Example",
                "guided_heading": "Guided Exercise",
                "independent_heading": "Independent Exercise",
                "self_check_heading": "Self-Check",
                "today_heading": "Today",
                "onramp": "course entry point",
                "capstone": "capstone integration",
                "email_subject": "Day {day} — {title}",
                "lesson_intro": "The learner should be able to {goal} through the lens of {title}.",
                "lesson_why": "{title} matters because the learner must turn ideas into repeatable action instead of loose theory inside {module}.",
                "lesson_explanation": "This lesson explains how to move from intent to execution around {title}, using the concrete deliverable {deliverable} as proof of applied understanding.",
                "lesson_context": "This draft connects back to {previous} and prepares the learner for {next}, so the day sits inside a continuous 30-day progression.",
                "lesson_example": "A realistic scenario should show how {title} becomes visible in day-to-day work, including how the learner notices friction and improves the result.",
                "lesson_guided": "Walk the learner through a structured exercise that produces {deliverable} in one concrete scenario connected to {title}.",
                "lesson_independent": "Ask the learner to adapt the same pattern to their own context and produce a version of {deliverable} without step-by-step support.",
                "lesson_self_check": "Help the learner review whether {deliverable} is specific, usable, and consistent with the main lesson goal.",
                "guided_exercise": "Produce {deliverable} in one guided scenario linked to {title}.",
                "independent_exercise": "Adapt {deliverable} to the learner's own context using the same pattern from {title}.",
                "self_check": "Verify whether {deliverable} is clear, useful, and consistent with the goal of {title}.",
                "email_body": "Today we focus on {title}. The learner should leave able to {goal}. Open the lesson and build {deliverable}.",
                "quiz_stem_focus": "Present a practical decision moment for {title} that tests whether the learner can produce or judge {deliverable} under realistic constraints. Focus {question_number}: {quiz_focus}",
                "quiz_correct_intent": "The best answer should apply {goal} in a concrete way and move the learner toward {deliverable}.",
                "quiz_distractors": "Distractors should reflect plausible mistakes: generic action, incomplete delivery, mis-prioritization, or theory without execution.",
            },
            "hu": {
                "learning_goal_heading": "Tanulási cél",
                "why_heading": "Miért fontos",
                "explanation_heading": "Magyarázat",
                "example_heading": "Példa",
                "guided_heading": "Irányított gyakorlat",
                "independent_heading": "Önálló gyakorlat",
                "self_check_heading": "Önellenőrzés",
                "today_heading": "Ma",
                "onramp": "kurzusindító rész",
                "capstone": "záró integráció",
                "email_subject": "{day}. nap — {title}",
                "lesson_intro": "A tanuló célja, hogy {goal}, mégpedig a(z) {title} leckén keresztül.",
                "lesson_why": "A(z) {title} azért fontos, mert a tanulónak a gondolatokat ismételhető gyakorlattá kell alakítania a(z) {module} területen.",
                "lesson_explanation": "Ez a lecke azt mutatja meg, hogyan lesz a szándékból végrehajtás a(z) {title} témában, miközben a konkrét bizonyíték a(z) {deliverable}.",
                "lesson_context": "Ez a vázlat visszakapcsol ehhez: {previous}, és előkészíti ezt: {next}, így a nap egy folytonos 30 napos ív része marad.",
                "lesson_example": "A példa mutassa meg, hogyan jelenik meg a(z) {title} a mindennapi működésben, hogyan ismeri fel a tanuló a súrlódást, és hogyan javít az eredményen.",
                "lesson_guided": "Vezesd végig a tanulót egy olyan gyakorlati feladaton, amelynek kimenete a(z) {deliverable}, és amely közvetlenül kapcsolódik a(z) {title} témához.",
                "lesson_independent": "Kérd meg a tanulót, hogy ugyanazt a mintát a saját helyzetére alkalmazza, és önállóan készítse el a(z) {deliverable} saját változatát.",
                "lesson_self_check": "Segíts a tanulónak ellenőrizni, hogy a(z) {deliverable} elég konkrét, használható és összhangban van-e a lecke fő céljával.",
                "guided_exercise": "Készítsd el a(z) {deliverable} első változatát egy vezetett helyzetben a(z) {title} alapján.",
                "independent_exercise": "Alakítsd át a(z) {deliverable} feladatot a saját környezetedre a(z) {title} mintája szerint.",
                "self_check": "Ellenőrizd, hogy a(z) {deliverable} valóban világos, hasznos és a(z) {title} céljához illeszkedik-e.",
                "email_body": "Ma a(z) {title} kerül fókuszba. A cél, hogy a tanuló képes legyen erre: {goal}. Nyisd meg a leckét, és készítsd el ezt: {deliverable}.",
                "quiz_stem_focus": "Adj egy gyakorlati döntési helyzetet a(z) {title} témában, ahol a tanulónak a(z) {deliverable} létrehozását vagy megítélését kell alkalmaznia. {question_number}. fókusz: {quiz_focus}",
                "quiz_correct_intent": "A legjobb válasz a(z) {goal} gyakorlati alkalmazását mutassa meg, és közelebb vigye a tanulót ehhez: {deliverable}.",
                "quiz_distractors": "A rossz válaszok legyenek hihető hibák: túl általános lépés, hiányos megoldás, rossz prioritás vagy végrehajtás nélküli elmélet.",
            },
        }
        return dict(packs.get(code) or packs["en"])

    def _creator_seed_question_from_quiz_row(
        self,
        row: dict[str, str],
        target_language: str,
        question_uuid: str,
    ) -> dict[str, Any]:
        stem = str(row.get("stem_focus") or "").strip()
        correct = str(row.get("correct_intent") or "").strip()
        distractor_source = str(row.get("distractor_themes") or "").strip()
        fragments = [
            piece.strip(" .;:-")
            for piece in re.split(r"[,:;]\s+|\.\s+", distractor_source)
            if piece.strip(" .;:-")
        ]
        while len(fragments) < 3:
            fragments.append(distractor_source or stem or "Distractor")
        options = [correct]
        options.extend(fragments[:3])
        options = [item if len(item) >= 25 else f"{item}. {stem}" for item in options]
        return {
            "uuid": question_uuid,
            "question": stem,
            "options": options[:4],
            "correctIndex": 0,
            "questionType": str(row.get("question_type") or "application"),
            "difficulty": "MEDIUM",
            "category": "Course Specific",
            "hashtags": [f"#{target_language}", "#creator-draft", "#qc-review"],
            "isActive": True,
            "language": target_language,
            "lessonTitle": str(row.get("lesson_title") or "").strip(),
        }

    def _creator_sentence(self, template: str, **values: str) -> str:
        normalized = {key: str(value or "").strip() for key, value in values.items()}
        return template.format(**normalized)

    def _creator_artifact_summaries(self, stage_artifacts: dict[str, Any]) -> dict[str, dict[str, Any]]:
        summaries: dict[str, dict[str, Any]] = {}
        research_content = str((stage_artifacts.get("research") or {}).get("content") or "").strip()
        if research_content:
            bullets = len(re.findall(r"^\s*-\s+", research_content, flags=re.MULTILINE))
            summaries["research"] = {
                "headline": f"Research brief with {bullets} captured bullets.",
                "stats": [f"Bullets {bullets}"],
            }
        blueprint_content = str((stage_artifacts.get("blueprint") or {}).get("content") or "").strip()
        if blueprint_content:
            day_rows = self._creator_parse_blueprint_days(blueprint_content)
            modules = sorted({row.get("module") or "" for row in day_rows if row.get("module")})
            summaries["blueprint"] = {
                "headline": f"{len(day_rows)} day architecture across {len(modules)} modules." if day_rows else "Blueprint saved.",
                "stats": [f"Days {len(day_rows)}", f"Modules {len(modules)}"],
                "samples": [row.get("title") or "" for row in day_rows[:3] if row.get("title")],
            }
        lesson_content = str((stage_artifacts.get("lesson_generation") or {}).get("content") or "").strip()
        if lesson_content:
            lesson_rows = len(re.findall(r"^### Day\s+\d{2}\s+Lesson Draft$", lesson_content, flags=re.MULTILINE))
            email_rows = len(re.findall(r"^- Email subject:", lesson_content, flags=re.MULTILINE))
            lesson_titles = re.findall(r"^- Lesson title:\s+(.+)$", lesson_content, flags=re.MULTILINE)
            summaries["lesson_generation"] = {
                "headline": f"{lesson_rows} lesson batch drafts prepared." if lesson_rows else "Lesson batch saved.",
                "stats": [f"Lesson drafts {lesson_rows}", f"Email subjects {email_rows}"],
                "samples": lesson_titles[:3],
            }
        quiz_content = str((stage_artifacts.get("quiz_generation") or {}).get("content") or "").strip()
        if quiz_content:
            quiz_days = len(re.findall(r"^### Day\s+\d{2}\s+Quiz Draft$", quiz_content, flags=re.MULTILINE))
            question_drafts = len(re.findall(r"^#### Question\s+\d+$", quiz_content, flags=re.MULTILINE))
            summaries["quiz_generation"] = {
                "headline": f"{question_drafts} quiz draft prompts across {quiz_days} days." if question_drafts else "Quiz batch saved.",
                "stats": [f"Quiz days {quiz_days}", f"Question drafts {question_drafts}"],
            }
        qc_content = str((stage_artifacts.get("qc_review") or {}).get("content") or "").strip()
        if qc_content:
            total = re.search(r"- Total QC tasks: (\d+)", qc_content)
            completed = re.search(r"- Completed: (\d+)", qc_content)
            failed = re.search(r"- Failed: (\d+)", qc_content)
            quarantined = re.search(r"- Quarantined: (\d+)", qc_content)
            summaries["qc_review"] = {
                "headline": (
                    f"QC queue contains {int(total.group(1)) if total else 0} injected tasks."
                ),
                "stats": [
                    f"Completed {int(completed.group(1)) if completed else 0}",
                    f"Failed {int(failed.group(1)) if failed else 0}",
                    f"Quarantined {int(quarantined.group(1)) if quarantined else 0}",
                ],
            }
        live_content = str((stage_artifacts.get("draft_to_live") or {}).get("content") or "").strip()
        if live_content:
            completed = re.search(r"- QC completed: (\d+) / (\d+)", live_content)
            failed = re.search(r"- Failed tasks: (\d+)", live_content)
            quarantined = re.search(r"- Quarantined tasks: (\d+)", live_content)
            summaries["draft_to_live"] = {
                "headline": "Draft-to-live readiness summary prepared.",
                "stats": [
                    f"QC completed {completed.group(1)}/{completed.group(2)}" if completed else "QC completed 0/0",
                    f"Failed {int(failed.group(1)) if failed else 0}",
                    f"Quarantined {int(quarantined.group(1)) if quarantined else 0}",
                ],
            }
        return summaries

    def _creator_collect_sources(
        self,
        topic: str,
        target_language: str,
        existing: list[dict[str, str]] | None = None,
    ) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_urls: set[str] = set()
        seen_domains: dict[str, dict[str, str]] = {}
        preferred_domains = self._preferred_source_domains(topic)
        fetched_at = utc_now()
        for item in existing or []:
            url = str(item.get("url") or "").strip()
            if not url:
                if str(item.get("sourceType") or "manual").strip() == "manual":
                    title = self._strip_tags(str(item.get("title") or "").strip())
                    snippet = self._strip_tags(str(item.get("snippet") or "").strip())
                    if title or snippet:
                        manual_item = {
                            "sourceId": str(item.get("sourceId") or f"src-{sha256_json({'title': title, 'snippet': snippet, 'type': 'manual'})[:12]}"),
                            "title": html_unescape(title),
                            "url": "",
                            "snippet": html_unescape(snippet),
                            "sourceType": "manual",
                            "domain": "",
                            "score": str(max(0, min(100, int(float(str(item.get("score") or '50')))))),
                            "fetchedAt": str(item.get("fetchedAt") or fetched_at),
                            "reviewStatus": str(item.get("reviewStatus") or "neutral"),
                            "topicMatches": list(item.get("topicMatches") or []),
                        }
                        results.append(manual_item)
                continue
            normalized = self._normalize_source_item(
                {
                    "sourceId": str(item.get("sourceId") or ""),
                    "title": str(item.get("title") or "").strip(),
                    "url": url,
                    "snippet": str(item.get("snippet") or "").strip(),
                    "sourceType": str(item.get("sourceType") or "existing").strip() or "existing",
                    "fetchedAt": str(item.get("fetchedAt") or fetched_at),
                    "reviewStatus": str(item.get("reviewStatus") or "neutral"),
                    "topicMatches": list(item.get("topicMatches") or []),
                },
                preferred_domains,
                topic,
            )
            if not normalized:
                continue
            seen_urls.add(normalized["url"])
            self._merge_source_candidate(results, seen_domains, normalized)
        queries = [
            topic,
            f"{topic} {target_language} guide",
            f"{topic} best practices",
        ]
        for query in queries:
            for row in self._duckduckgo_search(query, max_results=3):
                url = row.get("url") or ""
                if not url or url in seen_urls:
                    continue
                normalized = self._normalize_source_item({**row, "fetchedAt": fetched_at}, preferred_domains, topic)
                if not normalized:
                    continue
                seen_urls.add(normalized["url"])
                self._merge_source_candidate(results, seen_domains, normalized)
                if len(results) >= 12:
                    break
        for row in self._wikipedia_search(topic, max_results=3):
            url = row.get("url") or ""
            if not url or url in seen_urls:
                continue
            normalized = self._normalize_source_item({**row, "fetchedAt": fetched_at}, preferred_domains, topic)
            if not normalized:
                continue
            seen_urls.add(normalized["url"])
            self._merge_source_candidate(results, seen_domains, normalized)
        ranked = sorted(results, key=lambda item: int(item.get("score") or 0), reverse=True)
        return ranked[:8]

    def _preferred_source_domains(self, topic: str) -> list[str]:
        topic_lower = topic.lower()
        domains = [
            "wikipedia.org",
            "coursera.org",
            "edx.org",
            "gov",
            "edu",
            "mckinsey.com",
            "hbr.org",
        ]
        if "sales" in topic_lower:
            domains.extend(["salesforce.com", "hubspot.com", "gong.io", "secondnature.ai"])
        if "ai" in topic_lower:
            domains.extend(["openai.com", "anthropic.com", "deepmind.google"])
        return domains

    def _topic_keywords(self, topic: str) -> list[str]:
        tokens = re.findall(r"[A-Za-z0-9+#.]+", str(topic or "").lower())
        stop_words = {
            "the", "and", "for", "with", "from", "into", "how", "what", "why", "when", "where",
            "your", "their", "this", "that", "these", "those", "create", "creating", "beautiful",
            "useful", "minutes", "course", "training", "guide", "required", "optional", "beginner",
            "beginners", "introduction", "intro", "learn", "learning",
        }
        keywords: list[str] = []
        for token in tokens:
            if len(token) < 3 or token in stop_words:
                continue
            if token not in keywords:
                keywords.append(token)
        return keywords[:8]

    def _source_topic_relevance(self, title: str, snippet: str, topic: str) -> tuple[int, list[str]]:
        haystack = f"{title} {snippet}".lower()
        keywords = self._topic_keywords(topic)
        matches = [keyword for keyword in keywords if keyword in haystack]
        return len(matches), matches

    def _normalize_source_item(self, item: dict[str, str], preferred_domains: list[str], topic: str) -> dict[str, str] | None:
        url = str(item.get("url") or "").strip()
        if not url.startswith("http"):
            return None
        parsed = urllib.parse.urlparse(url)
        domain = (parsed.netloc or "").lower().removeprefix("www.")
        title = self._strip_tags(str(item.get("title") or "").strip())
        snippet = self._strip_tags(str(item.get("snippet") or "").strip())
        if not title and not snippet:
            return None
        relevance_score, matches = self._source_topic_relevance(title, snippet, topic)
        if relevance_score <= 0 and str(item.get("sourceType") or "") != "manual":
            return None
        score = self._score_source(domain, title, snippet, preferred_domains, relevance_score)
        return {
            "sourceId": str(item.get("sourceId") or f"src-{sha256_json({'title': title, 'url': url, 'sourceType': str(item.get('sourceType') or 'web-search')})[:12]}"),
            "title": html_unescape(title),
            "url": url,
            "snippet": html_unescape(snippet),
            "sourceType": str(item.get("sourceType") or "web-search"),
            "domain": domain,
            "score": str(score),
            "fetchedAt": str(item.get("fetchedAt") or utc_now()),
            "reviewStatus": str(item.get("reviewStatus") or "neutral"),
            "topicMatches": matches,
        }

    def _merge_source_candidate(
        self,
        results: list[dict[str, str]],
        seen_domains: dict[str, dict[str, str]],
        candidate: dict[str, str],
    ) -> None:
        domain = str(candidate.get("domain") or "")
        existing = seen_domains.get(domain)
        candidate_score = int(candidate.get("score") or 0)
        if existing is None:
            results.append(candidate)
            if domain:
                seen_domains[domain] = candidate
            return
        existing_score = int(existing.get("score") or 0)
        if candidate_score > existing_score:
            results.remove(existing)
            results.append(candidate)
            seen_domains[domain] = candidate

    def _score_source(self, domain: str, title: str, snippet: str, preferred_domains: list[str], relevance_score: int) -> int:
        score = 0
        if domain.startswith("en.wikipedia.org") or domain.endswith("wikipedia.org"):
            score += 30
        if any(domain == preferred or domain.endswith(f".{preferred}") or (preferred in {"gov", "edu"} and domain.endswith(f".{preferred}")) for preferred in preferred_domains):
            score += 25
        if title:
            score += 10
        if len(snippet) >= 80:
            score += 10
        if domain.endswith(".gov") or domain.endswith(".edu"):
            score += 20
        if "course" in title.lower() or "guide" in title.lower() or "training" in title.lower():
            score += 8
        score += min(relevance_score * 18, 54)
        return score

    def _duckduckgo_search(self, query: str, max_results: int = 5) -> list[dict[str, str]]:
        encoded = urllib.parse.urlencode({"q": query})
        url = f"https://html.duckduckgo.com/html/?{encoded}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; AmanobaCourseCreator/1.0)",
                "Accept-Language": "en-US,en;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                body = response.read().decode("utf-8", errors="replace")
        except Exception:
            return []
        rows: list[dict[str, str]] = []
        matches = re.findall(
            r'<a[^>]*class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>.*?(?:<a[^>]*class="result__snippet"[^>]*>|<div[^>]*class="result__snippet"[^>]*>)(?P<snippet>.*?)(?:</a>|</div>)',
            body,
            flags=re.DOTALL,
        )
        for raw_url, raw_title, raw_snippet in matches[:max_results]:
            url = html_unescape(self._strip_tags(raw_url))
            if "duckduckgo.com/l/?" in url:
                parsed = urllib.parse.urlparse(url)
                final_url = urllib.parse.parse_qs(parsed.query).get("uddg", [""])[0]
                if final_url:
                    url = urllib.parse.unquote(final_url)
            rows.append(
                {
                    "title": html_unescape(self._strip_tags(raw_title)),
                    "url": url,
                    "snippet": html_unescape(self._strip_tags(raw_snippet)),
                    "sourceType": "web-search",
                }
            )
        return rows

    def _wikipedia_search(self, topic: str, max_results: int = 3) -> list[dict[str, str]]:
        params = urllib.parse.urlencode(
            {
                "action": "query",
                "list": "search",
                "srsearch": topic,
                "utf8": "1",
                "format": "json",
                "srlimit": str(max_results),
            }
        )
        url = f"https://en.wikipedia.org/w/api.php?{params}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AmanobaCourseCreator/1.0)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []
        rows: list[dict[str, str]] = []
        for item in (payload.get("query") or {}).get("search") or []:
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            rows.append(
                {
                    "title": title,
                    "url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                    "snippet": html_unescape(self._strip_tags(str(item.get("snippet") or ""))),
                    "sourceType": "wikipedia",
                }
            )
        return rows

    def _strip_tags(self, value: str) -> str:
        return re.sub(r"<[^>]+>", " ", value or "").replace("\n", " ").replace("\r", " ").strip()

    def live_inventory_counts(self) -> dict[str, int]:
        if self.live_bridge is None:
            return {}
        try:
            payload = self.live_bridge.stats()
        except Exception:
            return {}
        counts = payload.get("counts") or {}
        return {
            "courses": int(counts.get("courses") or 0),
            "lessons": int(counts.get("lessons") or 0),
            "questions": int(counts.get("questions") or 0),
        }

    def _cached_inventory_counts(self) -> dict[str, int]:
        report_path = self.config.reports_dir / "health.json"
        if report_path.exists():
            try:
                payload = json.loads(report_path.read_text(encoding="utf-8"))
                inventory = dict(payload.get("inventory") or {})
                return {
                    "courses": int(inventory.get("courses") or 0),
                    "lessons": int(inventory.get("lessons") or 0),
                    "questions": int(inventory.get("questions") or 0),
                }
            except Exception:
                return {}
        return {}

    def reported_health_snapshot(self) -> dict[str, Any]:
        report_path = self.config.reports_dir / "health.json"
        snapshot = self.health_snapshot()
        self._write_json_atomic(report_path, snapshot)
        return snapshot

    def _iter_candidate_files(self) -> list[Path]:
        results: list[Path] = []
        for pattern in self.config.scan_globs:
            for path in self.config.workspace_root.glob(pattern):
                if not path.is_file():
                    continue
                if any(part in self.config.ignore_dirs for part in path.parts):
                    continue
                results.append(path.resolve())
        return sorted(set(results))

    def _load_package(self, path: Path) -> dict[str, Any] | None:
        try:
            if not path.exists() or not path.is_file():
                return None
        except OSError:
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None
        if not isinstance(payload.get("course"), dict):
            return None
        if not isinstance(payload.get("lessons"), list):
            return None
        return payload

    def _enrich_task_summary(self, summary: dict[str, Any]) -> dict[str, Any]:
        details = dict(summary.get("details") or {})
        if details.get("waitingOnLessonQc"):
            summary["displayStatus"] = "waiting-on-lesson"
            summary["lastError"] = "Waiting for the connected lesson to pass QC before question review can begin."
        rca = dict(details.get("rca") or {})
        rca_type = str(rca.get("type") or "").strip().lower()
        last_error = str(summary.get("lastError") or "").strip()
        is_repairable = rca_type == "repairable-content" or _looks_like_repairable_content_error(last_error)
        if is_repairable:
            summary["displayStatus"] = "rewriting"
            if last_error:
                recovery_mode = str(details.get("recoveryMode") or "").strip()
                if recovery_mode == "course-writer-reconstruction" or _looks_like_repairable_content_error(last_error):
                    summary["lastError"] = "Scheduled for full question/lesson reconstruction from course context."
                else:
                    summary["lastError"] = "Scheduled for rewrite because the content quality is repairable."
        if self.config.source_mode == "amanoba_live_db":
            course_name = str(details.get("humanCourseName") or summary.get("courseId") or "Unknown course")
            day_label = str(details.get("humanDayLabel") or summary.get("lessonId") or "-")
            lesson_title = str(details.get("humanLessonTitle") or summary.get("lessonId") or "-")
            human_title = str(
                details.get("displayTitle")
                or (details.get("after") or {}).get("question")
                or (details.get("before") or {}).get("question")
                or (details.get("after") or {}).get("title")
                or (details.get("before") or {}).get("title")
                or summary.get("taskKey")
            )
            summary["details"] = details
            summary["humanTitle"] = human_title
            summary["humanCourseName"] = course_name
            summary["humanDayLabel"] = day_label
            summary["humanLessonTitle"] = lesson_title
            summary["humanContext"] = f"{course_name} • {day_label}"
            summary["humanUpdatedAt"] = summary.get("finishedAt") or summary.get("updatedAt") or summary.get("startedAt") or summary.get("createdAt")
            return summary
        package_path_raw = str(summary.get("packagePath") or "").strip()
        package_path = Path(package_path_raw) if package_path_raw else None
        package = self._load_package(package_path) if package_path is not None else None
        course = package.get("course") if package is not None else None
        lesson = None
        question = None
        if package is not None:
            lesson = next((item for item in package.get("lessons") or [] if str(item.get("lessonId")) == str(summary.get("lessonId") or "")), None)
            if lesson is not None and summary.get("kind") == "question":
                index = summary.get("questionIndex")
                questions = lesson.get("quizQuestions") or []
                if isinstance(index, int) and 0 <= index < len(questions):
                    question = questions[index]
        if summary.get("kind") == "question":
            if "before" not in details and isinstance(question, dict):
                details["before"] = json.loads(json.dumps(question, ensure_ascii=False))
            if "displayTitle" not in details:
                details["displayTitle"] = (
                    str((details.get("after") or {}).get("question") or (details.get("before") or {}).get("question") or "")
                    or str((question or {}).get("question") or "")
                )
        else:
            if "before" not in details and isinstance(lesson, dict):
                details["before"] = {
                    "title": lesson.get("title"),
                    "content": lesson.get("content"),
                    "emailSubject": lesson.get("emailSubject"),
                    "emailBody": lesson.get("emailBody"),
                }
            if "displayTitle" not in details:
                details["displayTitle"] = (
                    str((details.get("after") or {}).get("title") or (details.get("before") or {}).get("title") or "")
                    or str((lesson or {}).get("title") or "")
                )
        human_title = details.get("displayTitle") or summary.get("questionUuid") or summary.get("lessonId") or summary.get("taskKey")
        course_name = str((course or {}).get("name") or summary.get("courseId") or "Unknown course")
        day_number = (lesson or {}).get("dayNumber")
        day_label = f"Day {day_number}" if day_number not in (None, "") else str(summary.get("lessonId") or "-")
        lesson_title = str((lesson or {}).get("title") or summary.get("lessonId") or "-")
        summary["details"] = details
        summary["humanTitle"] = str(human_title)
        summary["humanCourseName"] = course_name
        summary["humanDayLabel"] = day_label
        summary["humanLessonTitle"] = lesson_title
        summary["humanContext"] = f"{course_name} • {day_label}"
        summary["humanUpdatedAt"] = summary.get("finishedAt") or summary.get("updatedAt") or summary.get("startedAt") or summary.get("createdAt")
        return summary

    def _enqueue_tasks(self, path: Path, package: dict[str, Any]) -> int:
        raw_text = path.read_text(encoding="utf-8")
        fingerprint = sha256_text(raw_text)
        course = package.get("course") or {}
        lessons = package.get("lessons") or []
        course_id = str(course.get("courseId", ""))
        language = str(course.get("language", ""))
        self.state.save_package(str(path), fingerprint, course_id, language)

        created = 0
        for lesson_index, lesson in enumerate(lessons):
            lesson_id = str(lesson.get("lessonId", f"lesson-{lesson_index + 1}"))
            lesson_audit = audit_lesson(lesson, language)
            if not lesson_audit.is_valid:
                self.state.upsert_task(
                    task_key=f"lesson::{path}::{lesson_id}",
                    kind="lesson",
                    package_path=str(path),
                    course_id=course_id,
                    language=language,
                    lesson_id=lesson_id,
                    question_uuid=None,
                    question_index=None,
                    source_hash=sha256_json({"lesson": lesson}),
                    details={
                        "errors": lesson_audit.errors,
                        "warnings": lesson_audit.warnings,
                        "displayTitle": str(lesson.get("title") or lesson_id),
                        "judgement": confidence_for_validation("lesson", lesson_audit.errors, lesson_audit.warnings),
                    },
                )
                created += 1
                continue
            for question_index, question in enumerate(lesson.get("quizQuestions") or []):
                validation = validate_question(question, language)
                if validation.is_valid:
                    continue
                question_uuid = str(question.get("uuid") or f"idx-{question_index}")
                self.state.upsert_task(
                    task_key=f"question::{path}::{lesson_id}::{question_uuid}",
                    kind="question",
                    package_path=str(path),
                    course_id=course_id,
                    language=language,
                    lesson_id=lesson_id,
                    question_uuid=question_uuid,
                    question_index=question_index,
                    source_hash=sha256_json({"question": question}),
                    details={
                        "errors": validation.errors,
                        "warnings": validation.warnings,
                        "displayTitle": str(question.get("question") or question_uuid),
                        "judgement": confidence_for_validation("question", validation.errors, validation.warnings),
                    },
                )
                created += 1
        return created

    def _process_task(self, task: sqlite3.Row) -> dict[str, Any]:
        task_key = str(task["task_key"])
        if str(task["kind"]) == "creator_lesson":
            return self._process_creator_lesson_task(task)
        if str(task["kind"]) == "creator_question":
            return self._process_creator_question_task(task)
        if self.config.source_mode == "amanoba_live_db":
            return self._process_live_task(task)
        package_path = Path(task["package_path"])
        package = self._load_package(package_path)
        if package is None:
            raise RuntimeError(f"Package could not be loaded: {package_path}")
        course = package["course"]
        lessons = package["lessons"]
        lesson = next((item for item in lessons if str(item.get("lessonId")) == task["lesson_id"]), None)
        if lesson is None:
            raise RuntimeError(f"Lesson not found: {task['lesson_id']}")
        human_feedback = self.state.feedback_comments(task["task_key"])
        if task["kind"] == "lesson":
            return self._process_lesson_task(package_path, package, course, lesson, human_feedback, task_key=task_key)
        return self._process_question_task(package_path, package, course, lesson, int(task["question_index"]), human_feedback, task_key=task_key)

    def _lesson_ready_for_question_queue(self, *, package_path: str, course_id: str, lesson_id: str) -> bool:
        lesson_task = self.state.related_lesson_task(package_path, course_id, lesson_id)
        if lesson_task is None:
            return True
        return str(lesson_task["status"] or "") == "completed"

    def _question_task_waits_on_lesson(self, task: sqlite3.Row) -> bool:
        if str(task["kind"] or "") not in {"question", "creator_question"}:
            return False
        package_path = str(task["package_path"] or "")
        course_id = str(task["course_id"] or "")
        lesson_id = str(task["lesson_id"] or "")
        if not package_path or not lesson_id:
            return False
        lesson_task = self.state.related_lesson_task(package_path, course_id, lesson_id)
        if lesson_task is None:
            return False
        return str(lesson_task["status"] or "") != "completed"

    def _claim_next_eligible_task(self, max_attempts: int) -> sqlite3.Row | None:
        deferred = 0
        while True:
            task = self.state.claim_next_task(max_attempts)
            if task is None:
                return None
            if not self._question_task_waits_on_lesson(task):
                return task
            deferred += 1
            self.state.defer_task(
                str(task["task_key"]),
                details={
                    "waitingOnLessonQc": True,
                    "waitingOnLessonId": str(task["lesson_id"] or ""),
                },
            )
            self._clear_heartbeat_task("idle", f"Deferred {task['task_key']} until lesson QC passes.")
            if deferred >= 25:
                return None

    def _process_live_task(self, task: sqlite3.Row) -> dict[str, Any]:
        if self.live_bridge is None:
            raise RuntimeError("Live DB mode is enabled but the live bridge is not configured.")
        task_key = str(task["task_key"])
        live_task = self.live_bridge.fetch(str(task["task_key"]))
        human_feedback = self.state.feedback_comments(task["task_key"])
        course = live_task.get("course") or {}
        lesson = live_task.get("lesson") or {}
        context = dict(live_task.get("context") or {})
        if task["kind"] == "lesson":
            return self._process_live_lesson_task(task_key, course, lesson, human_feedback, context)
        question = live_task.get("question") or {}
        return self._process_live_question_task(task_key, course, lesson, question, human_feedback, context)

    def _creator_task_details(self, task: sqlite3.Row) -> dict[str, Any]:
        raw = task["details_json"]
        if not raw:
            return {}
        try:
            loaded = json.loads(raw)
            return loaded if isinstance(loaded, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _creator_store_qc_result(
        self,
        run_id: str,
        task_key: str,
        kind: str,
        payload_after: dict[str, Any],
        metadata: dict[str, Any],
    ) -> None:
        with self.state._lock:
            row = self.state.conn.execute("SELECT * FROM creator_runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None:
                raise RuntimeError(f"Creator run not found for QC result: {run_id}")
            creator_payload = self.state._load_creator_payload(row["payload_json"])
            qc_payload = dict(creator_payload.get("qcPayload") or {})
            lessons = dict(qc_payload.get("lessons") or {})
            questions = dict(qc_payload.get("questions") or {})
            results = dict(qc_payload.get("results") or {})
            if kind == "lesson":
                key = str(metadata.get("lessonId") or task_key)
                lessons[key] = payload_after
            else:
                key = str(metadata.get("questionUuid") or task_key)
                questions[key] = payload_after
            results[task_key] = {
                "status": str(metadata.get("status") or "completed"),
                "kind": kind,
                "displayTitle": str(metadata.get("displayTitle") or key),
                "updatedAt": utc_now(),
            }
            qc_payload["lessons"] = lessons
            qc_payload["questions"] = questions
            qc_payload["results"] = results
            creator_payload["qcPayload"] = qc_payload
            self.state.conn.execute(
                "UPDATE creator_runs SET payload_json=?, updated_at=? WHERE run_id=?",
                (json.dumps(creator_payload, ensure_ascii=False), utc_now(), run_id),
            )
            self.state.conn.commit()

    def _specialist_task_details(self, attempt: dict[str, Any]) -> dict[str, Any]:
        specialist = dict(attempt.get("specialist") or {})
        if not specialist:
            return {}
        return {
            "specialistPipeline": {
                "active": True,
                "provider": str(specialist.get("provider") or "specialist-pipeline"),
                "accepted": bool(specialist.get("accepted")),
                "trustScore": specialist.get("trustScore"),
                "impactScore": specialist.get("impactScore"),
                "judgeReason": str(specialist.get("judgeReason") or ""),
                "revisionNote": str(specialist.get("revisionNote") or ""),
                "roles": specialist.get("roles") or {},
            }
        }

    def _process_creator_lesson_task(self, task: sqlite3.Row) -> dict[str, Any]:
        task_key = str(task["task_key"])
        details = self._creator_task_details(task)
        before = _normalize_lesson_payload(dict(details.get("before") or {}))
        lesson_row = dict(details.get("lessonRow") or {})
        source_rows = list(details.get("sourceRows") or [])
        target_language = str(task["language"] or details.get("language") or "")
        human_feedback = self.state.feedback_comments(str(task["task_key"]))
        course = {
            "courseId": str(task["course_id"] or details.get("runId") or ""),
            "name": str(details.get("humanCourseName") or details.get("runId") or "Creator draft"),
            "language": target_language,
        }
        day_label = str(details.get("humanDayLabel") or task["lesson_id"] or "-")
        lesson = {
            "lessonId": str(task["lesson_id"] or ""),
            "title": str(before.get("title") or details.get("displayTitle") or task["lesson_id"] or ""),
            "content": str(before.get("content") or ""),
            "emailSubject": str(before.get("emailSubject") or ""),
            "emailBody": str(before.get("emailBody") or ""),
            "language": target_language,
            "dayNumber": int(str(details.get("creatorDay") or "0") or "0") or None,
        }
        context = dict(details.get("context") or {})
        audit = audit_lesson(before, target_language)
        if lesson_row:
            sanitized_before = _normalize_lesson_payload(
                {
                    "title": self._creator_public_lesson_title(
                        str(lesson_row.get("lesson_title") or ""),
                        str(before.get("title") or lesson.get("title") or ""),
                    ),
                    "content": self._creator_render_public_lesson_content(
                        str(lesson_row.get("lesson_title") or before.get("title") or lesson.get("title") or ""),
                        str(lesson_row.get("goal") or ""),
                        str(lesson_row.get("deliverable") or ""),
                        str(lesson_row.get("lesson_title") or ""),
                        source_rows,
                    ),
                    "emailSubject": self._creator_render_public_email_subject(
                        self._creator_public_lesson_title(
                            str(lesson_row.get("lesson_title") or ""),
                            str(before.get("title") or lesson.get("title") or ""),
                        ),
                        int(str(details.get("creatorDay") or "0") or "0") or 1,
                    ),
                    "emailBody": self._creator_render_public_email_body(
                        self._creator_public_lesson_title(
                            str(lesson_row.get("lesson_title") or ""),
                            str(before.get("title") or lesson.get("title") or ""),
                        ),
                        str(lesson_row.get("deliverable") or ""),
                    ),
                }
            )
            sanitized_audit = audit_lesson(sanitized_before, target_language)
            if sanitized_audit.is_valid:
                self._creator_store_qc_result(
                    str(details.get("runId") or ""),
                    str(task["task_key"]),
                    "lesson",
                    sanitized_before,
                    {
                        "lessonId": str(task["lesson_id"] or ""),
                        "status": "sanitized-valid",
                        "displayTitle": str(sanitized_before.get("title") or task["lesson_id"] or ""),
                    },
                )
                judgement = confidence_for_completion("creator-sanitized", sanitized_audit.warnings)
                return {
                    "status": "sanitized-valid",
                    "warnings": sanitized_audit.warnings,
                    "judgement": judgement,
                    "before": before,
                    "after": sanitized_before,
                    "displayTitle": str(sanitized_before.get("title") or task["lesson_id"] or ""),
                    "humanCourseName": course["name"],
                    "humanDayLabel": day_label,
                    "humanLessonTitle": str(sanitized_before.get("title") or task["lesson_id"] or ""),
                    "creatorRunId": str(details.get("runId") or ""),
                }
        if audit.is_valid:
            self._creator_store_qc_result(
                str(details.get("runId") or ""),
                str(task["task_key"]),
                "lesson",
                before,
                {
                    "lessonId": str(task["lesson_id"] or ""),
                    "status": "already-valid",
                    "displayTitle": str(before.get("title") or task["lesson_id"] or ""),
                },
            )
            judgement = confidence_for_completion("none", audit.warnings)
            return {
                "status": "already-valid",
                "warnings": audit.warnings,
                "judgement": judgement,
                "before": before,
                "after": before,
                "displayTitle": str(before.get("title") or task["lesson_id"] or ""),
                "humanCourseName": course["name"],
                "humanDayLabel": day_label,
                "humanLessonTitle": str(before.get("title") or task["lesson_id"] or ""),
                "creatorRunId": str(details.get("runId") or ""),
            }
        pulse = self._start_task_progress_pulse(task_key, "Creator lesson rewrite still in progress.")
        try:
            attempt = self._repair_lesson_candidate(course, lesson, target_language, audit, human_feedback, context)
        finally:
            self._stop_task_progress_pulse(pulse)
        raw_after = _normalize_lesson_payload(attempt["after"])
        after, merged_fields = _merge_lesson_payload(before, raw_after)
        post_audit = audit_lesson(after, target_language)
        changed_fields = [key for key in before if before.get(key) != after.get(key)]
        resolved_errors = [item for item in audit.errors if item not in post_audit.errors]
        if not post_audit.is_valid:
            raise TaskProcessingError(
                f"Rewritten creator lesson still failed validation: {post_audit.errors}",
                details={
                    "status": "partially-rewritten",
                    "provider": attempt["provider"],
                    "recoveryMode": attempt["mode"],
                    "warnings": post_audit.warnings,
                    "before": before,
                    "after": after,
                    "feedbackUsed": human_feedback,
                    "changedFields": changed_fields,
                    "resolvedErrors": resolved_errors,
                    "remainingErrors": post_audit.errors,
                    "mergedFallbackFields": merged_fields,
                    "missingGeneratedFields": _missing_lesson_fields(raw_after),
                    "providerTimings": attempt.get("providerTimings") or [],
                    **self._specialist_task_details(attempt),
                    "displayTitle": str(after.get("title") or before.get("title") or task["lesson_id"] or ""),
                    "humanCourseName": course["name"],
                    "humanDayLabel": day_label,
                    "humanLessonTitle": str(after.get("title") or before.get("title") or task["lesson_id"] or ""),
                    "creatorRunId": str(details.get("runId") or ""),
                },
            )
        self._creator_store_qc_result(
            str(details.get("runId") or ""),
            str(task["task_key"]),
            "lesson",
            after,
            {
                "lessonId": str(task["lesson_id"] or ""),
                "status": "completed",
                "displayTitle": str(after.get("title") or before.get("title") or task["lesson_id"] or ""),
            },
        )
        judgement = confidence_for_completion(str(attempt["provider"]), post_audit.warnings)
        return {
            "status": "rewritten" if attempt["mode"] == "rewrite" else "reconstructed",
            "provider": attempt["provider"],
            "recoveryMode": attempt["mode"],
            "warnings": post_audit.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "displayTitle": str(after.get("title") or before.get("title") or task["lesson_id"] or ""),
            "humanCourseName": course["name"],
            "humanDayLabel": day_label,
            "humanLessonTitle": str(after.get("title") or before.get("title") or task["lesson_id"] or ""),
            "feedbackUsed": human_feedback,
            "changedFields": changed_fields,
            "resolvedErrors": resolved_errors,
            "remainingErrors": [],
            "mergedFallbackFields": merged_fields,
            "missingGeneratedFields": _missing_lesson_fields(raw_after),
            "providerTimings": attempt.get("providerTimings") or [],
            **self._specialist_task_details(attempt),
            "creatorRunId": str(details.get("runId") or ""),
        }

    def _process_creator_question_task(self, task: sqlite3.Row) -> dict[str, Any]:
        task_key = str(task["task_key"])
        details = self._creator_task_details(task)
        before = json.loads(json.dumps(details.get("before") or {}, ensure_ascii=False))
        target_language = str(task["language"] or before.get("language") or "")
        human_feedback = self.state.feedback_comments(str(task["task_key"]))
        course = {
            "courseId": str(task["course_id"] or details.get("runId") or ""),
            "name": str(details.get("humanCourseName") or details.get("runId") or "Creator draft"),
            "language": target_language,
        }
        lesson = {
            "lessonId": str(task["lesson_id"] or ""),
            "title": str(details.get("humanLessonTitle") or before.get("lessonTitle") or task["lesson_id"] or ""),
            "language": target_language,
            "dayNumber": int(str(details.get("creatorDay") or "0") or "0") or None,
        }
        validation = validate_question(before, target_language)
        if validation.is_valid:
            self._creator_store_qc_result(
                str(details.get("runId") or ""),
                str(task["task_key"]),
                "question",
                before,
                {
                    "questionUuid": str(task["question_uuid"] or ""),
                    "status": "already-valid",
                    "displayTitle": str(before.get("question") or task["question_uuid"] or ""),
                },
            )
            judgement = confidence_for_completion("none", validation.warnings)
            return {
                "status": "already-valid",
                "warnings": validation.warnings,
                "judgement": judgement,
                "before": before,
                "after": before,
                "displayTitle": str(before.get("question") or task["question_uuid"] or ""),
                "humanCourseName": course["name"],
                "humanDayLabel": str(details.get("humanDayLabel") or task["lesson_id"] or "-"),
                "humanLessonTitle": lesson["title"],
                "creatorRunId": str(details.get("runId") or ""),
            }
        self._task_checkpoint(task_key, "Drafting creator question rewrite.")
        pulse = self._start_task_progress_pulse(task_key, "Creator question rewrite still in progress.")
        try:
            attempt = self._repair_question_candidate(course, lesson, before, target_language, validation, human_feedback, {})
        finally:
            self._stop_task_progress_pulse(pulse)
        self._task_checkpoint(task_key, "Creator question draft generated.")
        after = json.loads(json.dumps(attempt["after"], ensure_ascii=False))
        post_validation = attempt["validation"]
        changed_fields = [key for key in after if before.get(key) != after.get(key)]
        draft_changed = json.dumps(before, ensure_ascii=False, sort_keys=True) != json.dumps(after, ensure_ascii=False, sort_keys=True)
        resolved_errors = [item for item in validation.errors if item not in post_validation.errors]
        if draft_changed:
            self._creator_store_qc_result(
                str(details.get("runId") or ""),
                str(task["task_key"]),
                "question",
                after,
                {
                    "questionUuid": str(task["question_uuid"] or ""),
                    "status": "partial-applied" if not post_validation.is_valid else "completed",
                    "displayTitle": str(after.get("question") or before.get("question") or task["question_uuid"] or ""),
                },
            )
        if not post_validation.is_valid:
            raise TaskProcessingError(
                f"Rewritten creator question still failed validation: {post_validation.errors}",
                details={
                    "status": "partially-rewritten",
                    "provider": attempt["provider"],
                    "recoveryMode": attempt["mode"],
                    "warnings": post_validation.warnings,
                    "before": before,
                    "after": after,
                    "feedbackUsed": human_feedback,
                    "changedFields": changed_fields,
                    "draftChanged": draft_changed,
                    "resolvedErrors": resolved_errors,
                    "remainingErrors": post_validation.errors,
                    "providerTimings": attempt.get("providerTimings") or [],
                    **self._specialist_task_details(attempt),
                    "displayTitle": str(after.get("question") or before.get("question") or task["question_uuid"] or ""),
                    "humanCourseName": course["name"],
                    "humanDayLabel": str(details.get("humanDayLabel") or task["lesson_id"] or "-"),
                    "humanLessonTitle": lesson["title"],
                    "creatorRunId": str(details.get("runId") or ""),
                },
            )
        self._creator_store_qc_result(
            str(details.get("runId") or ""),
            str(task["task_key"]),
            "question",
            after,
            {
                "questionUuid": str(task["question_uuid"] or ""),
                "status": "completed",
                "displayTitle": str(after.get("question") or before.get("question") or task["question_uuid"] or ""),
            },
        )
        judgement = confidence_for_completion(str(attempt["provider"]), post_validation.warnings)
        return {
            "status": "rewritten" if attempt["mode"] == "rewrite" else "reconstructed",
            "provider": attempt["provider"],
            "recoveryMode": attempt["mode"],
            "warnings": post_validation.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "displayTitle": str(after.get("question") or before.get("question") or task["question_uuid"] or ""),
            "humanCourseName": course["name"],
            "humanDayLabel": str(details.get("humanDayLabel") or task["lesson_id"] or "-"),
            "humanLessonTitle": lesson["title"],
            "feedbackUsed": human_feedback,
            "changedFields": changed_fields,
            "draftChanged": draft_changed,
            "resolvedErrors": resolved_errors,
            "remainingErrors": [],
            "providerTimings": attempt.get("providerTimings") or [],
            **self._specialist_task_details(attempt),
            "creatorRunId": str(details.get("runId") or ""),
        }

    def _should_reconstruct_lesson(self, audit: ValidationResult, lesson: dict[str, Any]) -> bool:
        content = str(lesson.get("content") or "").strip()
        lowered = " | ".join([*audit.errors, *audit.warnings]).lower()
        return (
            len(content) < 900
            or "too short" in lowered
            or "very compact" in lowered
            or "little visible structure" in lowered
            or "does not show clear" in lowered
        )

    def _should_template_reconstruct_lesson(self, audit: ValidationResult, lesson: dict[str, Any]) -> bool:
        return False

    def _should_reconstruct_question(self, validation: ValidationResult, question: dict[str, Any]) -> bool:
        stem = str(question.get("question") or "").strip()
        options = [str(item).strip() for item in (question.get("options") or [])]
        lowered = " | ".join([*validation.errors, *validation.warnings]).lower()
        short_options = sum(1 for item in options if len(item) < 25)
        return (
            len(stem) < 80
            or len(options) < 4
            or short_options >= 2
            or "at least 2 options" in lowered
            or "must be at least 40 characters" in lowered
            or "does not show clear" in lowered
        )

    def _lesson_context_notes(self, course: dict[str, Any], context: dict[str, Any]) -> list[str]:
        notes = [
            "Escalation: this lesson is too poor for incremental QC repair. Recreate it from scratch as a clean course-writer draft.",
            f"Course context: {json.dumps({'courseId': course.get('courseId'), 'name': course.get('name'), 'language': course.get('language')}, ensure_ascii=False)}",
        ]
        previous = context.get("previousLesson") or {}
        if previous:
            notes.append(
                "Previous lesson anchor: "
                + json.dumps(
                    {
                        "lessonId": previous.get("lessonId"),
                        "dayNumber": previous.get("dayNumber"),
                        "title": previous.get("title"),
                        "contentExcerpt": str(previous.get("content") or "")[:500],
                    },
                    ensure_ascii=False,
                )
            )
        nxt = context.get("nextLesson") or {}
        if nxt:
            notes.append(
                "Next lesson anchor: "
                + json.dumps(
                    {
                        "lessonId": nxt.get("lessonId"),
                        "dayNumber": nxt.get("dayNumber"),
                        "title": nxt.get("title"),
                        "contentExcerpt": str(nxt.get("content") or "")[:500],
                    },
                    ensure_ascii=False,
                )
            )
        siblings = context.get("siblingQuestions") or []
        if siblings:
            notes.append(
                "Current-lesson question style anchors: "
                + json.dumps(
                    [
                        {
                            "question": item.get("question"),
                            "options": (item.get("options") or [])[:4],
                        }
                        for item in siblings[:3]
                    ],
                    ensure_ascii=False,
                )
            )
        notes.append("Keep the intended day/topic aligned with neighboring lessons. Do not mention these notes in the output.")
        return notes

    def _context_title(
        self,
        lesson_like: dict[str, Any] | None,
        fallback: str,
        target_language: str = "",
        *,
        allow_english_fallback: bool = True,
    ) -> str:
        if lesson_like and str(lesson_like.get("title") or "").strip():
            candidate = str(lesson_like.get("title") or "").strip()
            if not _language_purity_errors([candidate], target_language, allow_english_fallback=allow_english_fallback):
                return candidate
        return fallback

    def _template_reconstruct_lesson(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        context: dict[str, Any],
        target_language: str,
    ) -> dict[str, str]:
        pack = _lesson_language_pack(target_language)
        title = str(lesson.get("title") or "").strip() or self._context_title(
            context.get("nextLesson") or {},
            "Lesson",
            target_language,
            allow_english_fallback=False,
        )
        previous_title = self._context_title(context.get("previousLesson") or {}, title, target_language, allow_english_fallback=False)
        next_title = self._context_title(context.get("nextLesson") or {}, title, target_language, allow_english_fallback=False)
        sibling_questions = [
            str(item.get("question") or "").strip()
            for item in (context.get("siblingQuestions") or [])[:2]
            if str(item.get("question") or "").strip()
            and not _language_purity_errors([str(item.get("question") or "").strip()], target_language, allow_english_fallback=True)
        ]
        question_bridge = pack["question_bridge"]
        if sibling_questions:
            question_bridge += " " + " ".join(sibling_questions)

        content = "\n\n".join(
            [
                f"## {pack['goal']}\n{pack['goal_text'].format(title=title)}",
                f"## {pack['why']}\n{pack['why_text'].format(title=title)}",
                (
                    f"## {pack['explanation']}\n"
                    f"{pack['explanation_text'].format(title=title)}\n\n"
                    f"{pack['context_text'].format(previous=previous_title, next=next_title)}"
                ),
                f"## {pack['example']}\n{pack['example_text'].format(title=title)}",
                (
                    f"## {pack['exercise']}\n"
                    f"{pack['exercise_text'].format(title=title)}\n\n"
                    f"- {question_bridge}"
                ),
                f"## {pack['self_check']}\n{pack['self_check_text'].format(title=title)}",
            ]
        ).strip()

        existing_subject = str(lesson.get("emailSubject") or "").strip()
        if existing_subject and _language_purity_errors([existing_subject], target_language, allow_english_fallback=True):
            existing_subject = ""
        email_subject = existing_subject or f"{pack['email_subject_prefix']}: {title}"
        summary = pack["goal_text"].format(title=title)
        email_body = pack["email_body"].format(summary=summary, title=title, open_lesson=pack["open_lesson"])
        return {
            "title": title,
            "content": content,
            "emailSubject": email_subject,
            "emailBody": email_body,
        }

    def _clean_question_text(self, value: str) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        text = re.sub(r"^\s*képzeld\s+el,\s+hogy\s+", "", text, flags=re.I)
        text = re.sub(r"^\s*egy\s+feladaton\s+dolgozol,\s+és\s+döntened\s+kell\.?\s*", "", text, flags=re.I)
        text = re.sub(r"^\s*valós?\s+munka?helyzetben\s+kell\s+döntened\.?\s*", "", text, flags=re.I)
        text = re.sub(r"^\s*konret opcio:\s*", "", text, flags=re.I)
        text = re.sub(r"^\s*konkrét opció:\s*", "", text, flags=re.I)
        text = re.sub(r"\s+", " ", text).strip()
        return text.rstrip(".;,:")

    def _expand_question_option(
        self,
        text: str,
        *,
        target_language: str,
        is_correct: bool,
        fallback_index: int,
    ) -> str:
        base = self._clean_question_text(text)
        if not base:
            return ""
        return base if base.endswith((".", "!", "?")) else f"{base}."

    def _template_reconstruct_question(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        target_language: str,
    ) -> dict[str, Any]:
        raw_stem = self._clean_question_text(str(question.get("question") or ""))
        lesson_title = self._clean_question_text(str(lesson.get("title") or ""))
        stem = raw_stem or lesson_title
        if stem and not stem.endswith("?"):
            stem = f"{stem}?"

        raw_options = [str(item or "") for item in (question.get("options") or [])[:4]]
        while len(raw_options) < 4:
            raw_options.append("")
        correct_index = int(question.get("correctIndex") or 0)
        if correct_index < 0 or correct_index >= len(raw_options):
            correct_index = 0

        options: list[str] = []
        for index, raw_option in enumerate(raw_options[:4]):
            options.append(
                self._expand_question_option(
                    raw_option,
                    target_language=target_language,
                    is_correct=index == correct_index,
                    fallback_index=index,
                )
            )

        difficulty = str(question.get("difficulty") or "medium").strip().lower()
        if difficulty not in {"easy", "medium", "hard"}:
            difficulty = "medium"
        question_type = str(question.get("questionType") or "application").strip().lower() or "application"
        if question_type == "recall":
            question_type = "application"
        category = str(question.get("category") or "course_quality").strip().lower().replace(" ", "_") or "course_quality"
        hashtags = [str(item).strip() for item in (question.get("hashtags") or []) if str(item).strip()]
        return {
            "question": stem,
            "options": options[:4],
            "correctIndex": correct_index,
            "questionType": question_type,
            "difficulty": difficulty,
            "category": category,
            "hashtags": hashtags,
        }

    def _question_context_notes(self, course: dict[str, Any], lesson: dict[str, Any], context: dict[str, Any]) -> list[str]:
        notes = [
            "Escalation: this question is too poor for incremental QC repair. Recreate it from scratch as a clean course-writer question.",
            f"Course context: {json.dumps({'courseId': course.get('courseId'), 'name': course.get('name'), 'language': course.get('language')}, ensure_ascii=False)}",
            f"Lesson anchor: {json.dumps({'lessonId': lesson.get('lessonId'), 'title': lesson.get('title'), 'dayNumber': lesson.get('dayNumber')}, ensure_ascii=False)}",
        ]
        previous = context.get("previousLesson") or {}
        if previous:
            notes.append(
                "Previous lesson anchor: "
                + json.dumps(
                    {
                        "lessonId": previous.get("lessonId"),
                        "dayNumber": previous.get("dayNumber"),
                        "title": previous.get("title"),
                    },
                    ensure_ascii=False,
                )
            )
        nxt = context.get("nextLesson") or {}
        if nxt:
            notes.append(
                "Next lesson anchor: "
                + json.dumps(
                    {
                        "lessonId": nxt.get("lessonId"),
                        "dayNumber": nxt.get("dayNumber"),
                        "title": nxt.get("title"),
                    },
                    ensure_ascii=False,
                )
            )
        siblings = context.get("siblingQuestions") or []
        if siblings:
            notes.append(
                "Neighbor question anchors: "
                + json.dumps(
                    [
                        {
                            "question": item.get("question"),
                            "options": (item.get("options") or [])[:4],
                            "correctIndex": item.get("correctIndex"),
                        }
                        for item in siblings[:3]
                    ],
                    ensure_ascii=False,
                )
            )
        notes.append("Use the neighboring material only to infer intent and difficulty. Do not reference the lesson or course explicitly in the final question.")
        return notes

    def _package_lesson_context(self, package: dict[str, Any], lesson_id: str, *, include_questions: bool) -> dict[str, Any]:
        lessons = list(package.get("lessons") or [])
        ordered = sorted(
            lessons,
            key=lambda item: (
                int(item.get("dayNumber") or 0),
                str(item.get("lessonId") or ""),
            ),
        )
        index = next((idx for idx, item in enumerate(ordered) if str(item.get("lessonId") or "") == lesson_id), None)
        current = ordered[index] if index is not None else None
        context: dict[str, Any] = {}
        if index is not None and index > 0:
            prev = ordered[index - 1]
            context["previousLesson"] = {
                "lessonId": prev.get("lessonId"),
                "dayNumber": prev.get("dayNumber"),
                "title": prev.get("title"),
                "content": prev.get("content"),
            }
        if index is not None and index + 1 < len(ordered):
            nxt = ordered[index + 1]
            context["nextLesson"] = {
                "lessonId": nxt.get("lessonId"),
                "dayNumber": nxt.get("dayNumber"),
                "title": nxt.get("title"),
                "content": nxt.get("content"),
            }
        if include_questions and current is not None:
            context["siblingQuestions"] = [
                {
                    "question": item.get("question"),
                    "options": item.get("options") or [],
                    "correctIndex": item.get("correctIndex"),
                }
                for item in (current.get("quizQuestions") or [])[:3]
            ]
        return context

    def _writer_first_required(self, errors: list[str]) -> bool:
        lowered = " | ".join(str(item or "") for item in errors).lower()
        return (
            "does not show clear" in lowered
            or "mixes languages" in lowered
            or "language markers" in lowered
        )

    def _repair_lesson_candidate(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        target_language: str,
        audit: ValidationResult,
        human_feedback: list[str],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        provider_timings: list[dict[str, Any]] = []
        mode = "rewrite"
        candidate: dict[str, str]
        post_audit: ValidationResult

        specialist_errors = list(audit.errors)
        specialist_errors.extend(self._lesson_context_notes(course, context))
        specialist_errors.extend(f"Human challenge: {comment}" for comment in human_feedback)
        if self.runtime.specialist_qc_available():
            try:
                specialist = self.runtime.specialist_rewrite_lesson(
                    course,
                    lesson,
                    specialist_errors,
                    human_feedback,
                )
                provider_timings.extend(list(specialist.get("timings") or []))
                specialist_candidate = _normalize_lesson_payload(specialist["payload"])
                specialist_audit = audit_lesson(specialist_candidate, target_language)
                if bool(specialist.get("accepted")) and specialist_audit.is_valid:
                    return {
                        "provider": str(specialist.get("provider") or "specialist-pipeline"),
                        "mode": "specialist-pipeline",
                        "after": specialist_candidate,
                        "validation": specialist_audit,
                        "providerTimings": provider_timings,
                        "specialist": specialist,
                    }
            except Exception as exc:
                provider_timings.append(
                    {
                        "provider": "specialist-pipeline",
                        "status": "failed",
                        "detail": str(exc),
                        "durationMs": 0,
                    }
                )

        if self._should_reconstruct_lesson(audit, lesson):
            if self._should_template_reconstruct_lesson(audit, lesson):
                provider_name = "sanitization-fallback"
                provider_timings.append(
                    {
                        "provider": provider_name,
                        "status": "fallback",
                        "detail": "Immediate course-writer reconstruction for a clearly broken lesson.",
                        "durationMs": 0,
                    }
                )
                candidate = self._template_reconstruct_lesson(course, lesson, context, target_language)
                post_audit = audit_lesson(candidate, target_language)
                mode = "course-writer-reconstruction"
                return {
                    "provider": provider_name,
                    "mode": mode,
                    "after": candidate,
                    "validation": post_audit,
                    "providerTimings": provider_timings,
                }
            reconstruction_input = list(audit.errors)
            reconstruction_input.extend(self._lesson_context_notes(course, context))
            reconstruction_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
            try:
                reconstruction = self.runtime.rewrite_lesson_with_failover(
                    course,
                    lesson,
                    reconstruction_input,
                    preferred_order=self.runtime.writer_provider_order,
                )
                provider_name = str(reconstruction["provider"])
                provider_timings.extend(list(reconstruction.get("timings") or []))
                candidate = _normalize_lesson_payload(reconstruction["payload"])
                post_audit = audit_lesson(candidate, target_language)
            except Exception as exc:
                provider_name = "template-fallback"
                provider_timings.append({"provider": provider_name, "status": "fallback", "detail": str(exc), "durationMs": 0})
                candidate = self._template_reconstruct_lesson(course, lesson, context, target_language)
                post_audit = audit_lesson(candidate, target_language)
            mode = "course-writer-reconstruction"
        else:
            rewrite_input = list(audit.errors)
            rewrite_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
            rewrite_order = self.runtime.writer_provider_order if self._writer_first_required(audit.errors) else None
            rewrite = self.runtime.rewrite_lesson_with_failover(course, lesson, rewrite_input, preferred_order=rewrite_order)
            provider_name = str(rewrite["provider"])
            provider_timings.extend(list(rewrite.get("timings") or []))
            candidate = _normalize_lesson_payload(rewrite["payload"])
            post_audit = audit_lesson(candidate, target_language)
            if not post_audit.is_valid:
                reconstruction_input = list(audit.errors)
                reconstruction_input.extend(self._lesson_context_notes(course, context))
                reconstruction_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
                try:
                    reconstruction = self.runtime.rewrite_lesson_with_failover(
                        course,
                        lesson,
                        reconstruction_input,
                        preferred_order=self.runtime.writer_provider_order,
                    )
                    reconstruction_provider = str(reconstruction["provider"])
                    provider_timings.extend(list(reconstruction.get("timings") or []))
                    reconstructed = _normalize_lesson_payload(reconstruction["payload"])
                    reconstructed_audit = audit_lesson(reconstructed, target_language)
                except Exception as exc:
                    reconstruction_provider = "sanitization-fallback"
                    provider_timings.append({"provider": reconstruction_provider, "status": "fallback", "detail": str(exc), "durationMs": 0})
                    reconstructed = self._template_reconstruct_lesson(course, lesson, context, target_language)
                    reconstructed_audit = audit_lesson(reconstructed, target_language)
                if reconstructed_audit.is_valid or not post_audit.is_valid:
                    candidate = reconstructed
                    post_audit = reconstructed_audit
                    provider_name = reconstruction_provider
                    mode = "course-writer-reconstruction"
        return {
            "provider": provider_name,
            "mode": mode,
            "after": candidate,
            "validation": post_audit,
            "providerTimings": provider_timings,
        }

    def _repair_question_candidate(
        self,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        target_language: str,
        validation: ValidationResult,
        human_feedback: list[str],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        provider_timings: list[dict[str, Any]] = []
        rewrite_input = list(validation.errors)
        rewrite_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
        provider_name = "sanitization-fallback"
        mode = "sanitization-fallback"
        candidate = self._template_reconstruct_question(course, lesson, question, target_language)
        post_validation = validate_question(candidate, target_language)

        specialist_errors = list(validation.errors)
        specialist_errors.extend(self._question_context_notes(course, lesson, context))
        specialist_errors.extend(f"Human challenge: {comment}" for comment in human_feedback)
        if self.runtime.specialist_qc_available():
            try:
                specialist = self.runtime.specialist_rewrite_question(
                    course,
                    lesson,
                    question,
                    specialist_errors,
                    human_feedback,
                )
                provider_timings.extend(list(specialist.get("timings") or []))
                specialist_candidate = json.loads(json.dumps(specialist["payload"], ensure_ascii=False))
                specialist_validation = validate_question(specialist_candidate, target_language)
                if bool(specialist.get("accepted")) and specialist_validation.is_valid:
                    return {
                        "provider": str(specialist.get("provider") or "specialist-pipeline"),
                        "mode": "specialist-pipeline",
                        "after": specialist_candidate,
                        "validation": specialist_validation,
                        "providerTimings": provider_timings,
                        "specialist": specialist,
                    }
            except Exception as exc:
                provider_timings.append(
                    {
                        "provider": "specialist-pipeline",
                        "status": "failed",
                        "detail": str(exc),
                        "durationMs": 0,
                    }
                )

        try:
            rewrite_order = self.runtime.writer_provider_order if self._writer_first_required(validation.errors) else None
            rewrite = self.runtime.rewrite_question_with_failover(course, lesson, question, rewrite_input, preferred_order=rewrite_order)
            provider_name = str(rewrite["provider"])
            provider_timings.extend(list(rewrite.get("timings") or []))
            candidate = rewrite["payload"]
            post_validation = validate_question(candidate, target_language)
            mode = "rewrite"
        except Exception as exc:
            provider_timings.append(
                {
                    "provider": "sanitization-fallback",
                    "status": "fallback",
                    "detail": str(exc),
                    "durationMs": 0,
                }
            )

        if self._should_reconstruct_question(validation, question) or not post_validation.is_valid:
            reconstruction_input = list(validation.errors)
            reconstruction_input.extend(self._question_context_notes(course, lesson, context))
            reconstruction_input.extend(f"Human challenge: {comment}" for comment in human_feedback)
            try:
                reconstruction = self.runtime.rewrite_question_with_failover(
                    course,
                    lesson,
                    question,
                    reconstruction_input,
                    preferred_order=self.runtime.writer_provider_order,
                )
                reconstruction_provider = str(reconstruction["provider"])
                provider_timings.extend(list(reconstruction.get("timings") or []))
                reconstructed = reconstruction["payload"]
                reconstructed_validation = validate_question(reconstructed, target_language)
                if reconstructed_validation.is_valid or not post_validation.is_valid:
                    candidate = reconstructed
                    post_validation = reconstructed_validation
                    provider_name = reconstruction_provider
                    mode = "course-writer-reconstruction"
            except Exception as exc:
                fallback_candidate = self._template_reconstruct_question(course, lesson, question, target_language)
                fallback_validation = validate_question(fallback_candidate, target_language)
                provider_timings.append(
                    {
                        "provider": "sanitization-fallback",
                        "status": "fallback",
                        "detail": str(exc),
                        "durationMs": 0,
                    }
                )
                if fallback_validation.is_valid or not post_validation.is_valid:
                    candidate = fallback_candidate
                    post_validation = fallback_validation
                    provider_name = "sanitization-fallback"
                    mode = "sanitization-fallback"
        return {
            "provider": provider_name,
            "mode": mode,
            "after": json.loads(json.dumps(candidate, ensure_ascii=False)),
            "validation": post_validation,
            "providerTimings": provider_timings,
        }

    def _process_live_lesson_task(
        self,
        task_key: str,
        course: dict[str, Any],
        lesson: dict[str, Any],
        human_feedback: list[str],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        human_course = str(course.get("name") or lesson.get("courseName") or lesson.get("courseId") or "Unknown course")
        human_day = f"Day {lesson.get('dayNumber')}" if lesson.get("dayNumber") not in (None, "") else str(lesson.get("lessonId") or "-")
        human_lesson = str(lesson.get("title") or lesson.get("lessonId") or "-")
        before = {
            "title": lesson.get("title"),
            "content": lesson.get("content"),
            "emailSubject": lesson.get("emailSubject"),
            "emailBody": lesson.get("emailBody"),
        }
        target_language = str(course.get("language") or lesson.get("language") or "")
        audit = audit_lesson(before, target_language)
        if audit.is_valid:
            self.live_bridge.mark_reviewed(task_key, result="already-valid")
            judgement = confidence_for_completion("none", audit.warnings)
            return {
                "status": "already-valid",
                "warnings": audit.warnings,
                "judgement": judgement,
                "before": before,
                "after": before,
                "displayTitle": human_lesson,
                "humanCourseName": human_course,
                "humanDayLabel": human_day,
                "humanLessonTitle": human_lesson,
            }
        if not self.config.fix_lessons or not self.config.apply_fixes:
            raise RuntimeError(f"Lesson needs improvement but lesson fixing is disabled: {audit.errors}")
        self._task_checkpoint(task_key, "Drafting creator lesson rewrite.")
        pulse = self._start_task_progress_pulse(task_key, "Creator lesson rewrite still in progress.")
        try:
            attempt = self._repair_lesson_candidate(course, lesson, target_language, audit, human_feedback, context)
        finally:
            self._stop_task_progress_pulse(pulse)
        self._task_checkpoint(task_key, "Creator lesson draft generated.")
        raw_after = _normalize_lesson_payload(attempt["after"])
        after, merged_fields = _merge_lesson_payload(before, raw_after)
        post_audit = audit_lesson(after, target_language)
        changed_fields = [key for key in before if before.get(key) != after.get(key)]
        draft_changed = json.dumps(before, ensure_ascii=False, sort_keys=True) != json.dumps(after, ensure_ascii=False, sort_keys=True)
        resolved_errors = [item for item in audit.errors if item not in post_audit.errors]
        backup = None
        if draft_changed:
            backup = self._backup_live_snapshot(task_key, before)
            try:
                self.live_bridge.apply(task_key, after)
            except Exception as exc:
                raise TaskProcessingError(
                    f"Failed to apply lesson rewrite: {exc}",
                    details={
                        "status": "apply-failed",
                        "provider": attempt["provider"],
                        "recoveryMode": attempt["mode"],
                        "backup": str(backup) if backup is not None else None,
                        "warnings": post_audit.warnings,
                        "before": before,
                        "after": after,
                        "feedbackUsed": human_feedback,
                        "changedFields": changed_fields,
                        "draftChanged": draft_changed,
                        "resolvedErrors": resolved_errors,
                        "remainingErrors": post_audit.errors,
                        "partialApplied": False,
                        "mergedFallbackFields": merged_fields,
                        "missingGeneratedFields": _missing_lesson_fields(raw_after),
                        "providerTimings": attempt.get("providerTimings") or [],
                        **self._specialist_task_details(attempt),
                    },
                ) from exc
        if not post_audit.is_valid:
            raise TaskProcessingError(
                f"Rewritten lesson still failed validation: {post_audit.errors}",
                details={
                    "status": "partially-rewritten",
                    "provider": attempt["provider"],
                    "recoveryMode": attempt["mode"],
                    "backup": str(backup) if backup is not None else None,
                    "warnings": post_audit.warnings,
                    "before": before,
                    "after": after,
                    "feedbackUsed": human_feedback,
                    "changedFields": changed_fields,
                    "draftChanged": draft_changed,
                    "resolvedErrors": resolved_errors,
                    "remainingErrors": post_audit.errors,
                    "partialApplied": bool(draft_changed),
                    "mergedFallbackFields": merged_fields,
                    "missingGeneratedFields": _missing_lesson_fields(raw_after),
                    "providerTimings": attempt.get("providerTimings") or [],
                    **self._specialist_task_details(attempt),
                },
            )
        judgement = confidence_for_completion(str(attempt["provider"]), post_audit.warnings)
        return {
            "status": "rewritten" if attempt["mode"] == "rewrite" else "reconstructed",
            "provider": attempt["provider"],
            "recoveryMode": attempt["mode"],
            "backup": str(backup) if backup is not None else None,
            "warnings": post_audit.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "displayTitle": human_lesson,
            "humanCourseName": human_course,
            "humanDayLabel": human_day,
            "humanLessonTitle": human_lesson,
            "feedbackUsed": human_feedback,
            "changedFields": changed_fields,
            "draftChanged": draft_changed,
            "resolvedErrors": resolved_errors,
            "remainingErrors": [],
            "mergedFallbackFields": merged_fields,
            "missingGeneratedFields": _missing_lesson_fields(raw_after),
            "providerTimings": attempt.get("providerTimings") or [],
            **self._specialist_task_details(attempt),
        }

    def _process_live_question_task(
        self,
        task_key: str,
        course: dict[str, Any],
        lesson: dict[str, Any],
        question: dict[str, Any],
        human_feedback: list[str],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        human_course = str(course.get("name") or lesson.get("courseName") or lesson.get("courseId") or question.get("courseId") or "Unknown course")
        human_day = f"Day {lesson.get('dayNumber')}" if lesson.get("dayNumber") not in (None, "") else str(question.get("lessonId") or lesson.get("lessonId") or "-")
        human_lesson = str(lesson.get("title") or question.get("lessonTitle") or question.get("lessonId") or "-")
        human_question = str(question.get("question") or question.get("uuid") or task_key)
        before = json.loads(json.dumps(question, ensure_ascii=False))
        target_language = str(course.get("language") or lesson.get("language") or question.get("language") or "")
        validation = validate_question(before, target_language)
        if validation.is_valid:
            self.live_bridge.mark_reviewed(task_key, result="already-valid")
            judgement = confidence_for_completion("none", validation.warnings)
            return {
                "status": "already-valid",
                "warnings": validation.warnings,
                "judgement": judgement,
                "before": before,
                "after": before,
                "displayTitle": human_question,
                "humanCourseName": human_course,
                "humanDayLabel": human_day,
                "humanLessonTitle": human_lesson,
            }
        if not self.config.fix_questions or not self.config.apply_fixes:
            raise RuntimeError(f"Question needs improvement but question fixing is disabled: {validation.errors}")
        pulse = self._start_task_progress_pulse(task_key, "Live question rewrite still in progress.")
        try:
            attempt = self._repair_question_candidate(course, lesson, question, target_language, validation, human_feedback, context)
        finally:
            self._stop_task_progress_pulse(pulse)
        after = json.loads(json.dumps(attempt["after"], ensure_ascii=False))
        post_validation = attempt["validation"]
        changed_fields = [key for key in after if before.get(key) != after.get(key)]
        resolved_errors = [item for item in validation.errors if item not in post_validation.errors]
        backup = None
        if changed_fields:
            backup = self._backup_live_snapshot(task_key, before)
            self.live_bridge.apply(task_key, after)
        if not post_validation.is_valid:
            raise TaskProcessingError(
                f"Rewritten question still failed validation: {post_validation.errors}",
                details={
                    "status": "partially-rewritten",
                    "provider": attempt["provider"],
                    "recoveryMode": attempt["mode"],
                    "backup": str(backup) if backup is not None else None,
                    "warnings": post_validation.warnings,
                    "before": before,
                    "after": after,
                    "feedbackUsed": human_feedback,
                    "changedFields": changed_fields,
                    "resolvedErrors": resolved_errors,
                    "remainingErrors": post_validation.errors,
                    "partialApplied": bool(changed_fields),
                    "providerTimings": attempt.get("providerTimings") or [],
                    **self._specialist_task_details(attempt),
                },
            )
        judgement = confidence_for_completion(str(attempt["provider"]), post_validation.warnings)
        return {
            "status": "rewritten" if attempt["mode"] == "rewrite" else "reconstructed",
            "provider": attempt["provider"],
            "recoveryMode": attempt["mode"],
            "backup": str(backup) if backup is not None else None,
            "warnings": post_validation.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "displayTitle": str(after.get("question") or human_question),
            "humanCourseName": human_course,
            "humanDayLabel": human_day,
            "humanLessonTitle": human_lesson,
            "feedbackUsed": human_feedback,
            "changedFields": changed_fields,
            "resolvedErrors": resolved_errors,
            "remainingErrors": [],
            "providerTimings": attempt.get("providerTimings") or [],
            **self._specialist_task_details(attempt),
        }

    def _process_lesson_task(
        self,
        package_path: Path,
        package: dict[str, Any],
        course: dict[str, Any],
        lesson: dict[str, Any],
        human_feedback: list[str],
        task_key: str | None = None,
    ) -> dict[str, Any]:
        target_language = str(course.get("language") or lesson.get("language") or "")
        audit = audit_lesson(lesson, target_language)
        if audit.is_valid:
            judgement = confidence_for_completion("none", audit.warnings)
            return {"status": "already-valid", "warnings": audit.warnings, "judgement": judgement}
        if not self.config.fix_lessons or not self.config.apply_fixes:
            raise RuntimeError(f"Lesson needs improvement but lesson fixing is disabled: {audit.errors}")
        self._task_checkpoint(task_key, "Drafting lesson rewrite.")
        before = {
            "title": lesson.get("title"),
            "content": lesson.get("content"),
            "emailSubject": lesson.get("emailSubject"),
            "emailBody": lesson.get("emailBody"),
        }
        context = self._package_lesson_context(package, str(lesson.get("lessonId") or ""), include_questions=True)
        pulse = self._start_task_progress_pulse(task_key, "Package lesson rewrite still in progress.")
        try:
            attempt = self._repair_lesson_candidate(course, lesson, target_language, audit, human_feedback, context)
        finally:
            self._stop_task_progress_pulse(pulse)
        self._task_checkpoint(task_key, "Lesson draft generated.")
        raw_after = _normalize_lesson_payload(attempt["after"])
        after, merged_fields = _merge_lesson_payload(before, raw_after)
        post_audit = audit_lesson(after, target_language)
        changed_fields = [key for key in before if before.get(key) != after.get(key)]
        resolved_errors = [item for item in audit.errors if item not in post_audit.errors]
        backup = None
        if changed_fields:
            backup = self._backup_file(package_path)
            lesson["title"] = after["title"]
            lesson["content"] = after["content"]
            lesson["emailSubject"] = after["emailSubject"]
            lesson["emailBody"] = after["emailBody"]
            try:
                self._save_package(package_path, package)
            except Exception as exc:
                raise TaskProcessingError(
                    f"Failed to save lesson rewrite: {exc}",
                    details={
                        "status": "apply-failed",
                        "provider": attempt["provider"],
                        "recoveryMode": attempt["mode"],
                        "backup": str(backup) if backup is not None else None,
                        "warnings": post_audit.warnings,
                        "before": before,
                        "after": after,
                        "feedbackUsed": human_feedback,
                        "changedFields": changed_fields,
                        "resolvedErrors": resolved_errors,
                        "remainingErrors": post_audit.errors,
                        "partialApplied": False,
                        "mergedFallbackFields": merged_fields,
                        "missingGeneratedFields": _missing_lesson_fields(raw_after),
                        "providerTimings": attempt.get("providerTimings") or [],
                        **self._specialist_task_details(attempt),
                    },
                ) from exc
        if not post_audit.is_valid:
            raise TaskProcessingError(
                f"Rewritten lesson still failed validation: {post_audit.errors}",
                details={
                    "status": "partially-rewritten",
                    "provider": attempt["provider"],
                    "recoveryMode": attempt["mode"],
                    "backup": str(backup) if backup is not None else None,
                    "warnings": post_audit.warnings,
                    "before": before,
                    "after": after,
                    "feedbackUsed": human_feedback,
                    "changedFields": changed_fields,
                    "resolvedErrors": resolved_errors,
                    "remainingErrors": post_audit.errors,
                    "partialApplied": bool(changed_fields),
                    "mergedFallbackFields": merged_fields,
                    "missingGeneratedFields": _missing_lesson_fields(raw_after),
                    "providerTimings": attempt.get("providerTimings") or [],
                    **self._specialist_task_details(attempt),
                },
            )
        judgement = confidence_for_completion(str(attempt["provider"]), post_audit.warnings)
        return {
            "status": "rewritten" if attempt["mode"] == "rewrite" else "reconstructed",
            "provider": attempt["provider"],
            "recoveryMode": attempt["mode"],
            "backup": str(backup) if backup is not None else None,
            "warnings": post_audit.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "feedbackUsed": human_feedback,
            "changedFields": changed_fields,
            "resolvedErrors": resolved_errors,
            "remainingErrors": [],
            "mergedFallbackFields": merged_fields,
            "missingGeneratedFields": _missing_lesson_fields(raw_after),
            "providerTimings": attempt.get("providerTimings") or [],
            **self._specialist_task_details(attempt),
        }

    def _process_question_task(
        self,
        package_path: Path,
        package: dict[str, Any],
        course: dict[str, Any],
        lesson: dict[str, Any],
        question_index: int,
        human_feedback: list[str],
        task_key: str | None = None,
    ) -> dict[str, Any]:
        questions = lesson.get("quizQuestions") or []
        if question_index >= len(questions):
            raise RuntimeError(f"Question index is out of range: {question_index}")
        question = questions[question_index]
        target_language = str(course.get("language") or lesson.get("language") or question.get("language") or "")
        validation = validate_question(question, target_language)
        if validation.is_valid:
            judgement = confidence_for_completion("none", validation.warnings)
            return {"status": "already-valid", "warnings": validation.warnings, "judgement": judgement}
        if not self.config.fix_questions or not self.config.apply_fixes:
            raise RuntimeError(f"Question needs improvement but question fixing is disabled: {validation.errors}")
        self._task_checkpoint(task_key, "Drafting question rewrite.")
        before = json.loads(json.dumps(question, ensure_ascii=False))
        context = self._package_lesson_context(package, str(lesson.get("lessonId") or ""), include_questions=True)
        siblings = list(context.get("siblingQuestions") or [])
        if 0 <= question_index < len(siblings):
            siblings.pop(question_index)
        context["siblingQuestions"] = siblings
        pulse = self._start_task_progress_pulse(task_key, "Package question rewrite still in progress.")
        try:
            attempt = self._repair_question_candidate(course, lesson, question, target_language, validation, human_feedback, context)
        finally:
            self._stop_task_progress_pulse(pulse)
        self._task_checkpoint(task_key, "Question draft generated.")
        after = json.loads(json.dumps(attempt["after"], ensure_ascii=False))
        post_validation = attempt["validation"]
        changed_fields = [key for key in after if before.get(key) != after.get(key)]
        draft_changed = json.dumps(before, ensure_ascii=False, sort_keys=True) != json.dumps(after, ensure_ascii=False, sort_keys=True)
        resolved_errors = [item for item in validation.errors if item not in post_validation.errors]
        backup = None
        if draft_changed:
            backup = self._backup_file(package_path)
            for key in ["question", "options", "correctIndex", "questionType", "difficulty", "category", "hashtags"]:
                if key in after:
                    question[key] = after[key]
            self._save_package(package_path, package)
        if not post_validation.is_valid:
            raise TaskProcessingError(
                f"Rewritten question still failed validation: {post_validation.errors}",
                details={
                    "status": "partially-rewritten",
                    "provider": attempt["provider"],
                    "recoveryMode": attempt["mode"],
                    "backup": str(backup) if backup is not None else None,
                    "warnings": post_validation.warnings,
                    "before": before,
                    "after": after,
                    "feedbackUsed": human_feedback,
                    "changedFields": changed_fields,
                    "draftChanged": draft_changed,
                    "resolvedErrors": resolved_errors,
                    "remainingErrors": post_validation.errors,
                    "partialApplied": bool(draft_changed),
                    "providerTimings": attempt.get("providerTimings") or [],
                    **self._specialist_task_details(attempt),
                },
            )
        judgement = confidence_for_completion(str(attempt["provider"]), post_validation.warnings)
        return {
            "status": "rewritten" if attempt["mode"] == "rewrite" else "reconstructed",
            "provider": attempt["provider"],
            "recoveryMode": attempt["mode"],
            "backup": str(backup) if backup is not None else None,
            "warnings": post_validation.warnings,
            "judgement": judgement,
            "before": before,
            "after": after,
            "feedbackUsed": human_feedback,
            "changedFields": changed_fields,
            "draftChanged": draft_changed,
            "resolvedErrors": resolved_errors,
            "remainingErrors": [],
            "providerTimings": attempt.get("providerTimings") or [],
            **self._specialist_task_details(attempt),
        }

    def _save_package(self, path: Path, package: dict[str, Any]) -> None:
        path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _backup_file(self, path: Path) -> Path:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        relative = path.relative_to(self.config.workspace_root)
        backup_dir = self.config.backups_dir / relative.parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{path.stem}__{stamp}{path.suffix}"
        shutil.copy2(path, backup_path)
        return backup_path

    def _backup_live_snapshot(self, task_key: str, payload: dict[str, Any]) -> Path:
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        safe_name = task_key.replace("::", "__").replace("/", "_")
        backup_dir = self.config.backups_dir / "live-db"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{safe_name}__{stamp}.json"
        backup_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return backup_path

    def _write_reports(self) -> None:
        feed = self.feed_snapshot()
        health = self.reported_health_snapshot()
        (self.config.reports_dir / "status.json").write_text(
            json.dumps({"generatedAt": feed["generatedAt"], "counts": feed["counts"]}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.config.reports_dir / "feed.json").write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.config.reports_dir / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.config.reports_dir / "feed.md").write_text(self._feed_markdown(feed, health), encoding="utf-8")

    def _feed_markdown(self, feed: dict[str, Any], health: dict[str, Any]) -> str:
        lines = [
            "# Course Quality Control Center",
            "",
            f"Generated at: {feed['generatedAt']}",
            "",
            "## Runtime",
            "",
            f"- selected provider: {health['runtime']['selected'].get('provider')} ({health['runtime']['selected'].get('status')})",
            f"- detail: {health['runtime']['selected'].get('detail')}",
            f"- dashboard: {health['dashboard']['url']}",
            "",
            "## Counts",
            "",
        ]
        counts = feed.get("counts", {})
        if counts:
            for key in sorted(counts):
                lines.append(f"- {key}: {counts[key]}")
        else:
            lines.append("- no jobs yet")
        lines.extend(["", "## Coming Up", ""])
        lines.extend(self._section_lines(feed.get("queued", []), "No queued jobs."))
        lines.extend(["", "## Active Now", ""])
        lines.extend(self._section_lines(feed.get("running", []), "No running jobs."))
        lines.extend(["", "## Done Recently", ""])
        lines.extend(self._section_lines(feed.get("completed", []), "No completed jobs yet."))
        lines.extend(["", "## Failed", ""])
        lines.extend(self._section_lines(feed.get("failed", []), "No failed jobs."))
        lines.append("")
        return "\n".join(lines)

    def _section_lines(self, rows: list[dict[str, Any]], empty_message: str) -> list[str]:
        if not rows:
            return [f"- {empty_message}"]
        lines: list[str] = []
        for row in rows:
            target = row.get("questionUuid") or row.get("lessonId") or row.get("taskKey")
            prefix = f"- [{row.get('status')}] {row.get('courseId') or 'unknown-course'} / {row.get('lessonId') or '-'} / {target}"
            lines.append(prefix)
            judgement = row.get("details", {}).get("judgement") or {}
            if judgement:
                lines.append(f"  confidence: {judgement.get('confidence')} ({judgement.get('trustTier')})")
            if row.get("lastError"):
                lines.append(f"  error: {row['lastError']}")
            lines.append(f"  attempts: {row.get('attempts', 0)} | updated: {row.get('updatedAt')}")
        return lines


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Continuous quality worker for Amanoba course packages.")
    parser.add_argument("--config", required=True, help="Path to the daemon config JSON file.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("scan", help="Scan the workspace and refresh the task queue.")
    run_once = subparsers.add_parser("run-once", help="Scan, then process up to N items.")
    run_once.add_argument("--max-items", type=int, default=1)
    subparsers.add_parser("status", help="Print task counts.")
    feed = subparsers.add_parser("feed", help="Print the live job feed.")
    feed.add_argument("--limit", type=int, default=DEFAULT_FEED_LIMIT)
    subparsers.add_parser("health", help="Print runtime health.")
    subparsers.add_parser("watchdog", help="Run one watchdog supervision cycle.")
    dash = subparsers.add_parser("dashboard", help="Run the local web dashboard.")
    dash.add_argument("--host", default=None)
    dash.add_argument("--port", type=int, default=None)
    subparsers.add_parser("daemon", help="Run the scanner/worker loop continuously.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = Config.from_file(Path(args.config).resolve())
    daemon = CourseQualityDaemon(config, manage_worker_heartbeat=args.command in {"daemon", "run-once"})

    if args.command == "scan":
        print(json.dumps(daemon.scan(), ensure_ascii=False, indent=2))
        return
    if args.command == "run-once":
        lock_fd = acquire_process_lock(config.state_db_path.parent / "process.lock")
        if lock_fd is None:
            print(json.dumps({"busy": True, "reason": "another worker process is already active"}, ensure_ascii=False, indent=2))
            return
        try:
            scan_result = daemon.scan()
            processed: list[str] = []
            for _ in range(max(1, int(args.max_items))):
                outcome = daemon.process_one()
                if outcome == "idle":
                    break
                processed.append(outcome)
            print(json.dumps({"scan": scan_result, "processed": processed}, ensure_ascii=False, indent=2))
            return
        finally:
            release_process_lock(lock_fd)
    if args.command == "status":
        print(json.dumps(daemon.state.counts(), ensure_ascii=False, indent=2))
        return
    if args.command == "feed":
        print(json.dumps(daemon.feed_snapshot(limit=args.limit), ensure_ascii=False, indent=2))
        return
    if args.command == "health":
        print(json.dumps(daemon.health_snapshot(), ensure_ascii=False, indent=2))
        return
    if args.command == "watchdog":
        from .watchdog import run_watchdog

        run_watchdog(config.config_path)
        return
    if args.command == "dashboard":
        from .dashboard import run_dashboard

        run_dashboard(daemon, host=args.host or config.dashboard_host, port=args.port or config.dashboard_port)
        return
    lock_fd = acquire_process_lock(config.state_db_path.parent / "process.lock")
    if lock_fd is None:
        print(json.dumps({"busy": True, "reason": "another worker process is already active"}, ensure_ascii=False, indent=2))
        return
    try:
        daemon.run_daemon()
    finally:
        release_process_lock(lock_fd)
