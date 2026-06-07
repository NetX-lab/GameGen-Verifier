from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional


def run_and_capture(
    cmd: List[str],
    *,
    cwd: Path,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    log_path: Optional[Path] = None,
    log_preamble: str = "",
    timeout_note: Optional[str] = None,
    echo_output: bool = True,
    line_handler: Optional[Callable[[str], None]] = None,
    progress_callback: Optional[Callable[[], Optional[str]]] = None,
    progress_interval_sec: float = 15.0,
    progress_to_log: bool = False,
) -> subprocess.CompletedProcess:
    log_handle = None
    try:
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_handle = log_path.open("w", encoding="utf-8")
            if log_preamble:
                log_handle.write(log_preamble)
                log_handle.flush()

        popen_kwargs = {
            "cwd": str(cwd),
            "env": env,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "text": True,
            "bufsize": 1,
        }
        if os.name != "nt":
            # Put the child in its own process group so timeout cleanup can
            # terminate the full codex/node subtree instead of only the wrapper.
            popen_kwargs["start_new_session"] = True

        proc = subprocess.Popen(
            cmd,
            **popen_kwargs,
        )
        assert proc.stdout is not None

        chunks: List[str] = []

        def pump_stdout() -> None:
            try:
                for line in proc.stdout:
                    chunks.append(line)
                    if line_handler is not None:
                        try:
                            line_handler(line)
                        except Exception:
                            pass
                    if log_handle is not None:
                        log_handle.write(line)
                        log_handle.flush()
                    if echo_output:
                        sys.stdout.write(line)
                        sys.stdout.flush()
            except ValueError:
                # stdout can be closed during KeyboardInterrupt/teardown.
                return

        reader = threading.Thread(target=pump_stdout, daemon=True)
        reader.start()

        deadline = time.monotonic() + timeout if timeout is not None else None
        next_progress = (
            time.monotonic() + progress_interval_sec
            if progress_callback is not None and progress_interval_sec > 0
            else None
        )

        try:
            while True:
                wait_timeout = None
                now = time.monotonic()
                if deadline is not None:
                    remaining = deadline - now
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout, output="".join(chunks))
                    wait_timeout = remaining
                if next_progress is not None:
                    until_progress = max(0.0, next_progress - now)
                    wait_timeout = (
                        min(wait_timeout, until_progress)
                        if wait_timeout is not None
                        else until_progress
                    )
                try:
                    if wait_timeout is None:
                        return_code = proc.wait()
                    else:
                        return_code = proc.wait(timeout=wait_timeout)
                    break
                except subprocess.TimeoutExpired:
                    now = time.monotonic()
                    if deadline is not None and now >= deadline:
                        raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout, output="".join(chunks))
                    if next_progress is not None and now >= next_progress:
                        progress_line = progress_callback() if progress_callback is not None else None
                        if progress_line:
                            progress_text = progress_line.rstrip("\n") + "\n"
                            if echo_output:
                                sys.stdout.write(progress_text)
                                sys.stdout.flush()
                            if progress_to_log and log_handle is not None:
                                log_handle.write(progress_text)
                                log_handle.flush()
                        next_progress = now + progress_interval_sec
            reader.join()
        except subprocess.TimeoutExpired:
            if proc.poll() is None:
                try:
                    if os.name != "nt":
                        os.killpg(proc.pid, signal.SIGKILL)
                    else:
                        proc.kill()
                except ProcessLookupError:
                    pass
                except Exception:
                    proc.kill()
            reader.join()
            output = "".join(chunks)
            note = timeout_note or f"\n[TIMEOUT] process exceeded {timeout}s and was terminated.\n"
            if log_handle is not None:
                log_handle.write(note)
                log_handle.flush()
            if echo_output:
                sys.stdout.write(note)
                sys.stdout.flush()
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=timeout, output=output)
        finally:
            proc.stdout.close()

        return subprocess.CompletedProcess(
            cmd,
            return_code,
            stdout="".join(chunks),
            stderr=None,
        )
    finally:
        if log_handle is not None:
            log_handle.close()
