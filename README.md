# CliHub

**The App Store for AI Agents** — discover, install, and create CLI tools with `--help` as the universal protocol.

[clihub.net](https://clihub.net) | [Landing Page Repo](https://github.com/clihub-ai/clihub-landing-page)

## Install

```bash
pip install clihub
```

## Quick Start

```bash
# Search for tools
$ clihub search "json processing"

# Install a tool
$ clihub install jq

# Get tool info (+ --help preview if installed)
$ clihub info jq

# Browse categories
$ clihub list

# Check system readiness
$ clihub doctor
```

## Agent-Friendly

Every command supports `--json` for structured output:

```bash
$ clihub --json search "resize images"
$ clihub --json info jq
```

## What is CliHub?

CliHub is a CLI tool marketplace designed for AI agents. Every CLI tool is a superpower your agent can wield — no JSON schemas, no MCP servers, just `--help`.

- **Search** — Fuzzy search over a curated registry of 35+ tools
- **Install** — One command, auto-detects pip/npm/brew/cargo
- **Info** — View manifest + live `--help` preview
- **List** — Browse by category, see what's installed
- **Doctor** — Check which package managers are available

## Coming Soon

- `clihub publish` — share your tools with the community
- `clihub create` — AI-generated CLI tools from natural language
- Web marketplace at [clihub.net](https://clihub.net)
- 500+ indexed tools

## Contributing

1. Fork this repo
2. Create your feature branch (`git checkout -b feature/awesome`)
3. Commit your changes
4. Push and open a Pull Request

## License

MIT
