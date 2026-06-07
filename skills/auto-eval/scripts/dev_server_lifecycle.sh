#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  dev_server_lifecycle.sh start --repo-root <path> --game-name <name> [--game-url <url>] [--bootstrap-playwright] [--timeout-seconds <n>]
  dev_server_lifecycle.sh stop [--state-file <path>] [--server-pid <pid>]

Notes:
- start prints shell assignments that can be eval'ed by caller.
- stop is idempotent and safe when no live process exists.
USAGE
}

print_assignment() {
  local key="$1"
  local value="$2"
  printf '%s=%q\n' "$key" "$value"
}

curl_local() {
  curl --noproxy '*' -sf "$@"
}

find_free_port() {
  local port
  for port in $(seq 4173 4272); do
    if command -v ss >/dev/null 2>&1; then
      if ss -ltn "( sport = :$port )" 2>/dev/null | tail -n +2 | grep -q .; then
        continue
      fi
      echo "$port"
      return 0
    fi
    if command -v lsof >/dev/null 2>&1; then
      if lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
        continue
      fi
      echo "$port"
      return 0
    fi
    if ! curl_local "http://127.0.0.1:$port" >/dev/null 2>&1; then
      echo "$port"
      return 0
    fi
  done
  echo "No free port found in 4173-4272" >&2
  return 1
}

wait_until_ready() {
  local url="$1"
  local timeout_seconds="$2"
  local deadline=$((SECONDS + timeout_seconds))

  while true; do
    if curl_local "$url" >/dev/null; then
      return 0
    fi
    if [[ $SECONDS -ge $deadline ]]; then
      return 1
    fi
    sleep 1
  done
}

start_server() {
  local repo_root=""
  local game_name=""
  local game_url=""
  local bootstrap_playwright=0
  local timeout_seconds=30

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --repo-root)
        repo_root="$2"
        shift 2
        ;;
      --game-name)
        game_name="$2"
        shift 2
        ;;
      --game-url)
        game_url="$2"
        shift 2
        ;;
      --bootstrap-playwright)
        bootstrap_playwright=1
        shift
        ;;
      --timeout-seconds)
        timeout_seconds="$2"
        shift 2
        ;;
      *)
        echo "Unknown start arg: $1" >&2
        usage >&2
        return 2
        ;;
    esac
  done

  if [[ -z "$repo_root" || -z "$game_name" ]]; then
    echo "start requires --repo-root and --game-name" >&2
    return 2
  fi

  if [[ -n "$game_url" ]]; then
    print_assignment STARTED_SERVER "0"
    print_assignment SERVER_PID ""
    print_assignment SERVER_STATE_FILE ""
    print_assignment GAME_URL "$game_url"
    return 0
  fi

  local game_dir="$repo_root/games/$game_name"
  if [[ ! -d "$game_dir" ]]; then
    echo "Game directory not found: $game_dir" >&2
    return 2
  fi

  mkdir -p "$repo_root/runs/.server_state"

  local timestamp
  timestamp="$(date +%Y%m%d_%H%M%S)"
  local port
  port="$(find_free_port)"

  (
    cd "$game_dir"
    npm install >&2
  )

  if [[ $bootstrap_playwright -eq 1 && -f "$repo_root/tools/playwright/package.json" ]]; then
    (
      cd "$repo_root/tools/playwright"
      npm install >&2
      npm run install:chromium >&2
    )
  fi

  local log_file="$repo_root/runs/.server_state/${game_name}_${timestamp}_${port}.log"
  # Detach the background shell from stdout/stderr so callers using command substitution
  # (e.g. eval "$(... start ...)") do not block waiting for pipe EOF.
  (
    cd "$game_dir"
    exec npm run dev -- --host 127.0.0.1 --port "$port" --strictPort >"$log_file" 2>&1
  ) </dev/null >/dev/null 2>&1 &

  local pid=$!
  local resolved_url="http://127.0.0.1:$port"

  if ! wait_until_ready "$resolved_url" "$timeout_seconds"; then
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" || true
    fi
    echo "Dev server did not become ready within ${timeout_seconds}s: $resolved_url" >&2
    echo "Server log: $log_file" >&2
    tail -n 40 "$log_file" >&2 || true
    return 1
  fi

  local state_file="$repo_root/runs/.server_state/${game_name}_${timestamp}_${pid}.env"
  {
    echo "STARTED_SERVER=1"
    echo "SERVER_PID=$pid"
    echo "GAME_URL=$resolved_url"
    echo "LOG_FILE=$log_file"
  } >"$state_file"

  print_assignment STARTED_SERVER "1"
  print_assignment SERVER_PID "$pid"
  print_assignment SERVER_STATE_FILE "$state_file"
  print_assignment GAME_URL "$resolved_url"
}

stop_server() {
  local state_file=""
  local server_pid=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --state-file)
        state_file="$2"
        shift 2
        ;;
      --server-pid)
        server_pid="$2"
        shift 2
        ;;
      *)
        echo "Unknown stop arg: $1" >&2
        usage >&2
        return 2
        ;;
    esac
  done

  local started_server=""
  local state_pid=""

  if [[ -n "$state_file" && -f "$state_file" ]]; then
    # shellcheck disable=SC1090
    source "$state_file"
    started_server="${STARTED_SERVER:-}"
    state_pid="${SERVER_PID:-}"
  fi

  local pid="${server_pid:-$state_pid}"

  if [[ -z "$pid" ]]; then
    print_assignment STOP_RESULT "skipped_no_pid"
    return 0
  fi

  if [[ -n "$started_server" && "$started_server" != "1" ]]; then
    print_assignment STOP_RESULT "skipped_external_url"
    return 0
  fi

  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    for _ in {1..10}; do
      if ! kill -0 "$pid" 2>/dev/null; then
        break
      fi
      sleep 0.2
    done
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
    print_assignment STOP_RESULT "stopped"
  else
    print_assignment STOP_RESULT "already_stopped"
  fi

  if [[ -n "$state_file" && -f "$state_file" ]]; then
    rm -f "$state_file"
  fi
}

main() {
  if [[ $# -lt 1 ]]; then
    usage
    exit 2
  fi

  local cmd="$1"
  shift

  case "$cmd" in
    start)
      start_server "$@"
      ;;
    stop)
      stop_server "$@"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      echo "Unknown command: $cmd" >&2
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
