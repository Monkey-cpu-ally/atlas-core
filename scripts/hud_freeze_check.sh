#!/usr/bin/env bash
set -euo pipefail

# HUD Freeze Check
# Fails if protected HUD paths were modified without an explicit override.
#
# Override options:
# - Set env HUD_FREEZE_OVERRIDE=1
# - Include "[HUD-CHANGE]" in a commit message in the range BASE..HEAD
# - (CI) Set env HUD_FREEZE_PR_TITLE to a title containing "[HUD-CHANGE]"
#
# Usage:
#   bash scripts/hud_freeze_check.sh <base-ref> <head-ref>
# Examples:
#   bash scripts/hud_freeze_check.sh origin/main HEAD
#   bash scripts/hud_freeze_check.sh "$GITHUB_BASE_SHA" "$GITHUB_HEAD_SHA"

BASE_REF="${1:-}"
HEAD_REF="${2:-HEAD}"

if [[ -z "${BASE_REF}" ]]; then
  if git rev-parse --verify "${HEAD_REF}^" >/dev/null 2>&1; then
    BASE_REF="${HEAD_REF}^"
  else
    BASE_REF="${HEAD_REF}"
  fi
fi

git rev-parse --verify "${BASE_REF}" >/dev/null 2>&1 || {
  echo "HUD freeze: base ref '${BASE_REF}' not found."
  exit 2
}
git rev-parse --verify "${HEAD_REF}" >/dev/null 2>&1 || {
  echo "HUD freeze: head ref '${HEAD_REF}' not found."
  exit 2
}

CHANGED_FILES="$(git diff --name-only "${BASE_REF}...${HEAD_REF}" || true)"

# Protected HUD paths.
# (These are design-frozen; changes require an explicit [HUD-CHANGE] marker.)
PROTECTED_REGEX='^(docs/architecture/|flutter_atlas_scaffold/|lib/custom_code/atlas_console/atlas_console_widget\.dart$)'
PROTECTED_CHANGED="$(printf "%s\n" "${CHANGED_FILES}" | grep -E "${PROTECTED_REGEX}" || true)"

if [[ -z "${PROTECTED_CHANGED}" ]]; then
  echo "HUD freeze: OK (no protected HUD files changed)."
  exit 0
fi

if [[ "${HUD_FREEZE_OVERRIDE:-}" == "1" ]]; then
  echo "HUD freeze: OVERRIDE (HUD_FREEZE_OVERRIDE=1). Protected files changed:"
  printf "%s\n" "${PROTECTED_CHANGED}"
  exit 0
fi

if [[ "${HUD_FREEZE_PR_TITLE:-}" == *"[HUD-CHANGE]"* ]]; then
  echo "HUD freeze: OVERRIDE (PR title contains [HUD-CHANGE]). Protected files changed:"
  printf "%s\n" "${PROTECTED_CHANGED}"
  exit 0
fi

if git log --format=%B "${BASE_REF}..${HEAD_REF}" 2>/dev/null | grep -q '\[HUD-CHANGE\]'; then
  echo "HUD freeze: OVERRIDE (commit message contains [HUD-CHANGE]). Protected files changed:"
  printf "%s\n" "${PROTECTED_CHANGED}"
  exit 0
fi

echo "HUD freeze: BLOCKED."
echo
echo "Protected HUD paths were modified:"
printf "%s\n" "${PROTECTED_CHANGED}"
echo
echo "To intentionally change HUD design/code, add [HUD-CHANGE] to:"
echo "- the PR title, or"
echo "- a commit message in this change range."
echo
echo "To override locally (not recommended), run with HUD_FREEZE_OVERRIDE=1."
exit 1

