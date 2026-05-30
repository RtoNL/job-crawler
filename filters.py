import re

from config import (
    ENTRY_LEVEL_DESCRIPTION_KEYWORDS,
    ENTRY_LEVEL_TITLE_KEYWORDS,
    EXCLUDE_KEYWORDS,
    INTERNSHIP_TITLE_PATTERNS,
    KEYWORDS,
    REGIONS,
    SENIORITY_EXCLUDE_KEYWORDS,
)


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return str(value).lower()


def matches_keywords(text: str) -> bool:
    return any(keyword in normalize_text(text) for keyword in KEYWORDS)


def matches_exclude(text: str) -> bool:
    return any(keyword in normalize_text(text) for keyword in EXCLUDE_KEYWORDS)


def matches_region(location: str) -> bool:
    if not location:
        return True
    location_lower = normalize_text(location)
    return any(region in location_lower for region in REGIONS)


def is_internship_title(title: str) -> bool:
    title_lower = normalize_text(title)
    return any(re.search(pattern, title_lower) for pattern in INTERNSHIP_TITLE_PATTERNS)


def is_relevant_job(title: str, location: str = "") -> bool:
    if is_internship_title(title):
        return False
    if matches_exclude(title):
        return False
    return matches_keywords(title) and matches_region(location)


def has_senior_title(title: str) -> bool:
    title_lower = normalize_text(title)
    return any(keyword in title_lower for keyword in SENIORITY_EXCLUDE_KEYWORDS)


def has_entry_level_title(title: str) -> bool:
    title_lower = normalize_text(title)
    return any(keyword in title_lower for keyword in ENTRY_LEVEL_TITLE_KEYWORDS)


def has_entry_level_description(description: str) -> bool:
    description_lower = normalize_text(description)
    return any(keyword in description_lower for keyword in ENTRY_LEVEL_DESCRIPTION_KEYWORDS)


def requires_more_than_one_year(description: str) -> bool:
    description_lower = normalize_text(description)
    patterns = [
        r"([2-9])\+?\s*years?",
        r"([2-9])\s*-\s*([3-9])\s*years?",
        r"minimum\s+([2-9])\s*years?",
        r"at least\s+([2-9])\s*years?",
    ]

    for pattern in patterns:
        if re.search(pattern, description_lower):
            return True

    return False


def is_entry_level_job(title: str, description: str = "") -> bool:
    if is_internship_title(title):
        return False

    if has_senior_title(title):
        return False

    if requires_more_than_one_year(description):
        return False

    if has_entry_level_title(title):
        return True

    if has_entry_level_description(description):
        return True

    return False
