"""Unsent micro-confession entry.

Writes one two-part micro-confession to /output/entry.txt (or
$MAKEFUN_OUTPUT_DIR/entry.txt when that variable is set): a To: line
naming who it was meant for, and the unsent message itself, one line,
exactly as it was typed, with no explanation after it.

The text is a fixed constant; the surrounding code normalises,
validates and writes it deterministically. No network access, no
reading of files outside this repository. Output is byte-identical
on every run.
"""

import os
import sys

# The confession, exactly as submitted. The To: line and the message
# need each other: the confession is about one summer, one red bike,
# one person — and one specific thing done to it that only the rider
# would know. The trailing newline is appended by write_entry(),
# never baked into the constant.
CONFESSION_LINES = [
    "To: Marcus",
    "I never told you I snapped the chain on your red bike the summer we were twelve, and I let you blame the kid next door.",
]

MIN_CHARS = 1
MAX_CHARS = 260
MAX_MESSAGE_CHARS = 200
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.txt")


def normalise(lines):
    """Join lines with LF, strip trailing blank lines, add one newline."""
    text = "\n".join(lines)
    text = text.rstrip("\n")
    return text + "\n"


def validate(text):
    """Check the confession meets the competition's format rules."""
    if not isinstance(text, str):
        raise ValueError("confession must be a string")
    if len(text) < MIN_CHARS or len(text) > MAX_CHARS:
        raise ValueError(
            "confession must be %d-%d chars, got %d"
            % (MIN_CHARS, MAX_CHARS, len(text))
        )
    text.encode("utf-8")
    if not text.strip():
        raise ValueError("confession must not be only white space")
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise ValueError("confession must end with exactly one trailing newline")
    if "\r" in text:
        raise ValueError("confession must use LF line endings only")
    lines = text.rstrip("\n").split("\n")
    if len(lines) != 2:
        raise ValueError("confession must have exactly two lines, got %d" % len(lines))
    if not lines[0].startswith("To: "):
        raise ValueError("first line must start with 'To: '")
    if len(lines[1]) > MAX_MESSAGE_CHARS:
        raise ValueError(
            "message line must be at most %d chars, got %d"
            % (MAX_MESSAGE_CHARS, len(lines[1]))
        )
    return True


def summarise(text):
    """Return a small report about the confession: lines, chars, bytes."""
    lines = text.rstrip("\n").split("\n")
    return {
        "lines": len(lines),
        "to_chars": len(lines[0]),
        "message_chars": len(lines[1]),
        "chars": len(text),
        "bytes": len(text.encode("utf-8")),
    }


def build_confession():
    """Return the normalised confession text."""
    return normalise(CONFESSION_LINES)


def write_entry(path=OUTPUT_PATH):
    """Validate the confession and write it to path, creating dirs as needed."""
    text = build_confession()
    validate(text)
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return path


def main(argv=None):
    """Entry point: write the confession and report its size."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) > 1:
        raise ValueError("at most one argument (output path) is accepted")
    if argv and argv[0] in ("--check", "--report"):
        info = summarise(build_confession())
        print(
            "confession: %(lines)d lines, To: %(to_chars)d chars, "
            "message %(message_chars)d chars, "
            "%(chars)d chars total, %(bytes)d bytes" % info
        )
        return 0
    path = argv[0] if argv else OUTPUT_PATH
    written = write_entry(path)
    size = os.path.getsize(written)
    print("wrote %s (%d bytes)" % (written, size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
