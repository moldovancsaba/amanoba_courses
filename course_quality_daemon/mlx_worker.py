from __future__ import annotations

import argparse
import sys


def _fail(message: str) -> int:
    sys.stderr.write(message.strip() + "\n")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Isolated MLX text generation worker.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-tokens", required=True, type=int)
    args = parser.parse_args()

    prompt = sys.stdin.read()
    if not prompt.strip():
        return _fail("MLX worker failed: prompt is required on stdin.")

    try:
        from mlx_lm import generate, load
    except Exception as exc:
        return _fail(f"MLX worker import failed: {exc}")

    try:
        model, tokenizer = load(args.model)
    except Exception as exc:
        return _fail(f"MLX worker model load failed: {exc}")

    messages = [{"role": "user", "content": prompt}]
    try:
        if hasattr(tokenizer, "apply_chat_template"):
            rendered_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            rendered_prompt = prompt
        text = generate(model, tokenizer, prompt=rendered_prompt, max_tokens=int(args.max_tokens), verbose=False)
    except Exception as exc:
        return _fail(f"MLX worker generation failed: {exc}")

    text = str(text or "").strip()
    if not text:
        return _fail("MLX worker generation failed: empty response.")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
