from __future__ import annotations

from typing import Any


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def trust_tier(confidence: float) -> str:
    if confidence >= 0.75:
        return "HIGH"
    if confidence >= 0.5:
        return "MEDIUM"
    return "LOW"


def confidence_for_validation(kind: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    base = 0.92 if kind == "question" else 0.82
    confidence = base - (0.12 * len(errors)) - (0.04 * len(warnings))
    return {
        "confidence": round(clamp01(confidence), 2),
        "trustTier": trust_tier(clamp01(confidence)),
        "vote": "REWRITE" if errors else "ACCEPT",
        "reason": f"{len(errors)} error(s), {len(warnings)} warning(s).",
    }


def confidence_for_completion(provider: str, warnings: list[str]) -> dict[str, Any]:
    provider_bonus = {
        "ollama": 0.78,
        "mlx": 0.72,
        "llamacpp": 0.74,
        "openai": 0.84,
        "none": 0.15,
    }.get(provider, 0.6)
    confidence = provider_bonus - (0.05 * len(warnings))
    confidence = clamp01(confidence)
    return {
        "confidence": round(confidence, 2),
        "trustTier": trust_tier(confidence),
        "vote": "ACCEPT" if confidence >= 0.5 else "REVIEW",
        "reason": f"Provider={provider}; warnings={len(warnings)}.",
    }
