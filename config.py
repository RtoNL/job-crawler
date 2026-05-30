KEYWORDS = [
    "software engineer",
    "software developer",
    "frontend",
    "front-end",
    "backend",
    "back-end",
    "full stack",
    "full-stack",
    "fullstack",
    "new grad",
    "university graduate",
    "early career",
    "entry level",
    "ai engineer",
    "machine learning",
    "ml engineer",
    "developer tools",
    "infrastructure",
    "platform engineer",
]

EXCLUDE_KEYWORDS = [
    "staff",
    "principal",
    "senior manager",
    "director",
    "sales",
    "recruiter",
    "account executive",
]

INTERNSHIP_TITLE_PATTERNS = [
    r"\bintern\b",
    r"\binternship\b",
    r"\bco-?op\b",
]

REGIONS = [
    "united states",
    "us",
    "u.s.",
    "usa",
    "north america",
    "remote",
    "seattle",
    "bellevue",
    "san francisco",
    "new york",
    "california",
    "washington",
    "canada",
    "bay area",
    "toronto",
    "vancouver",
]

ENTRY_LEVEL_TITLE_KEYWORDS = [
    "new grad",
    "new graduate",
    "university graduate",
    "university grad",
    "graduate software engineer",
    "early career",
    "entry level",
    "entry-level",
    "junior",
    "associate software engineer",
    "software engineer i",
    "software engineer 1",
    "frontend engineer i",
    "backend engineer i",
    "full stack engineer i",
]

ENTRY_LEVEL_DESCRIPTION_KEYWORDS = [
    "0-1 years",
    "0-1 year",
    "0 to 1 years",
    "0 to 1 year",
    "0+ years",
    "no experience required",
    "new graduate",
    "recent graduate",
    "recent grads",
    "early career",
    "university graduate",
]

SENIORITY_EXCLUDE_KEYWORDS = [
    "senior",
    "staff",
    "principal",
    "lead",
    "manager",
    "director",
    "architect",
    "head of",
]

# When True, only keep entry-level jobs in the main crawl output.
# When False, keep all SDE-relevant jobs and also write entry_level_jobs.csv.
ENTRY_LEVEL_ONLY = False

# Jobs first seen within this window are reported as "new".
NEW_JOB_HOURS = 24

REQUEST_TIMEOUT = 15
USER_AGENT = "JobCrawler/1.0 (+https://github.com/your-repo)"
