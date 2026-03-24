# Lesson 12: Tool calling dan actions

**One-liner:** Hubungkan model ke tools dan batasi actions yang berisiko.  
**Time:** 20 hingga 30 menit  
**Deliverable:** Tool Schema dan Contoh Action

## Learning goal

You will be able to: **Menentukan tool schema dan menjalankan tool call yang aman.**

### Success criteria (observable)
- [ ] Tool schema mencakup nama, input, dan bentuk output.
- [ ] Tool call berjalan dengan contoh nyata.
- [ ] Action berisiko diblokir.

### Output you will produce
- **Deliverable:** Tool Schema dan Contoh Action
- **Format:** JSON schema dan test log
- **Where saved:** Di folder kursus dalam `/generative-ai-2026-build-ai-apps-and-agents-id/`

## Who

**Primary persona:** Digital nomad yang membangun AI dengan tools
**Secondary persona(s):** Pengguna yang memicu action
**Stakeholders (optional):** Mitra pembangunan

## What

### What it is
Definisi tool yang menjelaskan apa yang bisa dipanggil model dan bagaimana.
Contoh kecil yang membuktikan tool call berjalan sesuai harapan.

### What it is not
Bukan platform otomatisasi penuh.
Bukan sistem izin yang kompleks.

### 2-minute theory
- Tool calling membuat AI berguna di luar teks.
- Schema jelas mengurangi error input.
- Guardrails mencegah action berbahaya.

### Key terms
- **Tool schema:** Definisi terstruktur untuk input dan output tool.
- **Guardrail:** Aturan untuk mencegah action berisiko.

## Where

### Applies in
- Agent workflows
- Backend services

### Does not apply in
- Konten statis tanpa action

### Touchpoints
- Tool definitions
- Action logs
- Permission checks

## When

### Use it when
- Anda ingin AI memicu action
- Anda butuh input yang konsisten

### Frequency
Setiap menambah tool baru

### Late signals
- Tool call sering gagal karena input buruk
- Action tidak terduga terjadi

## Why it matters

### Practical benefits
- AI lebih berguna
- Automasi lebih stabil
- Keamanan dan kepercayaan meningkat

### Risks of ignoring
- Workflow rusak
- Action berbahaya terjadi

### Expectations
- Improves: keandalan dan keamanan
- Does not guarantee: keputusan sempurna

## How

### Step-by-step method
1. Tentukan nama tool dan tujuannya.
2. Definisikan input fields dan types.
3. Tentukan bentuk output.
4. Tambahkan guardrails untuk action berisiko.
5. Jalankan test call dan catat hasil.

### Do and don't

**Do**
- Validasi input sebelum eksekusi
- Log setiap action

**Don't**
- Menjalankan tool tanpa checks
- Membuka action berbahaya secara default

### Common mistakes and fixes
- **Mistake:** Schema terlalu longgar. **Fix:** Tambah field wajib dan types.
- **Mistake:** Tidak ada guardrails. **Fix:** Blokir parameter berisiko.

### Done when
- [ ] Tool schema didefinisikan dan diuji.
- [ ] Guardrails memblokir input berisiko.
- [ ] Log menunjukkan call berhasil.

## Guided exercise (10 to 15 min)

### Inputs
- Satu ide tool
- Contoh input

### Steps
1. Tulis tool schema.
2. Tambahkan guardrails untuk input berisiko.
3. Jalankan test call dan catat output.

### Output format
| Field | Value |
|---|---|
| Tool name | |
| Input schema | |
| Guardrails | |
| Test result | |

> **Pro tip:** Jika tool bisa mengubah data, tambahkan langkah konfirmasi.

## Independent exercise (5 to 10 min)

### Task
Tambahkan satu guardrail lagi dan ulangi test.

### Output
Schema yang diperbarui dan test log baru.

## Self-check (yes/no)

- [ ] Apakah schema jelas dan typed?
- [ ] Apakah action berisiko diblokir?
- [ ] Apakah test call tercatat?
- [ ] Apakah log disimpan?

### Baseline metric (recommended)
- **Score:** 1 tool call sukses dengan guardrails
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Tools Guide**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs/guides/tools

2. **OWASP API Security Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/www-project-api-security/

## Read more (optional)

1. **Function Calling Best Practices**
   Why: Pola aman untuk tool calling.
   Read: https://platform.openai.com/docs/guides/tools
