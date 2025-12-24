"""README generator - LLM-based generation with BYOM support."""

import os
from typing import Dict, Any
import httpx

# BYOM: Bring Your Own Model
PROVIDERS = {
    'anthropic': {
        'url': 'https://api.anthropic.com/v1/messages',
        'key_env': 'ANTHROPIC_API_KEY',
        'default_model': 'claude-sonnet-4-20250514',
    },
    'openai': {
        'url': 'https://api.openai.com/v1/chat/completions',
        'key_env': 'OPENAI_API_KEY',
        'default_model': 'gpt-4o',
    },
    'google': {
        'url': 'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        'key_env': 'GOOGLE_API_KEY',
        'default_model': 'gemini-1.5-flash',
    },
    'ollama': {
        'url': 'http://localhost:11434/api/generate',
        'key_env': None,
        'default_model': 'llama3.2',
    },
}


def generate_readme(context: Dict[str, Any]) -> str:
    """Generate README using configured LLM provider.

    Env vars:
        LLM_PROVIDER: anthropic/openai/google/ollama (default: anthropic)
        LLM_MODEL: model name (uses provider default if not set)
    """
    provider = os.environ.get('LLM_PROVIDER', 'anthropic')
    model = os.environ.get('LLM_MODEL', PROVIDERS[provider]['default_model'])

    prompt = _build_prompt(context)

    if provider == 'anthropic':
        return _call_anthropic(prompt, model)
    elif provider == 'openai':
        return _call_openai(prompt, model)
    elif provider == 'google':
        return _call_google(prompt, model)
    elif provider == 'ollama':
        return _call_ollama(prompt, model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _build_prompt(context: Dict[str, Any]) -> str:
    """Build prompt for README generation.

    Based on HN success patterns:
    - Title: [verb] [noun] in [metric]
    - First sentence: Problem statement
    - Quick Start: Exactly 3 steps
    - No wall of text
    """
    files_str = '\n'.join(f'  - {f}' for f in context.get('files', [])[:30])
    deps_str = ', '.join(context.get('dependencies', [])) or 'none detected'

    return f"""Generate a README.md for this project.

PROJECT INFO:
- Name: {context['name']}
- Type: {context['type']}
- Description: {context.get('description', 'No description')}
- Languages: {', '.join(context.get('languages', ['unknown']))}
- Install: {context.get('install_command', 'not detected')}
- Run: {context.get('entry_command', 'not detected')}
- Key dependencies: {deps_str}

FILES:
{files_str}

REQUIREMENTS (HN-optimized):
1. Title format: "# [project-name] - [verb] [noun] in [metric]" (e.g., "Generate README in 60s")
2. First paragraph: State the problem this solves (2-3 sentences max)
3. Quick Start: EXACTLY 3 steps with code blocks
4. Features: 3-5 bullet points, each one line
5. License: MIT
6. No walls of text. Be concise.

OUTPUT: Raw markdown only, no code fences around it."""


def _call_anthropic(prompt: str, model: str) -> str:
    """Call Anthropic API."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    resp = httpx.post(
        PROVIDERS['anthropic']['url'],
        headers={
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
        },
        json={
            'model': model,
            'max_tokens': 2000,
            'messages': [{'role': 'user', 'content': prompt}],
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()['content'][0]['text']


def _call_openai(prompt: str, model: str) -> str:
    """Call OpenAI API."""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    resp = httpx.post(
        PROVIDERS['openai']['url'],
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 2000,
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']


def _call_google(prompt: str, model: str) -> str:
    """Call Google Gemini API."""
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    url = PROVIDERS['google']['url'].format(model=model)
    resp = httpx.post(
        f"{url}?key={api_key}",
        json={
            'contents': [{'parts': [{'text': prompt}]}],
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()['candidates'][0]['content']['parts'][0]['text']


def _call_ollama(prompt: str, model: str) -> str:
    """Call local Ollama."""
    resp = httpx.post(
        PROVIDERS['ollama']['url'],
        json={
            'model': model,
            'prompt': prompt,
            'stream': False,
        },
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()['response']
