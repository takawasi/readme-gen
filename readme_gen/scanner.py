"""Project scanner - Extract context for README generation."""

from pathlib import Path
from typing import Dict, Any
import json


def scan_project(path: Path) -> Dict[str, Any]:
    """Scan project and extract context for README generation.

    Returns dict with:
        - name: project name
        - type: python/node/go/rust/unknown
        - description: from package config
        - languages: detected languages
        - entry_command: how to run
        - install_command: how to install
        - features: detected features
        - dependencies: key dependencies
    """
    context = {
        'name': path.name,
        'type': 'unknown',
        'description': '',
        'languages': [],
        'entry_command': '',
        'install_command': '',
        'features': [],
        'dependencies': [],
        'files': [],
    }

    # Collect file list for LLM context
    context['files'] = _collect_files(path)

    # Detect project type
    _detect_python(path, context)
    _detect_node(path, context)
    _detect_go(path, context)
    _detect_rust(path, context)

    return context


def _collect_files(path: Path, max_files: int = 50) -> list:
    """Collect file list for context."""
    ignore = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build'}
    files = []

    for item in path.rglob('*'):
        if any(ignored in item.parts for ignored in ignore):
            continue
        if item.is_file():
            rel_path = str(item.relative_to(path))
            files.append(rel_path)
            if len(files) >= max_files:
                break

    return files


def _detect_python(path: Path, context: Dict):
    """Detect Python project details."""
    # pyproject.toml
    pyproject = path / 'pyproject.toml'
    if pyproject.exists():
        context['type'] = 'python'
        context['languages'].append('Python')
        context['install_command'] = 'pip install .'

        try:
            import tomllib
            with open(pyproject, 'rb') as f:
                data = tomllib.load(f)

            project = data.get('project', {})
            context['description'] = project.get('description', '')
            context['name'] = project.get('name', context['name'])

            # Entry point
            scripts = project.get('scripts', {})
            if scripts:
                cmd = list(scripts.keys())[0]
                context['entry_command'] = cmd

            # Dependencies
            deps = project.get('dependencies', [])
            context['dependencies'] = [d.split('>=')[0].split('==')[0] for d in deps[:5]]

        except Exception:
            pass

    # requirements.txt fallback
    reqs = path / 'requirements.txt'
    if reqs.exists() and context['type'] == 'unknown':
        context['type'] = 'python'
        context['languages'].append('Python')
        context['install_command'] = 'pip install -r requirements.txt'


def _detect_node(path: Path, context: Dict):
    """Detect Node.js project details."""
    package = path / 'package.json'
    if package.exists():
        context['type'] = 'node'
        context['languages'].append('JavaScript')
        context['install_command'] = 'npm install'

        try:
            data = json.loads(package.read_text())
            context['description'] = data.get('description', '')
            context['name'] = data.get('name', context['name'])

            # Entry point
            scripts = data.get('scripts', {})
            if 'start' in scripts:
                context['entry_command'] = 'npm start'
            elif 'dev' in scripts:
                context['entry_command'] = 'npm run dev'

            # Dependencies
            deps = list(data.get('dependencies', {}).keys())[:5]
            context['dependencies'] = deps

        except Exception:
            pass

    # TypeScript
    if (path / 'tsconfig.json').exists():
        if 'TypeScript' not in context['languages']:
            context['languages'].append('TypeScript')


def _detect_go(path: Path, context: Dict):
    """Detect Go project details."""
    gomod = path / 'go.mod'
    if gomod.exists():
        context['type'] = 'go'
        context['languages'].append('Go')
        context['install_command'] = 'go install'
        context['entry_command'] = f'go run .'


def _detect_rust(path: Path, context: Dict):
    """Detect Rust project details."""
    cargo = path / 'Cargo.toml'
    if cargo.exists():
        context['type'] = 'rust'
        context['languages'].append('Rust')
        context['install_command'] = 'cargo install --path .'
        context['entry_command'] = 'cargo run'

        try:
            import tomllib
            with open(cargo, 'rb') as f:
                data = tomllib.load(f)
            package = data.get('package', {})
            context['description'] = package.get('description', '')
            context['name'] = package.get('name', context['name'])
        except Exception:
            pass
