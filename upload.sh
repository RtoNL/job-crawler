#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

# Remove partial git setup if any
rm -rf .git

git init
git branch -M main
git add .
git commit -m "$(cat <<'EOF'
Add ATS job crawler with entry-level filter.

EOF
)"

# Create repo on GitHub (requires gh CLI: brew install gh && gh auth login)
if command -v gh >/dev/null 2>&1; then
  gh repo create RtoNL/job-crawler --private --source=. --remote=origin --push
  echo "Done: https://github.com/RtoNL/job-crawler"
else
  echo "gh not found. Create repo manually at https://github.com/new"
  echo "Name: job-crawler"
  echo "Then run:"
  echo "  git remote add origin https://github.com/RtoNL/job-crawler.git"
  echo "  git push -u origin main"
fi
