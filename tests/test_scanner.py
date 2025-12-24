"""Tests for project scanner."""

import tempfile
from pathlib import Path

from readme_gen.scanner import scan_project


def test_detect_python_project():
    """Detect Python project from pyproject.toml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "pyproject.toml").write_text('''
[project]
name = "test-project"
description = "A test project"
dependencies = ["click>=8.0", "rich>=13.0"]

[project.scripts]
testcli = "test:main"
''')
        context = scan_project(path)

        assert context["type"] == "python"
        assert context["name"] == "test-project"
        assert context["description"] == "A test project"
        assert "click" in context["dependencies"]
        assert context["entry_command"] == "testcli"


def test_detect_node_project():
    """Detect Node.js project from package.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "package.json").write_text('''{
  "name": "my-node-app",
  "description": "A Node.js app",
  "scripts": {"start": "node index.js"},
  "dependencies": {"express": "^4.0"}
}''')
        context = scan_project(path)

        assert context["type"] == "node"
        assert context["name"] == "my-node-app"
        assert context["entry_command"] == "npm start"
        assert "express" in context["dependencies"]


def test_collect_files():
    """Collect files excluding ignored directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "main.py").write_text("")
        (path / "src").mkdir()
        (path / "src" / "app.py").write_text("")
        (path / "node_modules").mkdir()
        (path / "node_modules" / "pkg.js").write_text("")

        context = scan_project(path)

        assert "main.py" in context["files"]
        assert "src/app.py" in context["files"]
        # node_modules should be ignored
        assert not any("node_modules" in f for f in context["files"])
