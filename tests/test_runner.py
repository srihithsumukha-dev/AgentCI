import json

from agentci.runner import evaluate_task


def test_runner_passes_when_check_succeeds(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "parser.py").write_text(
        "def handle_empty():\n    return []\n",
        encoding="utf-8",
    )

    task_file = tmp_path / "task.json"
    task_file.write_text(
        json.dumps({
            "name": "empty-input test",
            "checks": [
                {
                    "name": "handler exists",
                    "path": "parser.py",
                    "contains": "handle_empty",
                }
            ],
        }),
        encoding="utf-8",
    )

    report = evaluate_task(project, task_file)

    assert report["passed"] is True
    assert report["results"][0]["passed"] is True


def test_runner_fails_when_check_fails(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "parser.py").write_text(
        "def parse():\n    pass\n",
        encoding="utf-8",
    )

    task_file = tmp_path / "task.json"
    task_file.write_text(
        json.dumps({
            "name": "empty-input test",
            "checks": [
                {
                    "name": "handler exists",
                    "path": "parser.py",
                    "contains": "handle_empty",
                }
            ],
        }),
        encoding="utf-8",
    )

    report = evaluate_task(project, task_file)

    assert report["passed"] is False
    assert report["results"][0]["passed"] is False