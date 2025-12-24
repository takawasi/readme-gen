# readme-gen

Generate HN-optimized README in 60 seconds.

Stop staring at blank README.md files. Let AI write it based on your actual code.

## Quick Start

```bash
# 1. Install
pip install readme-gen

# 2. Configure (BYOM - Bring Your Own Model)
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-...

# 3. Generate
readme-gen ./myproject -o README.md
```

## Features

- **BYOM**: Works with Claude, GPT-4, Gemini, or local Ollama
- **HN-optimized**: Follows patterns from successful Show HN posts
- **Fast**: Under 60 seconds
- **Zero config**: No config files needed

## Supported Providers

| Provider | Env Vars |
|----------|----------|
| Anthropic | `LLM_PROVIDER=anthropic` `ANTHROPIC_API_KEY=...` |
| OpenAI | `LLM_PROVIDER=openai` `OPENAI_API_KEY=...` |
| Google | `LLM_PROVIDER=google` `GOOGLE_API_KEY=...` |
| Ollama | `LLM_PROVIDER=ollama` (local, no key needed) |

## Usage

```bash
# Print to stdout
readme-gen ./myproject

# Write to file
readme-gen ./myproject -o README.md

# Preview context only (no LLM call)
readme-gen ./myproject --dry-run
```

## HN Success Patterns

Based on analysis of 100+ successful Show HN posts:

- **Title**: `[verb] [noun] in [metric]`
- **First sentence**: Problem statement
- **Quick Start**: Exactly 3 steps
- **No wall of text**

## More Tools

See all dev tools: https://takawasi-social.com/en/

## License

MIT
