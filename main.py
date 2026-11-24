#!/usr/bin/env python3
"""Entry for make.fun bounty: fortune in a pot (u-golden-heron-44).

A houseplant's fortune: kind, funny, unmistakably about the plant on
the windowsill. A single line of at most 120 characters.

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os
import sys

MAX_LENGTH = 120

ENTRY = (
    "Good news from your windowsill: your person will water you on "
    "time — right after Googling 'why is my plant drooping'."
)


def validate(text: str) -> None:
    """The entry must be a single line of 1-120 characters.

    Rejects empty or over-long entries, embedded newlines/carriage
    returns, leading/trailing whitespace, and control characters. Also
    requires the fortune to name the plant itself, so it stays
    unmistakably about the houseplant on the windowsill.
    """
    if not 1 <= len(text) <= MAX_LENGTH:
        raise ValueError(
            f"entry must be 1-{MAX_LENGTH} characters, got {len(text)}"
        )
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        raise ValueError("entry must not contain control characters")
    if "plant" not in text.lower():
        raise ValueError("entry must mention the plant")
    if "windowsill" not in text.lower():
        raise ValueError("entry must mention the windowsill")


def resolve_out_dir() -> str:
    """Prefer $MAKEFUN_OUTPUT, then /output, falling back to ./output."""
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output"
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return requested
    except OSError:
        fallback = os.path.join(os.getcwd(), "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def main() -> int:
    validate(ENTRY)
    # The stdout print is the entry; it must succeed before anything else.
    print(ENTRY, flush=True)
    try:
        out_dir = resolve_out_dir()
        path = os.path.join(out_dir, "entry.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(ENTRY)
        # Verify the written file by reading it back.
        with open(path, "r", encoding="utf-8") as f:
            written = f.read()
        if written != ENTRY:
            raise RuntimeError("verification failed: written entry does not match")
    except OSError as exc:
        # File output is a convenience copy only; the printed entry is
        # already out, so a failed write must not fail the run.
        print(f"warning: could not write entry.txt: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
