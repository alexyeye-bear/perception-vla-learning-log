#!/bin/sh
set -eu

if command -v python >/dev/null 2>&1; then
  python scripts/update_topic_indexes.py
elif command -v py >/dev/null 2>&1; then
  py -3 scripts/update_topic_indexes.py
else
  echo "Python is required to update topic indexes." >&2
  exit 1
fi

git add topics/README.md topics/perception.md topics/vla.md topics/uncategorized.md
