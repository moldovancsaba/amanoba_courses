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

