# pylint: disable=invalid-name
"""
convertNumbers.py

Reads a text file with one integer per line and converts each number to:
- Binary
- Hexadecimal

Rules:
- Input is a text file with one value per line.
- Invalid data must be reported and ignored (execution continues).
- Output is printed to console and written to ConversionResults.txt.
- All computation must be done using basic algorithms (no bin(), hex(), format()).
- Includes elapsed time at the end.

Negative numbers:
- Binary is represented in 10-bit two's complement (as shown in expected results).
- Hex is sign-extended to 10 hex digits using 'F' (as shown in expected results).
    Example: -6 -> BIN 1111111010, HEX FFFFFFFFFA.

Usage:
    python convertNumbers.py fileWithData.txt
"""

import sys
import time

RESULTS_FILE = "ConversionResults.txt"

BIN_NEG_BITS = 10
HEX_NEG_DIGITS = 10  # 10 hex digits = 40 bits of sign-extension


def _parse_int(line: str):
    """Parse a line as integer. Returns (ok, value_or_none)."""
    text = line.strip()
    if not text:
        return False, None

    # Optional leading +/-
    sign = 1
    if text[0] in "+-":
        if text[0] == "-":
            sign = -1
        text = text[1:]

    if not text:
        return False, None

    # Ensure all digits
    for ch in text:
        if ch < "0" or ch > "9":
            return False, None

    # Manual base-10 parse
    value = 0
    for ch in text:
        digit = ord(ch) - ord("0")
        value = value * 10 + digit

    return True, sign * value


def _to_binary_nonneg(n: int) -> str:
    """Convert n >= 0 to binary using repeated division."""
    if n == 0:
        return "0"

    bits = []
    x = n
    while x > 0:
        bits.append("1" if (x % 2) == 1 else "0")
        x //= 2

    bits.reverse()
    return "".join(bits)


def _to_hex_nonneg(n: int) -> str:
    """Convert n >= 0 to uppercase hex using repeated division."""
    if n == 0:
        return "0"

    digits = "0123456789ABCDEF"
    out = []
    x = n
    while x > 0:
        out.append(digits[x % 16])
        x //= 16

    out.reverse()
    return "".join(out)


def _to_twos_complement_binary_10bit(n: int) -> str:
    """
    n is negative.
    Represent in BIN_NEG_BITS two's complement:
      value = 2^bits + n
    """
    base = 1 << BIN_NEG_BITS
    val = base + n  # since n < 0
    # val should be in [0, 2^bits - 1] for expected test ranges
    b = _to_binary_nonneg(val)

    # Pad left with zeros to fixed width
    if len(b) < BIN_NEG_BITS:
        b = ("0" * (BIN_NEG_BITS - len(b))) + b
    return b


def _to_sign_extended_hex_10digits_from_bin(bin_10: str) -> str:
    """
    Expected format for negatives shows 10 hex digits with leading 'F's,
    and the last hex digits match the low bits (e.g., -6 => ...FA).

    We can compute the numeric value of the 10-bit pattern and convert to hex,
    then sign-extend with 'F' to 10 digits.
    """
    # Convert 10-bit binary to integer manually
    val = 0
    for ch in bin_10:
        val = val * 2 + (1 if ch == "1" else 0)

    low_hex = _to_hex_nonneg(val)

    # Left pad to at least 2 hex digits (so -6 ends with FA, -39 ends with D9)
    if len(low_hex) < 2:
        low_hex = ("0" * (2 - len(low_hex))) + low_hex

    # Sign-extension: pad with 'F' up to HEX_NEG_DIGITS
    if len(low_hex) < HEX_NEG_DIGITS:
        low_hex = ("F" * (HEX_NEG_DIGITS - len(low_hex))) + low_hex

    return low_hex


def _convert_number(n: int):
    """Return (bin_str, hex_str) according to rules."""
    if n >= 0:
        return _to_binary_nonneg(n), _to_hex_nonneg(n)

    bin_10 = _to_twos_complement_binary_10bit(n)
    hex_10 = _to_sign_extended_hex_10digits_from_bin(bin_10)
    return bin_10, hex_10


def _read_rows(file_path: str):
    """Read file and return (rows, error_message_or_none)."""
    rows = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            line_num = 0
            for raw in f:
                line_num += 1
                ok, val = _parse_int(raw)
                if not ok:
                    bad = raw.strip()
                    if bad:
                        print(f"Invalid data at line {line_num}: '{bad}' (ignored)")
                    continue

                bin_s, hex_s = _convert_number(val)
                rows.append((val, bin_s, hex_s))
    except FileNotFoundError:
        return None, f"Error: file not found -> {file_path}"
    except OSError as exc:
        return None, f"Error: cannot read file -> {file_path}. Details: {exc}"

    return rows, None


def _build_report(rows, elapsed: float) -> str:
    """Build output report string."""
    lines = ["ITEM\tVALUE\tBIN\tHEX"]
    for idx, (val, bin_s, hex_s) in enumerate(rows, start=1):
        lines.append(f"{idx}\t{val}\t{bin_s}\t{hex_s}")

    time_line = f"TIME (seconds): {elapsed:.10f}".rstrip("0").rstrip(".")
    lines.append(time_line)
    return "\n".join(lines) + "\n"


def main() -> int:
    """Program entry point."""
    start = time.time()

    if len(sys.argv) != 2:
        print("Usage: python convertNumbers.py fileWithData.txt")
        return 1

    file_path = sys.argv[1]
    rows, error = _read_rows(file_path)
    if error:
        print(error)
        return 1

    elapsed = time.time() - start

    report = _build_report(rows, elapsed)

    # Print + save
    print(report, end="")
    try:
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            f.write(report)
    except OSError as exc:
        print(f"Warning: could not write '{RESULTS_FILE}'. Details: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
