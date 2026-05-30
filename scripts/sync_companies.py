#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "validated_companies.csv"
DEFAULT_OUTPUT = ROOT / "companies.csv"


def sync_companies(input_path: Path, output_path: Path) -> int:
    if not input_path.exists():
        print(f"Missing input file: {input_path}")
        return 1

    rows = []
    seen_urls: set[str] = set()

    with input_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            company = row["company"].strip()
            career_url = row["career_url"].strip()
            source = row["source"].strip()

            if not company or not career_url or not source:
                continue
            if career_url in seen_urls:
                continue

            seen_urls.add(career_url)
            rows.append(
                {
                    "company": company,
                    "career_url": career_url,
                    "source": source,
                }
            )

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["company", "career_url", "source"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} companies to {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync validated_companies.csv into companies.csv"
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return sync_companies(args.input, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
