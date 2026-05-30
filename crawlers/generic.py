import hashlib
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT
from crawlers.base import Job, now_str
from filters import is_relevant_job


def crawl(company: str, career_url: str) -> list[Job]:
    response = requests.get(
        career_url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    jobs: list[Job] = []
    seen_urls: set[str] = set()

    for link in soup.find_all("a", href=True):
        title = link.get_text(strip=True)
        href = link["href"]

        if not title or len(title) < 5:
            continue
        if not is_relevant_job(title):
            continue

        url = urljoin(career_url, href)
        if url in seen_urls:
            continue
        seen_urls.add(url)

        job_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
        jobs.append(
            Job(
                company=company,
                title=title,
                url=url,
                location="",
                source="generic",
                job_id=job_id,
                found_at=now_str(),
            )
        )

    return jobs
