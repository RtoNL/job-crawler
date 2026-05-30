import re

from crawlers import ashby, generic, greenhouse, lever
from crawlers.base import Job


def detect_source(career_url: str) -> str:
    url = career_url.lower()
    if "greenhouse.io" in url:
        return "greenhouse"
    if "jobs.lever.co" in url:
        return "lever"
    if "jobs.ashbyhq.com" in url:
        return "ashby"
    return "generic"


def crawl_company(company: str, career_url: str, source: str | None = None) -> list[Job]:
    source = (source or detect_source(career_url)).lower().strip()

    if source == "greenhouse":
        return greenhouse.crawl(company, career_url)
    if source == "lever":
        return lever.crawl(company, career_url)
    if source == "ashby":
        return ashby.crawl(company, career_url)
    if source == "generic":
        return generic.crawl(company, career_url)

    raise ValueError(f"Unsupported source: {source}")
