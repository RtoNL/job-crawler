import re

from bs4 import BeautifulSoup

from crawlers.base import Job, fetch_json, now_str
from filters import is_relevant_job


def extract_slug(career_url: str) -> str | None:
    match = re.search(r"greenhouse\.io/([^/?#]+)", career_url, re.I)
    return match.group(1) if match else None


def _html_to_text(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)


def crawl(company: str, career_url: str) -> list[Job]:
    slug = extract_slug(career_url)
    if not slug:
        return []

    data = fetch_json(
        f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    )
    jobs: list[Job] = []

    for item in data.get("jobs", []):
        title = item.get("title", "")
        location = (item.get("location") or {}).get("name", "")
        url = item.get("absolute_url", "")

        if not title or not url:
            continue
        if not is_relevant_job(title, location):
            continue

        job_id = str(item.get("id", ""))
        if not job_id:
            continue

        description = _html_to_text(item.get("content", ""))
        posted_at = item.get("first_published") or item.get("updated_at")
        jobs.append(
            Job(
                company=company,
                title=title,
                url=url,
                location=location,
                source="greenhouse",
                job_id=job_id,
                found_at=now_str(),
                posted_at=posted_at,
                description=description,
            )
        )

    return jobs
