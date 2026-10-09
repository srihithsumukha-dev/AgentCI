
import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from agentci.gemma_client import suggest_fix


def extract_python_code(response):
    """Extract code from a Python Markdown block."""
    matches = re.findall(
        r"```(?:python)?\s*(.*?)```",
        response,
        re.DOTALL | re.IGNORECASE,
    )
    for candidate in matches:
        if candidate.strip():
            return candidate.strip() + "\n"

    raise ValueError("Gemma did not return a recognizable fenced code block")


def run_repair(project_dir, task_file, target_file, test_command):
    """Evaluate a proposed fix in a temporary copy of the project."""
    project_dir = Path(project_dir).resolve()
    task_file = Path(task_file).resolve()
    target_file = Path(target_file)

    target = (project_dir / target_file).resolve()
    target.relative_to(project_dir)

    if not target.is_file():
        raise FileNotFoundError(f"Target file not found: {target_file}")

    original_code = target.read_text(encoding="utf-8")
    task = json.loads(task_file.read_text(encoding="utf-8"))
    description = task.get("description") or task.get(
        "name", "Fix the failing code"
    )

    response = suggest_fix(description, original_code)
    proposed_code = extract_python_code(response)

    with tempfile.TemporaryDirectory(prefix="agentci_repair_") as temp:
        workspace = Path(temp) / "project"
        shutil.copytree(
            project_dir,
            workspace,
            ignore=shutil.ignore_patterns(
                ".git", ".venv", "venv", "__pycache__", "traces"
            ),
        )

        trial_target = (workspace / target_file).resolve()
        trial_target.relative_to(workspace)
        trial_target.write_text(proposed_code, encoding="utf-8")

        task_copy = workspace / task_file.relative_to(project_dir)

        command = [
            sys.executable,
            "-m",
            "agentci.runner",
            "--project",
            str(workspace),
            "--task",
            str(task_copy),
            "--test",
            shlex.join(test_command),
        ]

        completed = subprocess.run(
            command,
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=180,
        )

        try:
            evaluation = json.loads(completed.stdout)
        except json.JSONDecodeError:
            evaluation = {
                "passed": False,
                "error": "Could not parse AgentCI report",
                "stdout": completed.stdout[-3000:],
                "stderr": completed.stderr[-3000:],
            }

        return {
            "task": task.get("name", task_file.stem),
            "target_file": str(target_file),
            "original_preserved": (
                target.read_text(encoding="utf-8") == original_code
            ),
            "model_response": response,
            "evaluation": evaluation,
            "repair_accepted": bool(evaluation.get("passed", False)),
        }


def main():
    parser = argparse.ArgumentParser(description="AgentCI Gemma repair loop")
    parser.add_argument("--project", default=".", help="Project directory")
    parser.add_argument("--task", required=True, help="Task JSON file")
    parser.add_argument("--target", required=True, help="Target Python file")
    parser.add_argument(
        "--test",
        required=True,
        help='Test command, e.g. "python -m unittest tests.test_parse_items -v"',
    )
    args = parser.parse_args()

    try:
        report = run_repair(
            args.project,
            args.task,
            args.target,
            shlex.split(args.test),
        )
    except Exception as exc:
        print(json.dumps({
            "repair_accepted": False,
            "error": f"{type(exc).__name__}: {exc}",
        }, indent=2))
        raise SystemExit(1)

    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["repair_accepted"] else 1)


if __name__ == "__main__":
    main()
