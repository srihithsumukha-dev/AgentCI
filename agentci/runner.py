
import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from agentci.evaluator import check_file_contains


def evaluate_task(project_dir, task_file, test_command=None):
    """Run text checks and optional behavioral tests."""
    project_dir = Path(project_dir).resolve()
    task_file = Path(task_file).resolve()

    with task_file.open("r", encoding="utf-8") as file:
        task = json.load(file)

    results = []

    for check in task.get("checks", []):
        passed, message = check_file_contains(
            project_dir,
            check["path"],
            check["contains"],
        )
        results.append({
            "check": check.get("name", check["path"]),
            "passed": passed,
            "message": message,
        })

    if test_command:
        try:
            completed = subprocess.run(
                test_command,
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=120,
                shell=False,
            )
            results.append({
                "check": "Behavioral tests",
                "passed": completed.returncode == 0,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-5000:],
                "stderr": completed.stderr[-5000:],
            })
        except subprocess.TimeoutExpired:
            results.append({
                "check": "Behavioral tests",
                "passed": False,
                "message": "Tests exceeded the 120-second timeout",
            })
        except OSError as exc:
            results.append({
                "check": "Behavioral tests",
                "passed": False,
                "message": f"Could not run tests: {exc}",
            })

    return {
        "task": task.get("name", task_file.stem),
        "passed": bool(results) and all(item["passed"] for item in results),
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="AgentCI evaluation runner")
    parser.add_argument("--project", required=True, help="Project directory")
    parser.add_argument("--task", required=True, help="JSON task file")
    parser.add_argument(
        "--trace",
        default=None,
        help="Optional explicit trace file path",
    )
    parser.add_argument(
        "--test",
        help='Optional test command, e.g. "python -m unittest tests.test_parse_items -v"',
    )
    args = parser.parse_args()

    test_command = shlex.split(args.test) if args.test else None
    report = evaluate_task(args.project, args.task, test_command)
    report["timestamp"] = datetime.now(timezone.utc).isoformat()
    report["project"] = str(Path(args.project).resolve())

    if args.trace:
        trace_path = Path(args.trace).resolve()
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        trace_path = (Path("traces") / f"run_{timestamp}.json").resolve()

    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
