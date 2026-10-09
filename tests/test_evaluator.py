from agentci.evaluator import check_file_contains


def test_file_contains_expected_text(tmp_path):
    (tmp_path / "parser.py").write_text(
        "def handle_empty():\n    return []\n",
        encoding="utf-8",
    )

    passed, message = check_file_contains(
        tmp_path, "parser.py", "handle_empty"
    )

    assert passed is True
    assert "Found expected text" in message


def test_file_missing_expected_text(tmp_path):
    (tmp_path / "parser.py").write_text(
        "def parse():\n    pass\n",
        encoding="utf-8",
    )

    passed, message = check_file_contains(
        tmp_path, "parser.py", "handle_empty"
    )

    assert passed is False
    assert "Expected text not found" in message


def test_reject_path_outside_project(tmp_path):
    passed, message = check_file_contains(
        tmp_path, "../outside.py", "anything"
    )

    assert passed is False
    assert "Path escapes" in message
def test_reject_absolute_path_outside_project(tmp_path):
    outside_file = tmp_path.parent / "agentci_outside_test.txt"
    outside_file.write_text("secret", encoding="utf-8")

    try:
        passed, message = check_file_contains(
            tmp_path, str(outside_file), "secret"
        )

        assert passed is False
        assert "Path escapes" in message
    finally:
        outside_file.unlink(missing_ok=True)