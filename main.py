#!/usr/bin/env python3
"""A houseplant fortune for the make.fun bounty "fortune in a pot".

The fortune is a single kind, funny line spoken to the plant on the
windowsill, never more than 120 characters. The program prints it to
stdout, saves a copy as entry.txt, and reads that copy back to prove
it matches what was printed. Deterministic and stdlib only: no
network access, no clock, no randomness.
"""

import os
import sys
import tempfile

MAX_CHARS = 120
MIN_CHARS = 1
ENTRY_FILE = "entry.txt"

# The fortune itself, exactly as it must be printed.
FORTUNE = (
    "Good news from your windowsill: your person will water you on "
    "time — right after Googling 'why is my plant drooping'."
)

# Words the fortune has to contain so it stays about the plant.
REQUIRED_WORDS = ("plant", "windowsill", "water")


def check_length(text: str) -> None:
    """The fortune must be between 1 and 120 characters long."""
    length = len(text)
    if length < MIN_CHARS:
        raise ValueError("fortune rejected: empty entry")
    if length > MAX_CHARS:
        raise ValueError(
            f"fortune rejected: {length} characters, limit is {MAX_CHARS}"
        )


def check_single_line(text: str) -> None:
    """One line only: no newlines, carriage returns or control chars."""
    if "\n" in text or "\r" in text:
        raise ValueError("fortune rejected: entry spans more than one line")
    if text != text.strip():
        raise ValueError("fortune rejected: leading or trailing whitespace")
    for char in text:
        code = ord(char)
        if code < 0x20 or code == 0x7F:
            raise ValueError("fortune rejected: control character found")


def check_subject(text: str) -> None:
    """The fortune must stay about the plant on the windowsill."""
    lowered = text.lower()
    for word in REQUIRED_WORDS:
        if word not in lowered:
            raise ValueError(f"fortune rejected: missing word {word!r}")


def check_quotes(text: str) -> None:
    """Quoted speech inside the fortune must be balanced."""
    if text.count("'") % 2 != 0:
        raise ValueError("fortune rejected: unbalanced single quotes")


def check_ending(text: str) -> None:
    """The fortune must end with terminal punctuation, not trail off."""
    if text[-1] not in ".!?":
        raise ValueError("fortune rejected: entry must end with . ! or ?")


def check_fortune(text: str) -> None:
    """Run every validation rule over the fortune."""
    check_length(text)
    check_single_line(text)
    check_subject(text)
    check_quotes(text)
    check_ending(text)


def _directory_is_writable(directory: str) -> bool:
    """Probe whether a directory accepts a file, then clean up."""
    probe = os.path.join(directory, ".write_probe")
    try:
        os.makedirs(directory, exist_ok=True)
        with open(probe, "w", encoding="utf-8") as handle:
            handle.write("ok")
    except OSError:
        return False
    try:
        os.remove(probe)
    except OSError:
        pass
    return True


def choose_output_dir() -> str:
    """Pick where entry.txt goes.

    Tries $MAKEFUN_OUTPUT first, then /output, then ./output, and
    finally the system temp directory as a last resort.
    """
    candidates = [
        os.environ.get("MAKEFUN_OUTPUT"),
        "/output",
        os.path.join(os.getcwd(), "output"),
        tempfile.gettempdir(),
    ]
    for candidate in candidates:
        if candidate and _directory_is_writable(candidate):
            return candidate
    raise OSError("no writable output directory found")


def save_copy(text: str, directory: str) -> str:
    """Write entry.txt and read it back to prove it matches."""
    path = os.path.join(directory, ENTRY_FILE)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    with open(path, "r", encoding="utf-8") as handle:
        stored = handle.read()
    if stored != text:
        raise RuntimeError("verification failed: entry.txt does not match")
    return path


def main() -> int:
    """Validate the fortune, print it, then store a verified copy."""
    check_fortune(FORTUNE)
    # Stdout is the entry itself; print it before anything else so a
    # later file failure can never swallow it.
    print(FORTUNE, flush=True)
    try:
        directory = choose_output_dir()
        try:
            path = save_copy(FORTUNE, directory)
        except RuntimeError:
            # The copy did not verify: try once more in the temp dir
            # before giving up on the file copy.
            path = save_copy(FORTUNE, tempfile.gettempdir())
    except OSError as exc:
        # entry.txt is a convenience copy only. The fortune is already
        # printed, so a failed write warns instead of failing the run.
        print(f"warning: could not save entry.txt: {exc}", file=sys.stderr)
        return 0
    print(f"saved verified copy to {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
