"""
computeStatistics.py

Reads a text file with one value per line and computes:
- COUNT
- MEAN
- MEDIAN 
- MODE (or #N/A if there is no mode)
- Population Standard Deviation
- Population Variance

Usage:
    python computeStatistics.py fileWithData.txt

Outputs:
    - Prints results to console
    - Writes results to StatisticsResults.txt
"""

# pylint: disable=invalid-name

import sys
import time
from dataclasses import dataclass


RESULTS_FILE = "StatisticsResults.txt"


def _try_parse_number(raw: str):
    """
    Try to parse a number from a string.
    Supports:
      - integers and floats
      - comma decimals (e.g., 23,45 -> 23.45)
    Returns (success: bool, value: float|None).
    """
    text = raw.strip()
    if not text:
        return False, None

    # Normalize comma decimals
    text = text.replace(",", ".")

    try:
        value = float(text)
        return True, value
    except ValueError:
        return False, None


def _mean(values):
    total = 0.0
    count = 0
    for v in values:
        total += v
        count += 1
    return total / count if count > 0 else 0.0


def _median(sorted_values):
    n = len(sorted_values)
    if n == 0:
        return 0.0

    mid = n // 2
    if n % 2 == 1:
        return sorted_values[mid]

    return (sorted_values[mid - 1] + sorted_values[mid]) / 2.0


def _mode(values):
    """
    Returns (has_mode: bool, mode_value: float|None)

    Rule used for this assignment:
    - If max frequency <= 1 => no mode (#N/A)
    - If multiple values tie for max frequency => pick the one
      that appears FIRST in the input (earliest occurrence).
    """
    freq = {}
    first_pos = {}

    for idx, v in enumerate(values):
        freq[v] = freq.get(v, 0) + 1
        if v not in first_pos:
            first_pos[v] = idx

    max_count = 0
    for c in freq.values():
        max_count = max(max_count, c)

    if max_count <= 1:
        return False, None

    best_val = None
    best_first = None

    for v, c in freq.items():
        if c == max_count:
            pos = first_pos[v]
            if best_first is None or pos < best_first:
                best_first = pos
                best_val = v

    return True, best_val


def _population_variance(values, mean_val):
    n = len(values)
    if n == 0:
        return 0.0

    acc = 0.0
    for v in values:
        diff = v - mean_val
        acc += diff * diff

    return acc / n


def _population_std(variance_val):
    return variance_val ** 0.5

def _format_number(x):
    """
    Format numbers similar to typical spreadsheet output:
    - If it's an integer-like float, show without trailing.
    - Otherwise show up to 10 decimals trimmed.
    For simplicity and consistency: print with up to 10 decimals, removing trailing zeros.
    """
    # Keep high precision but readable
    s = f"{x:.10f}".rstrip("0").rstrip(".")
    return s if s else "0"


@dataclass(frozen=True)
class StatisticsResult:
    """Container for computed statistics and elapsed time."""
    count: int
    mean: float
    median: float
    mode: str
    sd: float
    variance: float
    elapsed: float


def _build_report(result: StatisticsResult):
    lines = []
    lines.append(f"COUNT: {result.count}")
    lines.append(f"MEAN: {_format_number(result.mean)}")
    lines.append(f"MEDIAN: {_format_number(result.median)}")
    lines.append(f"MODE: {result.mode}")
    lines.append(f"SD (Population): {_format_number(result.sd)}")
    lines.append(f"VARIANCE (Population): {_format_number(result.variance)}")
    lines.append(f"TIME (seconds): {_format_number(result.elapsed)}")
    return "\n".join(lines) + "\n"


def _read_values(file_path):
    values = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            line_num = 0
            for raw_line in f:
                line_num += 1
                ok, val = _try_parse_number(raw_line)
                if ok:
                    values.append(val)
                else:
                    bad = raw_line.strip()
                    if bad:
                        print(
                            f"Invalid data at line {line_num}: '{bad}' "
                            f"(ignored, continuing)"
                        )
    except FileNotFoundError:
        print(f"Error: file not found -> {file_path}")
        return None
    except OSError as exc:
        print(f"Error: cannot read file -> {file_path}. Details: {exc}")
        return None
    return values


def _compute_statistics(values, elapsed):
    values_sorted = sorted(values)

    mean_val = _mean(values)
    median_val = _median(values_sorted)

    has_mode, mode_val = _mode(values)
    mode_str = _format_number(mode_val) if has_mode else "#N/A"

    var_val = _population_variance(values, mean_val)
    sd_val = _population_std(var_val)

    return StatisticsResult(
        count=len(values),
        mean=mean_val,
        median=median_val,
        mode=mode_str,
        sd=sd_val,
        variance=var_val,
        elapsed=elapsed,
    )


def main():
    """Command-line entry point."""
    start = time.time()

    if len(sys.argv) != 2:
        print("Usage: python computeStatistics.py fileWithData.txt")
        return 1

    file_path = sys.argv[1]
    values = _read_values(file_path)
    if values is None:
        return 1

    if not values:
        print("Error: no valid numeric data found in the file.")
        return 1

    elapsed = time.time() - start
    report = _build_report(_compute_statistics(values, elapsed))

    # Print to console
    print(report, end="")

    # Write to file
    try:
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as exc:
        print(f"Warning: could not write '{RESULTS_FILE}'. Details: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
