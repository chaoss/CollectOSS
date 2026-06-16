#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# generate.sh — CollectOSS Sample Data Generator
#
# Brings up the CollectOSS Docker stack, loads a set of repositories,
# waits for collection to complete, and packages the collected `data`
# schema into a standalone Docker image that can be used as a portable
# sample dataset for downstreams and data science workloads.
#
# Usage:
#   ./generate.sh --repos repos.txt [OPTIONS]
#
# See --help for full usage.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ── Terminal colors ────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log()  { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $*"; }
ok()   { echo -e "${GREEN}[$(date '+%H:%M:%S')] ✓${NC} $*"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠${NC} $*"; }
die()  { echo -e "${RED}[$(date '+%H:%M:%S')] ✗ ERROR:${NC} $*" >&2; exit 1; }
section() { echo ""; echo -e "${BOLD}── $* ──────────────────────────────────────────────────${NC}"; }

# ── Defaults ───────────────────────────────────────────────────────────────────
REPOS_FILE=""
IMAGE_NAME="collectoss-sample-data"
IMAGE_TAG="$(date +%Y%m%d)"
TIMEOUT_MINUTES=120
POLL_INTERVAL=30
COMPOSE_PROJECT="collectoss-sampledata-$$"
SKIP_BUILD=0
KEEP_STACK=0
WAIT_FOR_FACADE=0
PUSH_IMAGE=0
REPO_GROUP_ID=5
REPO_GROUP_NAME="Sample Data"
OUTPUT_DIR="${SCRIPT_DIR}/output"
ENV_FILE="${REPO_ROOT}/.env"

# ── Usage ──────────────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
${BOLD}CollectOSS Sample Data Generator${NC}

Loads repositories into CollectOSS, waits for collection to finish,
and packages the collected 'data' schema as a portable Docker image.

${BOLD}Usage:${NC}
  $0 --repos FILE [OPTIONS]

${BOLD}Required:${NC}
  --repos FILE      Path to a repos input file. Two formats are accepted:

                    Plain list (one URL per line, '#' comments OK):
                      https://github.com/chaoss/augur
                      https://github.com/chaoss/grimoirelab
                      # this is ignored

                    CSV with 'repo_url' column (repo_group_id optional):
                      repo_url,repo_group_id
                      https://github.com/chaoss/augur,1

${BOLD}Options:${NC}
  --image NAME      Output Docker image name
                    (default: collectoss-sample-data)
  --tag TAG         Output Docker image tag
                    (default: YYYYMMDD)
  --timeout MINS    Max minutes to wait for collection before proceeding
                    with whatever has been collected (default: 120)
  --env FILE        Path to .env file (default: <repo root>/.env)
  --wait-facade     Also wait for facade (git clone) collection to finish.
                    Facade data includes git commit history and is slower
                    to collect — skip it unless you need commit-level data.
  --skip-build      Skip rebuilding Docker images (use already-built ones)
  --keep-stack      Don't tear down the compose stack after completion.
                    Useful for inspecting results or rerunning.
  --push            Push the built image with 'docker push' after building
  --output-dir DIR  Directory to write the SQL dump file
                    (default: scripts/sample-data/output/)
  -h, --help        Show this help

${BOLD}Examples:${NC}
  # Basic local run
  $0 --repos repos.txt

  # Custom image name + push to registry
  $0 --repos repos.txt \\
     --image ghcr.io/chaoss/collectoss-sample \\
     --tag v1.2.0 \\
     --push

  # Include facade data, raise timeout for large repos
  $0 --repos repos.txt --wait-facade --timeout 240

  # Keep stack running so you can inspect the DB afterward
  $0 --repos repos.txt --keep-stack

${BOLD}CI Usage (GitHub Actions):${NC}
  Recommended: set COLLECTOSS_GITHUB_API_KEY and other secrets as env vars,
  point --env at a generated .env file, and set --push with GHCR credentials
  already established via 'docker login'.
EOF
}

# ── Argument parsing ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repos)      REPOS_FILE="$2";       shift 2 ;;
    --image)      IMAGE_NAME="$2";       shift 2 ;;
    --tag)        IMAGE_TAG="$2";        shift 2 ;;
    --timeout)    TIMEOUT_MINUTES="$2";  shift 2 ;;
    --env)        ENV_FILE="$2";         shift 2 ;;
    --output-dir) OUTPUT_DIR="$2";       shift 2 ;;
    --wait-facade)  WAIT_FOR_FACADE=1;   shift ;;
    --skip-build)   SKIP_BUILD=1;        shift ;;
    --keep-stack)   KEEP_STACK=1;        shift ;;
    --push)         PUSH_IMAGE=1;        shift ;;
    -h|--help)    usage; exit 0 ;;
    *) die "Unknown option: $1\nRun '$0 --help' for usage." ;;
  esac
done

# ── Validate inputs ────────────────────────────────────────────────────────────
[[ -z "$REPOS_FILE" ]] && { usage; echo ""; die "--repos is required."; }
[[ -f "$REPOS_FILE" ]] || die "Repos file not found: $REPOS_FILE"
[[ -f "$ENV_FILE"   ]] || die ".env file not found: $ENV_FILE\nCreate one from environment.txt or use --env to specify its location."

command -v docker >/dev/null 2>&1 || die "'docker' is not installed or not in PATH."
docker compose version >/dev/null 2>&1 || die "'docker compose' (v2) is required. Please upgrade Docker."

# Source .env so local scripts can use the same credentials
set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

DB_USER="${COLLECTOSS_DB_USER:-augur}"
DB_NAME="${COLLECTOSS_DB_NAME:-augur}"
DB_PASSWORD="${COLLECTOSS_DB_PASSWORD:-augur}"

mkdir -p "$OUTPUT_DIR"

# Temp dir cleaned up on exit
WORK_DIR="$(mktemp -d)"

# ── Cleanup trap ───────────────────────────────────────────────────────────────
cleanup() {
  local exit_code=$?
  if [[ $KEEP_STACK -eq 0 ]]; then
    log "Tearing down stack '${COMPOSE_PROJECT}'..."
    compose_cmd down -v --remove-orphans 2>/dev/null || true
  else
    warn "Stack '${COMPOSE_PROJECT}' left running (--keep-stack)."
    warn "To tear it down later:  docker compose -p ${COMPOSE_PROJECT} down -v"
  fi
  rm -rf "$WORK_DIR"
  exit "$exit_code"
}
trap cleanup EXIT

# ── Helpers ────────────────────────────────────────────────────────────────────

# Wrapper so we don't have to repeat flags everywhere
compose_cmd() {
  docker compose \
    --project-name "$COMPOSE_PROJECT" \
    -f "${REPO_ROOT}/docker-compose.yml" \
    --env-file "$ENV_FILE" \
    "$@"
}

# Run a psql command inside the database container; returns raw trimmed output
db_query() {
  compose_cmd exec -T database \
    psql -U "$DB_USER" -d "$DB_NAME" \
    -t -A -F '|' \
    -c "$1" 2>/dev/null | head -1 | tr -d ' '
}

# Run a command inside the core container
core_exec() {
  compose_cmd exec -T core "$@"
}

# Parse the repos input file into a CSV suitable for `collectoss db add-repos`
prepare_repos_csv() {
  local src="$1"
  local dst="$2"

  # If the first non-comment, non-blank line contains a comma and 'repo_url',
  # treat the file as an already-formatted CSV.
  local first_data_line
  first_data_line="$(grep -v '^[[:space:]]*#' "$src" | grep -v '^[[:space:]]*$' | head -1 || true)"
  if echo "$first_data_line" | grep -qi "repo_url"; then
    cp "$src" "$dst"
    return
  fi

  # Plain URL list — generate CSV with repo_group_id column
  {
    echo "repo_url,repo_group_id"
    while IFS= read -r line; do
      # Strip comments and whitespace
      line="${line%%#*}"
      line="${line#"${line%%[![:space:]]*}"}"
      line="${line%"${line##*[![:space:]]}"}"
      [[ -z "$line" ]] && continue
      echo "${line},${REPO_GROUP_ID}"
    done < "$src"
  } > "$dst"
}

count_repos_in_csv() {
  local file="$1"
  # Count non-header, non-blank lines
  local total
  total="$(wc -l < "$file")"
  echo $(( total - 1 ))  # subtract header row
}

# ── Print banner ───────────────────────────────────────────────────────────────
REPOS_CSV="${WORK_DIR}/repos.csv"
GROUPS_CSV="${WORK_DIR}/groups.csv"
prepare_repos_csv "$REPOS_FILE" "$REPOS_CSV"
REPO_COUNT="$(count_repos_in_csv "$REPOS_CSV")"

echo ""
echo -e "${BOLD}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   CollectOSS Sample Data Generator           ║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Repos to collect : ${BOLD}${REPO_COUNT}${NC}"
echo -e "  Output image     : ${BOLD}${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo -e "  Compose project  : ${BOLD}${COMPOSE_PROJECT}${NC}"
echo -e "  Collection timeout: ${BOLD}${TIMEOUT_MINUTES}m${NC}"
[[ $WAIT_FOR_FACADE -eq 1 ]] && echo -e "  Facade collection: ${BOLD}enabled${NC}" || echo -e "  Facade collection: ${YELLOW}skipped${NC} (use --wait-facade to enable)"
echo ""

# ════════════════════════════════════════════════════════════════════════════════
section "STEP 1  Start the stack"
# ════════════════════════════════════════════════════════════════════════════════

BUILD_FLAGS=()
[[ $SKIP_BUILD -eq 0 ]] && BUILD_FLAGS+=("--build")

log "Starting CollectOSS stack (project: ${COMPOSE_PROJECT})..."
compose_cmd up -d "${BUILD_FLAGS[@]+"${BUILD_FLAGS[@]}"}"
ok "Stack started."

# Wait for the database to pass its healthcheck
log "Waiting for database to be healthy (up to 3 minutes)..."
DEADLINE=$(( $(date +%s) + 180 ))
while true; do
  DB_HEALTH="$(docker inspect \
    --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' \
    "$(compose_cmd ps -q database 2>/dev/null)" 2>/dev/null || echo "starting")"
  if [[ "$DB_HEALTH" == "healthy" ]]; then
    ok "Database is healthy."
    break
  fi
  if [[ $(date +%s) -ge $DEADLINE ]]; then
    die "Timed out waiting for database to become healthy."
  fi
  sleep 5
done

# Wait for the CollectOSS API to respond
log "Waiting for CollectOSS API to respond (up to 5 minutes)..."
DEADLINE=$(( $(date +%s) + 300 ))
while true; do
  if curl -sf --max-time 5 "http://localhost:5002/api/unstable/repo-groups" > /dev/null 2>&1; then
    ok "CollectOSS API is ready."
    break
  fi
  if [[ $(date +%s) -ge $DEADLINE ]]; then
    die "Timed out waiting for CollectOSS API on http://localhost:5002"
  fi
  sleep 5
done

# ════════════════════════════════════════════════════════════════════════════════
section "STEP 2  Load repositories"
# ════════════════════════════════════════════════════════════════════════════════

# Build the repo group CSV
{
  echo "repo_group_id,repo_group_name"
  echo "${REPO_GROUP_ID},${REPO_GROUP_NAME}"
} > "$GROUPS_CSV"

log "Copying CSVs into core container..."
compose_cmd cp "$GROUPS_CSV" core:/tmp/groups.csv
compose_cmd cp "$REPOS_CSV"  core:/tmp/repos.csv

log "Creating repo group '${REPO_GROUP_NAME}' (ID: ${REPO_GROUP_ID})..."
# The group may already exist if the DB was pre-seeded; that's fine.
core_exec collectoss db add-repo-groups /tmp/groups.csv 2>&1 | \
  grep -v "already exist" || true
ok "Repo group ready."

log "Loading ${REPO_COUNT} repos into CollectOSS..."
core_exec collectoss db add-repos /tmp/repos.csv
ok "Repos loaded. Workers will begin collecting automatically."

# ════════════════════════════════════════════════════════════════════════════════
section "STEP 3  Wait for collection to complete"
# ════════════════════════════════════════════════════════════════════════════════

log "Polling collection_status (timeout: ${TIMEOUT_MINUTES}m, interval: ${POLL_INTERVAL}s)..."

# All active (non-terminal) statuses per collection phase:
#   core/secondary: Pending | Collecting
#   facade:         Pending | Initializing | Update | Collecting
TIMEOUT_SECS=$(( TIMEOUT_MINUTES * 60 ))
START_TIME=$(date +%s)
DEADLINE=$(( START_TIME + TIMEOUT_SECS ))

while true; do
  NOW=$(date +%s)
  if [[ $NOW -ge $DEADLINE ]]; then
    warn "Collection timed out after ${TIMEOUT_MINUTES} minutes."
    warn "Proceeding with whatever data was collected."
    break
  fi

  # Query each count separately to keep parsing simple
  TOTAL=$(db_query        "SELECT COUNT(*) FROM operations.collection_status")
  CORE_DONE=$(db_query    "SELECT COUNT(*) FROM operations.collection_status WHERE core_status = 'Success'")
  CORE_ERR=$(db_query     "SELECT COUNT(*) FROM operations.collection_status WHERE core_status = 'Error'")
  CORE_PEND=$(db_query    "SELECT COUNT(*) FROM operations.collection_status WHERE core_status IN ('Pending','Collecting')")
  SEC_DONE=$(db_query     "SELECT COUNT(*) FROM operations.collection_status WHERE secondary_status = 'Success'")
  SEC_ERR=$(db_query      "SELECT COUNT(*) FROM operations.collection_status WHERE secondary_status = 'Error'")
  SEC_PEND=$(db_query     "SELECT COUNT(*) FROM operations.collection_status WHERE secondary_status IN ('Pending','Collecting')")
  FACADE_DONE=$(db_query  "SELECT COUNT(*) FROM operations.collection_status WHERE facade_status = 'Success'")
  FACADE_ERR=$(db_query   "SELECT COUNT(*) FROM operations.collection_status WHERE facade_status IN ('Error','Failed Clone')")
  FACADE_PEND=$(db_query  "SELECT COUNT(*) FROM operations.collection_status WHERE facade_status IN ('Pending','Initializing','Update','Collecting')")

  # Replace empty/failed queries with 0
  TOTAL=${TOTAL:-0};         CORE_DONE=${CORE_DONE:-0};   CORE_ERR=${CORE_ERR:-0};   CORE_PEND=${CORE_PEND:-0}
  SEC_DONE=${SEC_DONE:-0};   SEC_ERR=${SEC_ERR:-0};       SEC_PEND=${SEC_PEND:-0}
  FACADE_DONE=${FACADE_DONE:-0}; FACADE_ERR=${FACADE_ERR:-0}; FACADE_PEND=${FACADE_PEND:-0}

  ELAPSED=$(( NOW - START_TIME ))
  ELAPSED_FMT="$(( ELAPSED / 60 ))m$(( ELAPSED % 60 ))s"

  log "[${ELAPSED_FMT}] status_rows=${TOTAL}/${REPO_COUNT} | core: ✓${CORE_DONE} ✗${CORE_ERR} ⏳${CORE_PEND} | secondary: ✓${SEC_DONE} ✗${SEC_ERR} ⏳${SEC_PEND} | facade: ✓${FACADE_DONE} ✗${FACADE_ERR} ⏳${FACADE_PEND}"

  if [[ "$TOTAL" -eq 0 ]]; then
    log "No collection_status records yet — workers are starting up..."
    sleep "$POLL_INTERVAL"
    continue
  fi

  # Determine if we're done
  ALL_DONE=1
  [[ "$CORE_PEND" -gt 0 ]] && ALL_DONE=0
  [[ "$SEC_PEND"  -gt 0 ]] && ALL_DONE=0
  if [[ $WAIT_FOR_FACADE -eq 1 ]]; then
    [[ "$FACADE_PEND" -gt 0 ]] && ALL_DONE=0
  fi

  if [[ $ALL_DONE -eq 1 ]]; then
    ok "Collection complete!"
    ok "  Core      : ${CORE_DONE} success / ${CORE_ERR} error"
    ok "  Secondary : ${SEC_DONE} success / ${SEC_ERR} error"
    ok "  Facade    : ${FACADE_DONE} success / ${FACADE_ERR} error"
    break
  fi

  sleep "$POLL_INTERVAL"
done

# ════════════════════════════════════════════════════════════════════════════════
section "STEP 4  Dump the 'data' schema"
# ════════════════════════════════════════════════════════════════════════════════

DUMP_FILE="${OUTPUT_DIR}/data_dump_${IMAGE_TAG}.sql"
log "Dumping 'data' schema → ${DUMP_FILE} ..."

# Also capture collection_status as metadata (contains no PII/auth data)
METADATA_FILE="${OUTPUT_DIR}/collection_status_${IMAGE_TAG}.sql"
log "Dumping collection_status metadata → ${METADATA_FILE} ..."

compose_cmd exec -T database pg_dump \
  -U "$DB_USER" \
  "$DB_NAME" \
  --schema=data \
  --no-owner \
  --no-acl \
  > "$DUMP_FILE"

# Dump collection_status table from operations schema (metadata only, no auth)
compose_cmd exec -T database pg_dump \
  -U "$DB_USER" \
  "$DB_NAME" \
  --table="operations.collection_status" \
  --no-owner \
  --no-acl \
  > "$METADATA_FILE"

DUMP_SIZE="$(du -sh "$DUMP_FILE" | cut -f1)"
META_SIZE="$(du -sh "$METADATA_FILE" | cut -f1)"
ok "Data schema dump: ${DUMP_FILE} (${DUMP_SIZE})"
ok "Metadata dump:    ${METADATA_FILE} (${META_SIZE})"

# ════════════════════════════════════════════════════════════════════════════════
section "STEP 5  Build the sample data Docker image"
# ════════════════════════════════════════════════════════════════════════════════

DOCKER_BUILD_DIR="${WORK_DIR}/docker-build"
mkdir -p "$DOCKER_BUILD_DIR"

cp "$DUMP_FILE"     "${DOCKER_BUILD_DIR}/01_data_schema.sql"
# cp "$METADATA_FILE" "${DOCKER_BUILD_DIR}/02_collection_status.sql"

# Write the Dockerfile for the sample-data image.
# The postgres:16 entrypoint automatically runs all *.sql files in
# /docker-entrypoint-initdb.d/ on first startup.
cat > "${DOCKER_BUILD_DIR}/Dockerfile" <<'DOCKERFILE'
FROM postgres:16

LABEL org.opencontainers.image.title="CollectOSS Sample Data"
LABEL org.opencontainers.image.description="Pre-collected open-source metrics from the CollectOSS 'data' schema. Ready to use for downstream analytics and data science without running a live instance."
LABEL org.opencontainers.image.source="https://github.com/chaoss/collectoss"
LABEL org.opencontainers.image.licenses="MIT"

# Default credentials for the sample database.
# Override with -e flags when running the container if needed.
ENV POSTGRES_DB=collectoss_sample
ENV POSTGRES_USER=collectoss
ENV POSTGRES_PASSWORD=collectoss

# Copy schema dumps — postgres entrypoint loads these alphabetically on init.
# 01_ creates all tables; 02_ loads collection_status metadata.
COPY 01_data_schema.sql        /docker-entrypoint-initdb.d/01_data_schema.sql
# COPY 02_collection_status.sql  /docker-entrypoint-initdb.d/02_collection_status.sql

EXPOSE 5432
DOCKERFILE

GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

log "Building ${IMAGE_NAME}:${IMAGE_TAG} ..."
docker build \
  --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
  --tag "${IMAGE_NAME}:latest" \
  --label "collectoss.sample-data.repos=${REPO_COUNT}" \
  --label "collectoss.sample-data.generated=${GENERATED_AT}" \
  --label "collectoss.sample-data.waited-for-facade=${WAIT_FOR_FACADE}" \
  "$DOCKER_BUILD_DIR"

ok "Image built: ${IMAGE_NAME}:${IMAGE_TAG}"
ok "Image built: ${IMAGE_NAME}:latest"

# ════════════════════════════════════════════════════════════════════════════════
section "STEP 6  Push (optional)"
# ════════════════════════════════════════════════════════════════════════════════

if [[ $PUSH_IMAGE -eq 1 ]]; then
  log "Pushing ${IMAGE_NAME}:${IMAGE_TAG} ..."
  docker push "${IMAGE_NAME}:${IMAGE_TAG}"
  docker push "${IMAGE_NAME}:latest"
  ok "Pushed ${IMAGE_NAME}:${IMAGE_TAG}"
  ok "Pushed ${IMAGE_NAME}:latest"
else
  log "Skipping push (use --push to enable)."
fi

# ════════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║   Done!                                       ║${NC}"
echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Image      : ${BOLD}${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo -e "  Dump file  : ${BOLD}${DUMP_FILE}${NC}"
echo ""
echo -e "${BOLD}  Run the sample container:${NC}"
echo -e "    docker run -d -p 5432:5432 --name collectoss-sample ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo -e "${BOLD}  Connect:${NC}"
echo -e "    psql -h localhost -p 5432 -U collectoss -d collectoss_sample"
echo ""
echo -e "${BOLD}  Available schemas:${NC}"
echo -e "    \\dn                          -- list schemas (you'll see 'data')"
echo -e "    \\dt data.*                   -- list all tables in 'data'"
echo -e "    SELECT * FROM data.repo;     -- explore repos"
echo ""
