"""Check SQL answers; --strict exits 1 unless every answer is correct.

Usage: python practice/check.py [answers.sql] [--strict]
Without --strict, incomplete or incorrect answers still print a score and exit 0.
Input/setup errors exit 1; invalid command-line arguments exit 2.
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path


def split(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^--\s*(Q\d+)\b.*$", text, flags=re.M)
    out = {}
    for i in range(1, len(parts), 2):
        body = "\n".join(line for line in parts[i + 1].splitlines() if not line.strip().startswith("--")).strip()
        out[parts[i]] = body
    return out


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answers", nargs="?", type=Path, default=here / "my_answers.sql")
    parser.add_argument("--strict", action="store_true", help="Exit 1 unless every answer is correct")
    args = parser.parse_args(argv)
    db = here / "school.db"
    if not db.exists():
        print("school.db not found - run: python practice/make_school_db.py", file=sys.stderr)
        return 1
    try:
        mine = split(args.answers)
        ref = json.loads((here / "expected.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Cannot read checker input: {exc}", file=sys.stderr)
        return 1

    score = 0
    try:
        con = sqlite3.connect(db)
    except sqlite3.Error as exc:
        print(f"Cannot open school.db: {exc}", file=sys.stderr)
        return 1
    try:
        for q in sorted(ref, key=lambda k: int(k[1:])):
            sql = mine.get(q, "")
            if not sql:
                print(f"{q:4} ..  not answered yet")
                continue
            try:
                got = [list(row) for row in con.execute(sql).fetchall()]
            except sqlite3.Error as exc:
                print(f"{q:4} ERR {exc}")
                continue
            want, ordered = ref[q]["rows"], ref[q]["ordered"]
            same = got == want if ordered else sorted(map(repr, got)) == sorted(map(repr, want))
            score += same
            detail = "" if same else f"expected {want[:3]}{' ...' if len(want) > 3 else ''}, got {got[:3]}"
            print(f"{q:4} {'OK ' if same else 'NO '} " + detail)
    finally:
        con.close()
    print(f"\nScore: {score}/{len(ref)}")
    return int(args.strict and score != len(ref))


if __name__ == "__main__":
    raise SystemExit(main())
