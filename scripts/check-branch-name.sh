#!/usr/bin/env bash
#
# Validate the current Git branch name against the Open-Jarvis convention.
# Used by pre-commit and developers locally.
#
# Convention: docs/it/contributing/branching-strategy.md

set -euo pipefail

BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# Branches protetti che non seguono il pattern feature
PROTECTED_REGEX='^(main|develop|staging|test)$'

# Pattern per branch di lavoro: <type>/<scope>-<purpose>[-#issueNumber]
FEATURE_REGEX='^(feat|fix|hotfix|docs|refactor|perf|test|chore|ci|style|build|release)\/[a-z0-9]+(-[a-z0-9]+)*(-#[0-9]+)?$'

if [[ "$BRANCH" =~ $PROTECTED_REGEX ]] || [[ "$BRANCH" =~ $FEATURE_REGEX ]]; then
  exit 0
fi

cat >&2 <<EOF
❌ Nome branch non valido: '$BRANCH'

Convention Open-Jarvis (vedi docs/it/contributing/branching-strategy.md):

  Branch protetti:  main, develop, staging, test
  Branch di lavoro: <type>/<scope>-<purpose>

Tipi consentiti:
  feat       — nuova feature
  fix        — bug fix
  hotfix     — fix urgente production
  docs       — solo documentazione
  refactor   — refactor senza cambio comportamento
  perf       — miglioramento performance
  test       — aggiunta/modifica test
  chore      — manutenzione (es. update dipendenze)
  ci         — solo CI/CD changes
  style      — format, lint, no code changes
  build      — sistema di build, Dockerfile
  release    — preparazione release branch

Esempi validi:
  feat/health-oura-integration
  fix/voice-agent-empty-buffer
  docs/it-architecture-rag
  hotfix/security-cve-2026-1234
  feat/health-oura-#42  (con riferimento issue)

Per rinominare il branch corrente:
  git branch -m feat/scope-purpose

EOF

exit 1
