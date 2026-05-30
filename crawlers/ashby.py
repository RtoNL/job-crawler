import re

from crawlers.base import Job, fetch_json, now_str
from filters import is_relevant_job


def extract_slug(career_url: str) -> str | None:
    match = re.search(r"jobs\.ashbyhq\.com/([^/?#]+)", career_url, re.I)
    return match.group(1) if match else None


def crawl(company: str, career_url: str) -> list[Job]:
    slug = extract_slug(career_url)
    if not slug:
        return []

    data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    jobs: list[Job] = []

    for item in data.get("jobs", []):
        title = item.get("title", "")
        location = item.get("location", "")
        url = item.get("jobUrl") or item.get("applyUrl", "")

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
                source="ashby",
                job_id=job_id,
                found_at=now_str(),
                posted_at=item.get("publishedAt"),
                description=item.get("descriptionPlain") or item.get("description") or "",
            )
        )

    return jobs
