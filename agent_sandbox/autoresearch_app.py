"""Dedicated Modal entrypoints for running karpathy/autoresearch."""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

import modal

from agent_sandbox.autoresearch import (
    append_result_row,
    branch_name,
    build_claude_baseline_prompt,
    build_paths,
    ensure_results_file,
    is_data_ready,
    parse_training_summary,
)
from agent_sandbox.config.settings import get_modal_secrets, get_settings
from agent_sandbox.utils.cli import (
    CLAUDE_CLI_APP_ROOT,
    CLAUDE_CLI_USER,
    claude_cli_env,
    demote_to_claude,
    maybe_chown_for_claude,
    require_claude_cli_auth,
)

_settings = get_settings()
_logger = logging.getLogger(__name__)

AUTORESEARCH_APP_NAME = "autoresearch-modal"
AUTORESEARCH_WORKSPACE_VOLUME = modal.Volume.from_name(
    _settings.autoresearch_workspace_vol_name,
    create_if_missing=True,
)
AUTORESEARCH_CACHE_VOLUME = modal.Volume.from_name(
    _settings.autoresearch_cache_vol_name,
    create_if_missing=True,
)
AUTORESEARCH_VOLUMES = {
    _settings.autoresearch_workspace_root: AUTORESEARCH_WORKSPACE_VOLUME,
    _settings.autoresearch_cache_root: AUTORESEARCH_CACHE_VOLUME,
}
AUTORESEARCH_IGNORE = [
    ".agent",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "*.egg-info",
    "*.pyc",
    ".DS_Store",
    "docs",
    "tests",
]


def _build_autoresearch_image() -> modal.Image:
    """Build the Modal image used for autoresearch preparation and execution."""
    return (
        modal.Image.debian_slim(python_version="3.11")
        .apt_install("curl", "git")
        .uv_pip_install(
            "uv",
            "kernels>=0.11.7",
            "matplotlib>=3.10.8",
            "numpy>=2.2.6",
            "pandas>=2.3.3",
            "pyarrow>=21.0.0",
            "requests>=2.32.0",
            "rustbpe>=0.1.0",
            "tiktoken>=0.11.0",
            "torch==2.9.1",
        )
        .run_commands(
            "curl -fsSL https://deb.nodesource.com/setup_20.x | bash -",
            "apt-get install -y nodejs",
            "useradd -m -s /bin/bash -U claude",
            "su -l claude -c 'curl -fsSL https://claude.ai/install.sh | bash'",
        )
        .env(
            {
                "PATH": (
                    "/root/.local/bin:/root/.claude/bin:"
                    "/home/claude/.local/bin:/home/claude/.claude/bin:"
                    "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
                ),
                "PYTHONUNBUFFERED": "1",
            }
        )
        .workdir(str(CLAUDE_CLI_APP_ROOT))
        .add_local_dir(
            ".",
            remote_path=str(CLAUDE_CLI_APP_ROOT),
            copy=True,
            ignore=AUTORESEARCH_IGNORE,
        )
        .run_commands(
            f"chown -R {CLAUDE_CLI_USER}:{CLAUDE_CLI_USER} {CLAUDE_CLI_APP_ROOT}",
            f"cd {CLAUDE_CLI_APP_ROOT} && uv pip install -e . --system --no-cache",
        )
    )


app = modal.App(AUTORESEARCH_APP_NAME)
autoresearch_image = _build_autoresearch_image()


def _subprocess_kwargs(as_claude: bool, env: dict[str, str] | None = None) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"text": True}
    if as_claude:
        kwargs["env"] = env or claude_cli_env()
        kwargs["preexec_fn"] = demote_to_claude()
    elif env is not None:
        kwargs["env"] = env
    return kwargs


def _autoresearch_env(cache_dir: Path | None = None) -> dict[str, str]:
    """Build the runtime environment for repo-local autoresearch commands."""
    env = claude_cli_env()
    active_cache_dir = cache_dir or Path(_settings.autoresearch_cache_root)
    env["TRITON_CACHE_DIR"] = str(active_cache_dir / "triton-cache")
    env["TORCHINDUCTOR_CACHE_DIR"] = str(active_cache_dir / "inductor-cache")
    return env


def _run_command(
    cmd: list[str],
    *,
    cwd: Path,
    timeout: int,
    as_claude: bool = False,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a command in the autoresearch workspace."""
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        timeout=timeout,
        **_subprocess_kwargs(as_claude, env),
    )
    if check and result.returncode != 0:
        message = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Command failed ({result.returncode}): {' '.join(cmd)}\n{message}")
    return result


def _run_command_to_log(
    cmd: list[str],
    *,
    cwd: Path,
    log_path: Path,
    timeout: int,
    as_claude: bool = False,
    env: dict[str, str] | None = None,
) -> None:
    """Run a command and redirect stdout/stderr to a log file."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=handle,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            **_subprocess_kwargs(as_claude, env),
        )
    if result.returncode != 0:
        tail = _tail_file(log_path)
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\nLast log lines:\n{tail}"
        )


def _tail_file(path: Path, lines: int = 80) -> str:
    """Return the last N lines of a file for error reporting."""
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(content[-lines:])


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    maybe_chown_for_claude(path)


def _git(repo_dir: Path, *args: str, timeout: int = 300, check: bool = True) -> str:
    result = _run_command(
        ["git", *args],
        cwd=repo_dir,
        timeout=timeout,
        as_claude=True,
        check=check,
    )
    return (result.stdout or "").strip()


def _commit_volumes() -> None:
    for volume in (AUTORESEARCH_WORKSPACE_VOLUME, AUTORESEARCH_CACHE_VOLUME):
        try:
            volume.commit()
        except RuntimeError as exc:
            if "running function" not in str(exc):
                _logger.warning("Failed to commit volume: %s", exc)


def _bootstrap_workspace(run_tag: str) -> tuple[Any, str]:
    paths = build_paths(
        _settings.autoresearch_workspace_root,
        _settings.autoresearch_cache_root,
        run_tag,
    )
    _ensure_dir(paths.workspace_root)
    _ensure_dir(paths.run_root)
    _ensure_dir(paths.cache_dir)
    _ensure_dir(paths.cache_dir / "triton-cache")
    _ensure_dir(paths.cache_dir / "inductor-cache")

    if not paths.repo_dir.exists():
        _run_command(
            ["git", "clone", _settings.autoresearch_repo_url, paths.repo_dir.name],
            cwd=paths.run_root,
            timeout=600,
            as_claude=True,
        )
    else:
        _git(paths.repo_dir, "remote", "set-url", "origin", _settings.autoresearch_repo_url)
        _git(paths.repo_dir, "fetch", "origin", "--prune", timeout=600)

    _git(paths.repo_dir, "config", "user.name", _settings.autoresearch_git_user_name)
    _git(paths.repo_dir, "config", "user.email", _settings.autoresearch_git_user_email)

    target_branch = branch_name(run_tag)
    existing_branch = _git(paths.repo_dir, "branch", "--list", target_branch)
    if existing_branch:
        _git(paths.repo_dir, "checkout", target_branch)
    else:
        _git(paths.repo_dir, "fetch", "origin", _settings.autoresearch_base_branch, timeout=600)
        _git(
            paths.repo_dir,
            "checkout",
            "-B",
            _settings.autoresearch_base_branch,
            f"origin/{_settings.autoresearch_base_branch}",
        )
        _git(paths.repo_dir, "checkout", "-b", target_branch)

    ensure_results_file(paths.results_path)
    maybe_chown_for_claude(paths.results_path)
    _commit_volumes()
    return paths, target_branch


def _prepare_if_needed(paths: Any, num_shards: int) -> bool:
    if is_data_ready(paths.cache_dir):
        return False
    _run_command_to_log(
        ["python", "prepare.py", "--num-shards", str(num_shards)],
        cwd=paths.repo_dir,
        log_path=paths.run_root / "prepare.log",
        timeout=_settings.autoresearch_prepare_timeout,
        as_claude=True,
        env=_autoresearch_env(paths.cache_dir),
    )
    _commit_volumes()
    return True


def _current_commit(repo_dir: Path) -> str:
    return _git(repo_dir, "rev-parse", "--short", "HEAD")


def _train_baseline(paths: Any, description: str) -> dict[str, Any]:
    _run_command_to_log(
        ["python", "train.py"],
        cwd=paths.repo_dir,
        log_path=paths.run_log_path,
        timeout=_settings.autoresearch_train_timeout,
        as_claude=True,
        env=_autoresearch_env(paths.cache_dir),
    )
    summary = parse_training_summary(
        paths.run_log_path.read_text(encoding="utf-8", errors="ignore")
    )
    commit = _current_commit(paths.repo_dir)
    append_result_row(
        paths.results_path,
        commit=commit,
        val_bpb=summary.val_bpb,
        memory_gb=summary.peak_vram_mb / 1024,
        status="keep",
        description=description,
    )
    maybe_chown_for_claude(paths.results_path)
    _commit_volumes()
    return {
        "run_log_path": str(paths.run_log_path),
        "results_path": str(paths.results_path),
        "commit": commit,
        "summary": {
            "val_bpb": summary.val_bpb,
            "training_seconds": summary.training_seconds,
            "total_seconds": summary.total_seconds,
            "peak_vram_mb": summary.peak_vram_mb,
            "mfu_percent": summary.mfu_percent,
            "total_tokens_m": summary.total_tokens_m,
            "num_steps": summary.num_steps,
            "num_params_m": summary.num_params_m,
            "depth": summary.depth,
        },
    }


def _run_claude(prompt: str, *, cwd: Path, max_turns: int, timeout: int) -> str:
    env = _autoresearch_env(Path(_settings.autoresearch_cache_root))
    require_claude_cli_auth(env)
    result = _run_command(
        [
            "claude",
            "-p",
            prompt,
            "--output-format",
            "text",
            "--dangerously-skip-permissions",
            "--max-turns",
            str(max_turns),
        ],
        cwd=cwd,
        timeout=timeout,
        as_claude=True,
        env=env,
    )
    return (result.stdout or result.stderr or "").strip()


@app.function(image=autoresearch_image, volumes=AUTORESEARCH_VOLUMES, timeout=600)
def probe_autoresearch_environment() -> dict[str, str]:
    """Verify the runtime image has the required CLI surface."""
    versions = {
        "python": _run_command(
            ["python", "--version"], cwd=CLAUDE_CLI_APP_ROOT, timeout=30
        ).stdout.strip(),
        "git": _run_command(
            ["git", "--version"], cwd=CLAUDE_CLI_APP_ROOT, timeout=30
        ).stdout.strip(),
        "claude": _run_command(
            ["claude", "--version"],
            cwd=CLAUDE_CLI_APP_ROOT,
            timeout=30,
            as_claude=True,
        ).stdout.strip(),
    }
    versions["workspace_root"] = _settings.autoresearch_workspace_root
    versions["cache_root"] = _settings.autoresearch_cache_root
    return versions


@app.function(
    image=autoresearch_image,
    volumes=AUTORESEARCH_VOLUMES,
    timeout=_settings.autoresearch_prepare_timeout,
)
def prepare_autoresearch_run(run_tag: str, num_shards: int | None = None) -> dict[str, Any]:
    """Clone the upstream repo, create the run branch, and prepare data if needed."""
    paths, target_branch = _bootstrap_workspace(run_tag)
    prepared = _prepare_if_needed(
        paths,
        _settings.autoresearch_prepare_num_shards if num_shards is None else num_shards,
    )
    return {
        "run_tag": run_tag,
        "branch": target_branch,
        "repo_dir": str(paths.repo_dir),
        "cache_dir": str(paths.cache_dir),
        "results_path": str(paths.results_path),
        "prepared": prepared,
        "data_ready": is_data_ready(paths.cache_dir),
        "commit": _current_commit(paths.repo_dir),
    }


@app.function(
    image=autoresearch_image,
    volumes=AUTORESEARCH_VOLUMES,
    gpu=_settings.autoresearch_gpu,
    timeout=_settings.autoresearch_train_timeout,
)
def run_autoresearch_baseline(run_tag: str, prepare_if_missing: bool = True) -> dict[str, Any]:
    """Run one direct baseline experiment without Claude in the loop."""
    paths, target_branch = _bootstrap_workspace(run_tag)
    if prepare_if_missing:
        _prepare_if_needed(paths, _settings.autoresearch_prepare_num_shards)
    if not is_data_ready(paths.cache_dir):
        raise RuntimeError("Autoresearch cache is not ready. Run prepare_autoresearch_run first.")
    result = _train_baseline(paths, description="baseline")
    result.update(
        {
            "run_tag": run_tag,
            "branch": target_branch,
            "repo_dir": str(paths.repo_dir),
        }
    )
    return result


@app.function(
    image=autoresearch_image,
    volumes=AUTORESEARCH_VOLUMES,
    gpu=_settings.autoresearch_gpu,
    secrets=get_modal_secrets(),
    timeout=_settings.autoresearch_claude_timeout,
)
def run_autoresearch_with_claude(
    run_tag: str,
    prompt: str | None = None,
    max_turns: int = 16,
    prepare_if_missing: bool = True,
) -> dict[str, Any]:
    """Run a bounded Claude-driven autoresearch session inside the GPU container."""
    paths, target_branch = _bootstrap_workspace(run_tag)
    if prepare_if_missing:
        _prepare_if_needed(paths, _settings.autoresearch_prepare_num_shards)
    if not is_data_ready(paths.cache_dir):
        raise RuntimeError("Autoresearch cache is not ready. Run prepare_autoresearch_run first.")

    cli_prompt = prompt or build_claude_baseline_prompt(
        run_tag,
        _settings.autoresearch_prepare_num_shards,
    )
    cli_output = _run_claude(
        cli_prompt,
        cwd=paths.repo_dir,
        max_turns=max_turns,
        timeout=_settings.autoresearch_claude_timeout,
    )

    payload: dict[str, Any] = {
        "run_tag": run_tag,
        "branch": target_branch,
        "repo_dir": str(paths.repo_dir),
        "results_path": str(paths.results_path),
        "cli_output": cli_output,
    }
    if paths.run_log_path.exists():
        try:
            summary = parse_training_summary(
                paths.run_log_path.read_text(encoding="utf-8", errors="ignore")
            )
        except ValueError:
            payload["run_log_tail"] = _tail_file(paths.run_log_path)
        else:
            payload["summary"] = {
                "val_bpb": summary.val_bpb,
                "training_seconds": summary.training_seconds,
                "total_seconds": summary.total_seconds,
                "peak_vram_mb": summary.peak_vram_mb,
                "mfu_percent": summary.mfu_percent,
                "total_tokens_m": summary.total_tokens_m,
                "num_steps": summary.num_steps,
                "num_params_m": summary.num_params_m,
                "depth": summary.depth,
            }
    _commit_volumes()
    return payload


@app.local_entrypoint()
def main(
    mode: str = "probe",
    run_tag: str = "smoke",
    num_shards: int = 10,
) -> None:
    """Convenience local entrypoint for common autoresearch flows."""
    if mode == "probe":
        result = probe_autoresearch_environment.remote()
    elif mode == "prepare":
        result = prepare_autoresearch_run.remote(run_tag=run_tag, num_shards=num_shards)
    elif mode == "baseline":
        result = run_autoresearch_baseline.remote(run_tag=run_tag)
    elif mode == "claude-baseline":
        result = run_autoresearch_with_claude.remote(run_tag=run_tag)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    print(json.dumps(result, indent=2, sort_keys=True))
