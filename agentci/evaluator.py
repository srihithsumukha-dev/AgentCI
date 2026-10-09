from pathlib import Path


def check_file_contains(project_dir, path, pattern):
    """Check a file stays within the project and contains expected text."""
    root = Path(project_dir).resolve()

    try:
        target = (root / path).resolve()
        target.relative_to(root)
    except (ValueError, OSError, RuntimeError):
        return False, "Path escapes project directory or cannot be resolved"

    if not target.is_file():
        return False, f"File not found: {path}"

    try:
        content = target.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return False, f"Could not read file: {exc}"

    if pattern in content:
        return True, f"Found expected text in {path}"

    return False, f"Expected text not found in {path}"