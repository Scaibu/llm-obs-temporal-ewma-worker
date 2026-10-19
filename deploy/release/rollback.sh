#!/usr/bin/env bash
set -euo pipefail

ENV="${1:-dev}"
REVISION="${2:-0}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "=== Rolling back temporal-ewma-worker in environment: ${ENV} ==="

if command -v kubectl >/dev/null 2>&1; then
  if [ "${REVISION}" != "0" ]; then
    echo "Rolling back to revision ${REVISION}..."
    kubectl rollout undo deployment/temporal-ewma-worker -n "llmobs-${ENV}" --to-revision="${REVISION}"
  else
    echo "Rolling back to previous revision..."
    kubectl rollout undo deployment/temporal-ewma-worker -n "llmobs-${ENV}"
  fi
  kubectl rollout status deployment/temporal-ewma-worker -n "llmobs-${ENV}" --timeout=120s
elif command -v helm >/dev/null 2>&1; then
  echo "Rolling back Helm release..."
  if [ "${REVISION}" != "0" ]; then
    helm rollback temporal-ewma-worker "${REVISION}" --namespace "llmobs-${ENV}"
  else
    helm rollback temporal-ewma-worker 0 --namespace "llmobs-${ENV}"
  fi
else
  echo "Neither kubectl nor helm found. Rollback aborted."
  exit 1
fi

echo "Rollback completed successfully."
