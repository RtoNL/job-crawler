#!/usr/bin/env python3
from pathlib import Path

import pandas as pd

from config import ENTRY_LEVEL_ONLY
from crawlers.base import Job
from crawlers.registry import crawl_company
from filters import is_entry_level_job
from storage import (
    is_baseline_run,
    load_seen_jobs,
    save_outputs,
    split_new_jobs,
    update_seen_jobs,
)


def load_companies(path: Path) -> list[dict]:
    df = pd.read_csv(path)
    required = {"company", "career_url", "source"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"companies.csv missing columns: {', '.join(sorted(missing))}")

    companies = []
    for row in df.to_dict("records"):
        companies.append(
            {
                "company": str(row["company"]).strip(),
                "career_url": str(row["career_url"]).strip(),
                "source": str(row["source"]).strip(),
            }
        )
    return companies


def filter_entry_level_jobs(jobs: list[Job]) -> list[Job]:
    return [
        job
        for job in jobs
        if is_entry_level_job(job.title, job.description or "")
    ]


def main() -> int:
    companies_path = Path("companies.csv")
    if not companies_path.exists():
        print("companies.csv not found. Create it first.")
        return 1

    companies = load_companies(companies_path)
    seen_df = load_seen_jobs()
    baseline = is_baseline_run(seen_df)

    all_jobs = []
    errors = []
    seen_keys_this_run: set[str] = set()

    for item in companies:
        company = item["company"]
        try:
            jobs = crawl_company(company, item["career_url"], item["source"])
            kept = 0
            for job in jobs:
                if job.job_key in seen_keys_this_run:
                    continue
                seen_keys_this_run.add(job.job_key)
                all_jobs.append(job)
                kept += 1
            print(f"[ok] {company}: {kept} relevant jobs")
        except Exception as exc:
            errors.append((company, str(exc)))
            print(f"[error] {company}: {exc}")

    entry_level_jobs = filter_entry_level_jobs(all_jobs)
    tracked_jobs = entry_level_jobs if ENTRY_LEVEL_ONLY else all_jobs

    newly_discovered = split_new_jobs(tracked_jobs, seen_df)
    new_entry_level_jobs = filter_entry_level_jobs(newly_discovered)
    updated_seen = update_seen_jobs(tracked_jobs, seen_df)
    save_outputs(
        newly_discovered,
        all_jobs,
        entry_level_jobs,
        new_entry_level_jobs,
        updated_seen,
        baseline=baseline,
    )

    print()
    print(f"Total relevant jobs this run: {len(all_jobs)}")
    print(f"Entry level jobs this run: {len(entry_level_jobs)}")
    if ENTRY_LEVEL_ONLY:
        print("ENTRY_LEVEL_ONLY=True: tracking and new_jobs use entry-level filter only.")
    if baseline:
        print("Baseline run: saved seen_jobs.csv only, no new_jobs output.")
        print(f"Tracked jobs: {len(updated_seen)}")
    else:
        print(f"New jobs this run: {len(newly_discovered)}")
        print(f"New entry level jobs this run: {len(new_entry_level_jobs)}")
        print("Saved to output/new_jobs.csv, output/entry_level_jobs.csv")

    if errors:
        print()
        print(f"Failed companies: {len(errors)}")
        for company, message in errors:
            print(f"  - {company}: {message}")

    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
