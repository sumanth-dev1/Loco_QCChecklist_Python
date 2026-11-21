import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import subprocess
from flask import Blueprint, jsonify

update_version_bp = Blueprint('update_version', __name__)


def _git_subprocess_kwargs(env, timeout=15):
    kwargs = {
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "stdin": subprocess.DEVNULL,
        "env": env,
        "timeout": timeout,
    }
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        if creationflags:
            kwargs["creationflags"] = creationflags
        if hasattr(subprocess, "STARTUPINFO"):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
            startupinfo.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
            kwargs["startupinfo"] = startupinfo
    return kwargs


def _run_git(cmd, cwd, env, timeout=15):
    return subprocess.run(cmd, cwd=cwd, **_git_subprocess_kwargs(env, timeout=timeout))


@update_version_bp.route('/update_version', methods=['GET', 'POST'])
def update_version():
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GIT_ASKPASS'] = 'echo'
    env['GCM_INTERACTIVE'] = 'never'

    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if not os.path.exists(os.path.join(repo, '.git')):
        return jsonify({"status": "uptodate", "message": "Running in production without local git repo."})

    git = "git"
    step = "init"

    try:
        # Ensure repo is registered as safe.directory without appending duplicates
        safe_repo = repo.replace('\\', '/')
        safe_dirs_proc = _run_git([git, "config", "--global", "--get-all", "safe.directory"], cwd=repo, env=env)
        existing_safe_dirs = [line.strip() for line in (safe_dirs_proc.stdout or "").splitlines() if line.strip()]
        has_safe_dir = any(
            (d.lower() == safe_repo.lower() if os.name == "nt" else d == safe_repo)
            for d in existing_safe_dirs
        )
        if not has_safe_dir:
            _run_git([git, "config", "--global", "--add", "safe.directory", safe_repo], cwd=repo, env=env)

        step = "branch"
        branch_proc = _run_git([git, "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo, env=env)
        current_branch = (branch_proc.stdout or "").strip() or 'main'

        step = "fetch"
        fetch_proc = _run_git([git, "fetch", "origin", current_branch], cwd=repo, env=env, timeout=30)
        if fetch_proc.returncode != 0:
            output_lines = ((fetch_proc.stdout or "") + (fetch_proc.stderr or "")).splitlines()
            return jsonify({
                "status": "error",
                "step": "fetch",
                "output": output_lines
            })

        step = "compare"
        local_proc = _run_git([git, "rev-parse", "HEAD"], cwd=repo, env=env)
        remote_proc = _run_git([git, "rev-parse", f"origin/{current_branch}"], cwd=repo, env=env)

        local = (local_proc.stdout or "").strip()
        remote = (remote_proc.stdout or "").strip()

        if local == remote:
            return jsonify({"status": "uptodate"})

        # Automatic backup before update
        backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        step = "pull"
        _run_git([git, "reset", "--hard"], cwd=repo, env=env)
        _run_git([git, "clean", "-fd"], cwd=repo, env=env)
        pull_proc = _run_git([git, "pull", "origin", current_branch], cwd=repo, env=env, timeout=60)

        commit_after_proc = _run_git([git, "rev-parse", "HEAD"], cwd=repo, env=env)
        commit_after = (commit_after_proc.stdout or "").strip()

        if pull_proc.returncode == 0:
            if local != commit_after:
                return jsonify({"status": "updated"})
            else:
                return jsonify({"status": "uptodate"})
        else:
            output_lines = ((pull_proc.stdout or "") + (pull_proc.stderr or "")).splitlines()
            return jsonify({
                "status": "error",
                "step": "pull",
                "output": output_lines
            })
    except subprocess.TimeoutExpired as e:
        return jsonify({
            "status": "error",
            "step": step,
            "output": [f"Git command timed out after {e.timeout}s"]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "step": step,
            "output": [str(e)]
        })

