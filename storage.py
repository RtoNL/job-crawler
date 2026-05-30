from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from config import NEW_JOB_HOURS
from crawlers.base import Job

DATA_DIR = Path("data")
SEEN_JOBS_PATH = DATA_DIR / "seen_jobs.csv"
OUTPUT_DIR = Path("output")
NEW_JOBS_PATH = OUTPUT_DIR / "new_jobs.csv"
ALL_JOBS_PATH = OUTPUT_DIR / "all_relevant_jobs.csv"
ENTRY_LEVEL_JOBS_PATH = OUTPUT_DIR / "entry_level_jobs.csv"
NEW_ENTRY_LEVEL_JOBS_PATH = OUTPUT_DIR / "new_entry_level_jobs.csv"
RECENT_JOBS_PATH = OUTPUT_DIR / "recent_24h_jobs.csv"

OUTPUT_COLUMNS = [
    "company",
    "title",
    "url",
    "location",
    "source",
    "job_id",
    "job_key",
    "found_at",
    "posted_at",
]

SEEN_JOBS_COLUMNS = [
    "job_key",
    "job_id",
    "url",
    "company",
    "title",
    "location",
    "source",
    "first_seen",
    "posted_at",
]


def ensure_dirs() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def _empty_seen_jobs() -> pd.DataFrame:
    return pd.DataFrame(columns=SEEN_JOBS_COLUMNS)


def is_baseline_run(seen_df: pd.DataFrame) -> bool:
    return seen_df.empty


def load_seen_jobs() -> pd.DataFrame:
    ensure_dirs()
    if not SEEN_JOBS_PATH.exists() or SEEN_JOBS_PATH.stat().st_size == 0:
        return _empty_seen_jobs()

    try:
        df = pd.read_csv(SEEN_JOBS_PATH)
    except pd.errors.EmptyDataError:
        return _empty_seen_jobs()

    # Migrate older files that only tracked url.
    if "job_key" not in df.columns:
        df["job_key"] = df["url"].astype(str)
    if "job_id" not in df.columns:
        df["job_id"] = ""

    return df


def _known_keys(seen_df: pd.DataFrame) -> set[str]:
    if seen_df.empty:
        return set()
    return set(seen_df["job_key"].astype(str))


def jobs_to_dataframe(jobs: list[Job]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "company": job.company,
                "title": job.title,
                "url": job.url,
                "location": job.location,
                "source": job.source,
                "job_id": job.job_id,
                "job_key": job.job_key,
                "found_at": job.found_at,
                "posted_at": job.posted_at,
            }
            for job in jobs
        ]
    )


def split_new_jobs(jobs: list[Job], seen_df: pd.DataFrame) -> list[Job]:
    if is_baseline_run(seen_df):
        return []

    known_keys = _known_keys(seen_df)
    return [job for job in jobs if job.job_key not in known_keys]


def update_seen_jobs(jobs: list[Job], seen_df: pd.DataFrame) -> pd.DataFrame:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = []

    existing = {}
    if not seen_df.empty:
        for row in seen_df.to_dict("records"):
            existing[str(row["job_key"])] = row

    for job in jobs:
        if job.job_key in existing:
            records.append(existing[job.job_key])
            continue

        records.append(
            {
                "job_key": job.job_key,
                "job_id": job.job_id,
                "url": job.url,
                "company": job.company,
                "title": job.title,
                "location": job.location,
                "source": job.source,
                "first_seen": now,
                "posted_at": job.posted_at,
            }
        )

    updated = pd.DataFrame(records, columns=SEEN_JOBS_COLUMNS)
    updated.to_csv(SEEN_JOBS_PATH, index=False)
    return updated


def save_outputs(
    newly_discovered: list[Job],
    all_jobs: list[Job],
    entry_level_jobs: list[Job],
    new_entry_level_jobs: list[Job],
    seen_df: pd.DataFrame,
    *,
    baseline: bool,
) -> None:
    ensure_dirs()

    all_df = jobs_to_dataframe(all_jobs)
    all_df.to_csv(ALL_JOBS_PATH, index=False)

    entry_level_df = jobs_to_dataframe(entry_level_jobs)
    entry_level_df.to_csv(ENTRY_LEVEL_JOBS_PATH, index=False)

    if baseline:
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(NEW_JOBS_PATH, index=False)
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(NEW_ENTRY_LEVEL_JOBS_PATH, index=False)
        pd.DataFrame(columns=SEEN_JOBS_COLUMNS).to_csv(RECENT_JOBS_PATH, index=False)
        return

    new_df = jobs_to_dataframe(newly_discovered)
    new_df.to_csv(NEW_JOBS_PATH, index=False)

    new_entry_level_df = jobs_to_dataframe(new_entry_level_jobs)
    new_entry_level_df.to_csv(NEW_ENTRY_LEVEL_JOBS_PATH, index=False)

    cutoff = datetime.now() - timedelta(hours=NEW_JOB_HOURS)
    recent = seen_df.copy()
    recent["first_seen"] = pd.to_datetime(recent["first_seen"], errors="coerce")
    recent_df = recent[recent["first_seen"] >= cutoff].copy()
    recent_df["first_seen"] = recent_df["first_seen"].dt.strftime("%Y-%m-%d %H:%M:%S")
    recent_df.to_csv(RECENT_JOBS_PATH, index=False)
