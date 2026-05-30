#!/usr/bin/env python3
import argparse
import csv
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import REQUEST_TIMEOUT, USER_AGENT

CANDIDATES_FILE = ROOT / "candidate_companies.csv"
OUTPUT_FILE = ROOT / "validated_companies.csv"

HEADERS = {"User-Agent": USER_AGENT}


def try_greenhouse(slug: str) -> dict | None:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)

    if response.status_code != 200:
        return None

    data = response.json()
    if "jobs" not in data:
        return None

    return {
        "source": "greenhouse",
        "career_url": f"https://boards.greenhouse.io/{slug}",
        "job_count": len(data.get("jobs", [])),
    }


def try_lever(slug: str) -> dict | None:
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)

    if response.status_code != 200:
        return None

    data = response.json()
    if not isinstance(data, list):
        return None

    return {
        "source": "lever",
        "career_url": f"https://jobs.lever.co/{slug}",
        "job_count": len(data),
    }


def try_ashby(slug: str) -> dict | None:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=HEADERS)

    if response.status_code != 200:
        return None

    data = response.json()
    jobs = data.get("jobs", [])

    return {
        "source": "ashby",
        "career_url": f"https://jobs.ashbyhq.com/{slug}",
        "job_count": len(jobs),
    }


def validate_company(company: str, slug: str) -> dict | None:
    checks = [try_greenhouse, try_lever, try_ashby]

    for check in checks:
        try:
            result = check(slug)
            if result and result["job_count"] > 0:
                return {
                    "company": company,
                    "career_url": result["career_url"],
                    "source": result["source"],
                    "job_count": result["job_count"],
                }
        except Exception:
            continue

    return None


def load_candidates(path: Path) -> list[tuple[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if "company" not in reader.fieldnames or "slug" not in reader.fieldnames:
            raise ValueError(f"{path} must have columns: company, slug")

        rows = []
        seen_slugs: set[str] = set()

        for row in reader:
            company = row["company"].strip()
            slug = row["slug"].strip().lower()
            if not company or not slug:
                continue
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            rows.append((company, slug))

        return rows


def write_validated(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["company", "career_url", "source", "job_count"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate company ATS slugs.")
    parser.add_argument(
        "--candidates",
        type=Path,
        default=CANDIDATES_FILE,
        help="CSV with company,slug columns",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help="Where to write validated companies",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Also update companies.csv from validated results",
    )
    args = parser.parse_args()

    if not args.candidates.exists():
        print(f"Missing candidates file: {args.candidates}")
        return 1

    valid_rows = []
    skipped = 0

    for company, slug in load_candidates(args.candidates):
        result = validate_company(company, slug)
        if result:
            print(
                f"[ok] {company}: {result['source']} "
                f"({result['job_count']} jobs)"
            )
            valid_rows.append(result)
        else:
            print(f"[skip] {company}: no valid ATS found")
            skipped += 1

    write_validated(valid_rows, args.output)
    print(f"\nSaved {len(valid_rows)} valid companies to {args.output}")
    print(f"Skipped {skipped} companies")

    if args.sync:
        if not valid_rows:
            print("\nNo valid companies to sync; companies.csv unchanged.")
            return 1

        sync_script = Path(__file__).with_name("sync_companies.py")
        import subprocess

        cmd = [sys.executable, str(sync_script), "--input", str(args.output)]
        print("\nSyncing companies.csv...")
        return subprocess.call(cmd)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
