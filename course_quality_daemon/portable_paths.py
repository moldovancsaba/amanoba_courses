from __future__ import annotations

import os
from pathlib import Path


def _remap_home_prefix(path: Path) -> Path:
    parts = path.parts
    if len(parts) >= 4 and parts[0] == os.sep and parts[1] == "Users":
        try:
            home = Path.home().resolve()
        except Exception:
            home = Path.home()
        return home.joinpath(*parts[3:])
    return path


def resolve_portable_path(value: str | Path | None, *, base_dir: Path | None = None) -> Path:
    text = str(value or "").strip()
    if not text:
        return Path()
    expanded = os.path.expandvars(os.path.expanduser(text))
    candidate = Path(expanded)
    if not candidate.is_absolute():
        if base_dir is not None:
            candidate = (base_dir / candidate).resolve()
        else:
            candidate = candidate.resolve()
    if candidate.exists():
        return candidate
    remapped = _remap_home_prefix(candidate)
    if remapped.exists():
        return remapped
    return remapped if remapped != candidate else candidate


def resolve_mlx_model_path(value: str | Path | None, *, base_dir: Path | None = None, label: str | None = None) -> Path:
    candidate = resolve_portable_path(value, base_dir=base_dir)
    if candidate.exists():
        return candidate

    search_terms: list[str] = []
    for raw in (str(value or ""), str(label or "")):
        lowered = raw.lower()
        if "gemma-3-270m" in lowered:
            search_terms.append("gemma-3-270m")
        if "granite-4.0-h-350m" in lowered:
            search_terms.append("granite-4.0-h-350m")
        if "qwen2.5-0.5b" in lowered:
            search_terms.append("qwen2.5-0.5b")
        if "apertus-8b-instruct-2509" in lowered:
            search_terms.append("apertus-8b-instruct-2509")

    if not search_terms:
        return candidate

    cache_root = Path.home() / ".cache" / "huggingface" / "hub"
    if not cache_root.exists():
        return candidate

    matches: list[Path] = []
    for repo_dir in sorted(cache_root.glob("models--*")):
        repo_name = repo_dir.name.lower()
        if not any(term in repo_name for term in search_terms):
            continue
        snapshots = [path for path in sorted((repo_dir / "snapshots").glob("*")) if path.is_dir()]
        matches.extend(snapshots)

    if matches:
        try:
            matches.sort(key=lambda item: item.stat().st_mtime)
        except OSError:
            matches.sort()
        return matches[-1]

    return candidate
