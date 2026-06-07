from __future__ import annotations

import os
import tomllib
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple

from harness.quota_control import QUOTA_ERROR_TYPE, extract_retry_after_hint, is_quota_exceeded_text
from harness.runner_utils import run_and_capture


SUPPORTED_BACKENDS = {"codex", "claude"}
DEFAULT_CODEX_MODEL_PROVIDER = "openai"

_BUILTIN_CODEX_PROVIDERS = {"openai"}

_GENERIC_TRANSPORT_ERROR_INDICATORS = (
    "stream disconnected before completion",
    "transport error:",
    "reconnecting...",
    "connection reset",
    "econnreset",
    "socket hang up",
    "network error",
    "timed out",
    "deadline exceeded",
    "internal server error",
    "server error",
)


def normalize_backend(value: Any) -> str:
    backend = str(value or "codex").strip().lower()
    if backend not in SUPPORTED_BACKENDS:
        raise ValueError(f"Unsupported backend: {backend}. Allowed: {sorted(SUPPORTED_BACKENDS)}")
    return backend


def backend_binary_name(backend: str) -> str:
    backend = normalize_backend(backend)
    if backend == "claude":
        return "claude"
    return "codex"


def codex_config_path() -> Path:
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    if codex_home:
        return Path(codex_home).expanduser() / "config.toml"
    return Path.home() / ".codex" / "config.toml"


def load_codex_config() -> Dict[str, Any]:
    path = codex_config_path()
    if not path.exists():
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_codex_model_provider() -> str:
    env_provider = os.environ.get("CODEX_MODEL_PROVIDER", "").strip()
    if env_provider:
        return env_provider
    cfg = load_codex_config()
    provider = str(cfg.get("model_provider", "")).strip()
    if provider:
        return provider
    return DEFAULT_CODEX_MODEL_PROVIDER


def codex_provider_is_declared(provider: str) -> bool:
    name = str(provider or "").strip()
    if not name:
        return False
    if name in _BUILTIN_CODEX_PROVIDERS:
        return True
    cfg = load_codex_config()
    providers = cfg.get("model_providers")
    return isinstance(providers, dict) and name in providers


def ensure_backend_available(backend: str) -> str:
    backend = normalize_backend(backend)
    name = backend_binary_name(backend)
    path = shutil.which(name)
    if path is None:
        raise FileNotFoundError(f"Required backend binary not found in PATH: {name}")
    if backend == "codex":
        provider = resolve_codex_model_provider()
        if not codex_provider_is_declared(provider):
            raise RuntimeError(
                f"Configured Codex model provider `{provider}` is not available in {codex_config_path()}."
            )
    return path


def map_reasoning_effort(backend: str, reasoning_effort: str) -> str:
    backend = normalize_backend(backend)
    effort = str(reasoning_effort or "").strip().lower()
    if not effort:
        return ""
    if backend == "claude":
        return {
            "xhigh": "max",
        }.get(effort, effort)
    return effort


def prepend_system_prompt(prompt: str, system_prompt: str) -> str:
    if not system_prompt.strip():
        return prompt
    return f"[SYSTEM CONTEXT]\n{system_prompt}\n\n[USER TASK]\n{prompt}"


def effective_system_prompt(backend: str, system_prompt: str) -> str:
    if normalize_backend(backend) != "claude":
        return ""
    return system_prompt


def sanitize_codex_extra_args(extra_args: List[Any]) -> Tuple[List[str], List[str]]:
    kept: List[str] = []
    dropped: List[str] = []

    i = 0
    raw = [str(x) for x in extra_args]
    while i < len(raw):
        token = raw[i]

        if token == "--search":
            dropped.append(token)
            i += 1
            continue
        if token in ("-a", "--ask-for-approval"):
            dropped.append(token)
            if i + 1 < len(raw):
                dropped.append(raw[i + 1])
                i += 2
            else:
                i += 1
            continue
        if token.startswith("--approval="):
            dropped.append(token)
            i += 1
            continue
        if token in ("-C", "--cd", "-s", "--sandbox"):
            dropped.append(token)
            if i + 1 < len(raw):
                dropped.append(raw[i + 1])
                i += 2
            else:
                i += 1
            continue

        kept.append(token)
        i += 1

    return kept, dropped


def _normalize_extra_args(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return [str(x) for x in raw]
    if raw is None:
        return []
    return [str(raw)]


def _has_codex_config_override(extra_args: List[str], key: str) -> bool:
    for i, token in enumerate(extra_args):
        if token == "-c" and i + 1 < len(extra_args):
            if str(extra_args[i + 1]).startswith(f"{key}="):
                return True
    return False


def _has_flag(extra_args: List[str], flag: str) -> bool:
    return any(token == flag or token.startswith(f"{flag}=") for token in extra_args)


def build_agent_cmd(
    repo: Path,
    *,
    backend: str,
    prompt: str,
    model: str = "",
    reasoning_effort: str = "",
    system_prompt: str = "",
    extra_args: Optional[List[Any]] = None,
    disable_multi_agent: bool = False,
    sandbox: str = "danger-full-access",
    approval: str = "never",
    allowed_dirs: Optional[List[Path]] = None,
) -> List[str]:
    backend = normalize_backend(backend)
    repo = repo.resolve()
    model = str(model or "").strip()
    effort = map_reasoning_effort(backend, reasoning_effort)
    system_prompt = effective_system_prompt(backend, system_prompt)
    raw_extra_args = _normalize_extra_args(extra_args)

    if backend == "codex":
        kept_extra_args, _ = sanitize_codex_extra_args(raw_extra_args)
        cmd = ["codex", "exec", "--cd", str(repo)]
        if sandbox:
            cmd.extend(["--sandbox", str(sandbox).strip()])
        if str(approval or "").strip().lower() == "never" and str(sandbox).strip() == "danger-full-access":
            cmd.append("--dangerously-bypass-approvals-and-sandbox")
        if model:
            cmd.extend(["-m", model])
        if not _has_codex_config_override(kept_extra_args, "model_provider"):
            cmd.extend(["-c", f'model_provider="{resolve_codex_model_provider()}"'])
        if effort and not _has_codex_config_override(kept_extra_args, "model_reasoning_effort"):
            cmd.extend(["-c", f'model_reasoning_effort="{effort}"'])
        if disable_multi_agent and not _has_codex_config_override(kept_extra_args, "features.multi_agent"):
            cmd.extend(["-c", "features.multi_agent=false"])
        cmd.extend(kept_extra_args)
        cmd.append(prepend_system_prompt(prompt, system_prompt))
        return cmd

    cmd = [
        "claude",
        "-p",
        "--output-format",
        "text",
        "--permission-mode",
        "bypassPermissions",
        "--no-session-persistence",
    ]
    allowed: List[Path] = [repo]
    for path in allowed_dirs or []:
        resolved = Path(path).resolve()
        if resolved not in allowed:
            allowed.append(resolved)
    for path in allowed:
        cmd.extend(["--add-dir", str(path)])
    if model:
        cmd.extend(["--model", model])
    if effort and not _has_flag(raw_extra_args, "--effort"):
        cmd.extend(["--effort", effort])
    if system_prompt.strip():
        cmd.extend(["--append-system-prompt", system_prompt])
    cmd.extend(raw_extra_args)
    cmd.extend(["--", prompt])
    return cmd


def cfg_int(agent_cfg: Dict[str, Any], key: str, default: int, minimum: int = 0) -> int:
    raw = agent_cfg.get(key, default)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    if value < minimum:
        return minimum
    return value


def parse_retry_error_types(agent_cfg: Dict[str, Any]) -> List[str]:
    raw = agent_cfg.get("retry_on_error_types", ["timeout", "transport_error"])
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str):
        text = raw.strip()
        return [text] if text else ["timeout", "transport_error"]
    return ["timeout", "transport_error"]


def is_retryable_failure(result: Dict[str, Any], retry_error_types: List[str]) -> bool:
    if result.get("return_code", 1) == 0:
        return False
    if "*" in retry_error_types:
        return True
    error_type = str(result.get("error_type", "")).strip()
    return bool(error_type and error_type in retry_error_types)


def get_attempt_log_path(base_log_path: Path, attempt_index: int) -> Path:
    if attempt_index <= 1:
        return base_log_path
    return base_log_path.with_name(f"{base_log_path.stem}.retry{attempt_index - 1}{base_log_path.suffix}")


def build_eval_agent_cfg(backend: str, agent_cfg: Dict[str, Any]) -> Dict[str, Any]:
    backend = normalize_backend(backend)
    cfg = dict(agent_cfg or {})
    if backend == "codex":
        cfg["disable_multi_agent"] = bool(cfg.get("disable_multi_agent_for_eval", True))
    return cfg


def _looks_like_transport_error(output: str) -> bool:
    lowered = output.lower()
    return any(indicator in lowered for indicator in _GENERIC_TRANSPORT_ERROR_INDICATORS)


def run_agent_once(
    repo: Path,
    backend: str,
    agent_cfg: Dict[str, Any],
    prompt: str,
    log_path: Path,
    dry_run: bool,
    attempt_index: int,
    total_attempts: int,
    *,
    system_prompt: str = "",
    allowed_dirs: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    backend = normalize_backend(backend)
    cmd = build_agent_cmd(
        repo=repo,
        backend=backend,
        prompt=prompt,
        model=str(agent_cfg.get("model", "")).strip(),
        reasoning_effort=str(agent_cfg.get("reasoning_effort", "")).strip(),
        system_prompt=system_prompt,
        extra_args=agent_cfg.get("extra_args", []),
        disable_multi_agent=bool(agent_cfg.get("disable_multi_agent", False)),
        sandbox=str(agent_cfg.get("sandbox", "danger-full-access")).strip(),
        approval=str(agent_cfg.get("approval", "never")).strip().lower(),
        allowed_dirs=allowed_dirs,
    )
    timeout_seconds = cfg_int(agent_cfg, "timeout_seconds", 1200, minimum=1)

    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        log_path.write_text(
            "DRY RUN\n"
            + " ".join(cmd)
            + "\n\nSYSTEM PROMPT:\n"
            + system_prompt
            + "\n\nPROMPT:\n"
            + prompt
            + "\n",
            encoding="utf-8",
        )
        ended = time.time()
        return {
            "command": cmd,
            "duration_sec": round(ended - started, 3),
            "return_code": 0,
            "status": "DRY_RUN",
            "executed": False,
            "attempt_index": attempt_index,
            "attempts_total": total_attempts,
        }

    log_preamble = (
        "COMMAND:\n"
        + " ".join(cmd)
        + "\n\n"
        + f"BACKEND:\n{backend}\n\n"
        + f"ATTEMPT:\n{attempt_index}/{total_attempts}\n\n"
        + "SYSTEM PROMPT:\n"
        + system_prompt
        + "\n\n"
        + "PROMPT:\n"
        + prompt
        + "\n\n"
        + f"TIMEOUT_SECONDS:\n{timeout_seconds}\n\n"
        + "OUTPUT:\n"
    )
    try:
        proc = run_and_capture(
            cmd,
            cwd=repo,
            env=None,
            timeout=timeout_seconds,
            log_path=log_path,
            log_preamble=log_preamble,
            timeout_note=f"\n[TIMEOUT] {backend} command exceeded {timeout_seconds}s and was terminated by runner.\n",
        )
        output = proc.stdout or ""
        ended = time.time()

        error_type = None
        if proc.returncode != 0:
            if is_quota_exceeded_text(output):
                error_type = QUOTA_ERROR_TYPE
            elif _looks_like_transport_error(output):
                error_type = "transport_error"

        result = {
            "command": cmd,
            "duration_sec": round(ended - started, 3),
            "return_code": proc.returncode,
            "status": "PASS" if proc.returncode == 0 else ("PAUSED" if error_type == QUOTA_ERROR_TYPE else "FAIL"),
            "executed": True,
            "attempt_index": attempt_index,
            "attempts_total": total_attempts,
        }
        if error_type:
            result["error_type"] = error_type
        if error_type == QUOTA_ERROR_TYPE:
            retry_after_hint = extract_retry_after_hint(output)
            if retry_after_hint:
                result["retry_after_hint"] = retry_after_hint
        return result
    except subprocess.TimeoutExpired as exc:
        ended = time.time()
        output = exc.output or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        error_type = QUOTA_ERROR_TYPE if is_quota_exceeded_text(output) else "timeout"
        result = {
            "command": cmd,
            "duration_sec": round(ended - started, 3),
            "return_code": 124,
            "status": "PAUSED" if error_type == QUOTA_ERROR_TYPE else "FAIL",
            "executed": True,
            "error_type": error_type,
            "attempt_index": attempt_index,
            "attempts_total": total_attempts,
        }
        if error_type == QUOTA_ERROR_TYPE:
            retry_after_hint = extract_retry_after_hint(output)
            if retry_after_hint:
                result["retry_after_hint"] = retry_after_hint
        else:
            result["error_detail"] = f"{backend} command exceeded timeout_seconds={timeout_seconds}"
        return result


def run_agent(
    repo: Path,
    backend: str,
    agent_cfg: Dict[str, Any],
    prompt: str,
    log_path: Path,
    dry_run: bool,
    *,
    system_prompt: str = "",
    allowed_dirs: Optional[List[Path]] = None,
) -> Dict[str, Any]:
    max_retries = cfg_int(agent_cfg, "max_retries", 0, minimum=0)
    retry_backoff_seconds = cfg_int(agent_cfg, "retry_backoff_seconds", 5, minimum=0)
    retry_error_types = parse_retry_error_types(agent_cfg)
    total_attempts = max_retries + 1

    attempt_results: List[Dict[str, Any]] = []
    attempt_log_paths: List[str] = []

    for attempt_index in range(1, total_attempts + 1):
        attempt_log_path = get_attempt_log_path(log_path, attempt_index)
        attempt_log_paths.append(str(attempt_log_path))
        result = run_agent_once(
            repo=repo,
            backend=backend,
            agent_cfg=agent_cfg,
            prompt=prompt,
            log_path=attempt_log_path,
            dry_run=dry_run,
            attempt_index=attempt_index,
            total_attempts=total_attempts,
            system_prompt=system_prompt,
            allowed_dirs=allowed_dirs,
        )
        attempt_results.append(result)

        if result.get("return_code", 1) == 0:
            break

        has_next_attempt = attempt_index < total_attempts
        if has_next_attempt and is_retryable_failure(result, retry_error_types):
            print(
                f"[RETRY] {backend} step failed with error_type={result.get('error_type', '<none>')} "
                f"(attempt {attempt_index}/{total_attempts}); retrying in {retry_backoff_seconds}s..."
            )
            if retry_backoff_seconds > 0 and not dry_run:
                time.sleep(retry_backoff_seconds)
            continue
        break

    final_result = dict(attempt_results[-1])
    final_result["attempt_count"] = len(attempt_results)
    final_result["attempt_log_paths"] = attempt_log_paths
    final_result["log_path"] = attempt_log_paths[-1]
    return final_result
