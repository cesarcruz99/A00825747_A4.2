# pylint: disable=invalid-name

"""
wordCount.py

Reads a text file and counts distinct words and their frequency.

Rules:
- Input file contains words separated by whitespace.
- Invalid data must be reported and ignored (execution continues).
- Output is printed to console and written to WordCountResults.txt.
- Computation uses basic algorithms (no specialized libraries).
- Includes elapsed time at the end.

Usage:
    python wordCount.py fileWithData.txt
"""

import sys
import time

RESULTS_FILE = "WordCountResults.txt"


def _tokenize(text: str):
    """
    Tokenize text into words using basic character scanning.
    Words are sequences of non-whitespace characters.
    """
    words = []
    current = []

    for ch in text:
        if ch.isspace():
            if current:
                words.append("".join(current))
                current = []
        else:
            current.append(ch)

    if current:
        words.append("".join(current))

    return words


def _count_words(words):
    """
    Count frequencies using basic dictionary logic.
    Returns:
      counts: dict[word] -> int
      order: list of words in first-appearance order (deterministic output)
    """
    counts = {}
    order = []

    for w in words:
        if w in counts:
            counts[w] += 1
        else:
            counts[w] = 1
            order.append(w)

    return counts, order


def _build_report(counts, order, elapsed):
    lines = []
    lines.append("WORD\tCOUNT")

    for w in order:
        lines.append(f"{w}\t{counts[w]}")

    lines.append(f"TIME (seconds): {elapsed:.10f}".rstrip("0").rstrip("."))
    return "\n".join(lines) + "\n"


def main() -> int:
    """Run word counting flow and return exit code."""
    start = time.time()

    if len(sys.argv) != 2:
        print("Usage: python wordCount.py fileWithData.txt")
        return 1

    file_path = sys.argv[1]
    all_words = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            line_num = 0
            for raw_line in f:
                line_num += 1
                line = raw_line.strip("\n")

                # Consider empty lines as "invalid" / ignorable input
                if not line.strip():
                    print(f"Invalid data at line {line_num}: empty line (ignored)")
                    continue

                words = _tokenize(line)
                if not words:
                    print(f"Invalid data at line {line_num}: no words (ignored)")
                    continue

                for w in words:
                    all_words.append(w)

    except FileNotFoundError:
        print(f"Error: file not found -> {file_path}")
        return 1
    except OSError as exc:
        print(f"Error: cannot read file -> {file_path}. Details: {exc}")
        return 1

    elapsed = time.time() - start

    counts, order = _count_words(all_words)
    report = _build_report(counts, order, elapsed)

    print(report, end="")

    try:
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as exc:
        print(f"Warning: could not write '{RESULTS_FILE}'. Details: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
