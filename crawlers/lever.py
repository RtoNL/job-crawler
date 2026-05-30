import re
from datetime import datetime, timezone

from crawlers.base import Job, fetch_json, now_str
from filters import is_relevant_job


def extract_slug(career_url: str) -> str | None:
    match = re.search(r"jobs\.lever\.co/([^/?#]+)", career_url, re.I)
    return match.group(1) if match else None


def _format_timestamp(ms: int | None) -> str | None:
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _extract_description(item: dict) -> str:
    description = item.get("descriptionPlain") or item.get("description") or ""
    if description:
        return description

    parts = [item.get("opening", ""), item.get("descriptionBody", "")]
    for block in item.get("lists", []) or []:
        parts.append(block.get("text", ""))
        for entry in block.get("content", "") or []:
            if isinstance(entry, str):
                parts.append(entry)

    return "\n".join(part for part in parts if part)


def crawl(company: str, career_url: str) -> list[Job]:
    slug = extract_slug(career_url)
    if not slug:
        return []

    data = fetch_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    jobs: list[Job] = []

    for item in data:
        title = item.get("text", "")
        location = (item.get("categories") or {}).get("location", "")
        url = item.get("hostedUrl", "")

        if not title or not url:
            continue
        if not is_relevant_job(title, location):
            continue

        job_id = str(item.get("id", ""))
        if not job_id:
            continue

        jobs.append(
            Job(
                company=company,
                title=title,
                url=url,
                location=location,
                source="lever",
                job_id=job_id,
                found_at=now_str(),
                posted_at=_format_timestamp(item.get("createdAt")),
                description=_extract_description(item),
            )
        )

    return jobs
