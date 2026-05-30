import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

from config import REQUEST_TIMEOUT, USER_AGENT


@dataclass
class Job:
    company: str
    title: str
    url: str
    location: str
    source: str
    job_id: str
    found_at: str
    posted_at: Optional[str] = None
    description: Optional[str] = None

    @property
    def job_key(self) -> str:
        return make_job_key(self.source, self.company, self.job_id)


def make_job_key(source: str, company: str, job_id: str) -> str:
    company_slug = re.sub(r"[^a-z0-9]+", "_", company.lower()).strip("_")
    return f"{source}_{company_slug}_{job_id}"


def fetch_json(url: str) -> dict | list:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.json()


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
