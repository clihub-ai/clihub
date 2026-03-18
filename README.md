<p align="center">
  <br>
  <a href="https://clihub.net">
    <img src="assets/readme-banner-transparent.svg" alt="clihub" width="500">
  </a>
  <br>
  <br>
  <strong>Discover, install, and manage 100+ CLI tools. Built for AI agents.</strong>
  <br>
  <br>
  <a href="https://pypi.org/project/clihub-ai"><img alt="PyPI" src="https://img.shields.io/pypi/v/clihub-ai?style=flat-square&color=00ff88&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/actions"><img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/clihub-ai/clihub/ci.yml?style=flat-square&labelColor=1a1a2e&label=tests"></a>
</p>

```bash
pip install clihub-ai

clihub search "convert pdf"       # find the right tool
clihub install pandoc              # install it (auto-detects brew/pip/npm/cargo)
pandoc README.md -o README.pdf     # use it
```

---

<p align="center">
  <a href="#why">Why</a> &middot;
  <a href="#how-it-works">How It Works</a> &middot;
  <a href="#for-ai-agents">For AI Agents</a> &middot;
  <a href="#whats-included">What's Included</a> &middot;
  <a href="#add-your-tool">Add Your Tool</a>
</p>

## Why

Your AI agent needs to resize an image. It knows *how* — it's seen millions of shell examples in training. But it doesn't know what's installed on this machine, or what tool to use.

**CliHub is the missing piece.** A curated registry of 104 CLI tools with structured metadata — descriptions, install methods, and agent-readable hints. Your agent queries the registry, picks the right tool, installs it, and runs it. Two commands. Zero configuration.

**Why CLI tools instead of MCP?** Because MCP servers inject thousands of tokens into every prompt — even when unused. CLI tools cost **zero tokens** until the agent actually runs one. And LLMs are already trained on `jq`, `ffmpeg`, `curl`, and `grep` — they don't need a schema to use them.

|  | MCP Server | CLI via CliHub |
|---|---|---|
| **Idle cost** | 8,000+ tokens per prompt | **0 tokens** |
| **Discovery** | Schemas dumped into every prompt | On demand via `clihub list --json` |
| **LLM familiarity** | Must learn custom schemas | Already trained on shell commands |
| **Composability** | One tool per call | Unix pipes: `curl \| jq \| grep` |
| **Ecosystem** | Hundreds of servers | **Thousands of tools**, built over 50 years |

<br>

## How It Works

**For humans** — search, install, use:

```bash
clihub search "resize images"      # fuzzy search across 104 tools
clihub install imagemagick          # auto-detects the right package manager
clihub info jq                      # view metadata, examples, and --help output
clihub list                         # browse all categories
clihub doctor                       # check which package managers are available
```

**For agents** — add `--json` to any command:

```bash
clihub list --json                  # full catalog: 104 tools with descriptions + agent_hints
clihub install jq --json            # → {"status": "success", "message": "Installed jq@1.7.1 via brew"}
clihub info ruff --json             # → full metadata, install method, example commands
```

Every response is valid JSON. Every error goes to stderr. Exit codes: `0` success, `1` error, `2` not found.

<br>

## For AI Agents

The design is simple: **CliHub is a dumb pipe. The agent is the brain.**

An agent doesn't need a search algorithm — it *is* one. CliHub gives it a structured catalog. The agent reads it, picks the right tool, and installs it. Two API calls:

```bash
# Step 1: Read the catalog (87KB — fits in any context window)
$ clihub list --json
[
  {
    "name": "jq",
    "description": "Lightweight command-line JSON processor.",
    "categories": ["data", "json"],
    "agent_hints": {
      "when_to_use": "Parse, filter, or transform JSON data",
      "example_usage": ["jq '.users[] | select(.age > 30)' data.json"]
    },
    "install": {"method": "brew", "package": "jq"}
  },
  ... 103 more tools
]

# Step 2: Install what it needs
$ clihub install jq --json
{"status": "success", "message": "Installed jq@1.7.1 via brew"}

# Done. Agent runs the tool.
$ jq '.users[] | .name' data.json
```

### Composable

```bash
clihub list --installed --json | jq '[.[] | select(.categories[] == "python")]'
clihub info ffmpeg --json | jq '.agent_hints.example_usage'
clihub doctor --json | jq '[.[] | select(.ok == false) | .check]'
```

### All Commands

| Command | What it Does |
|---|---|
| `clihub list [--json]` | Browse the full tool catalog (104 tools with metadata) |
| `clihub search <query> [--json]` | Fuzzy-search tools by keyword |
| `clihub install <tool> [--json]` | Install via auto-detected package manager |
| `clihub info <tool> [--json]` | Show metadata, agent hints, and `--help` output |
| `clihub doctor [--json]` | Check system readiness and available package managers |
| `clihub convert <tool> [--json]` | Auto-generate a manifest from an installed tool |
| `clihub submit <file> [--json]` | Validate a manifest for registry submission |

<br>

## What's Included

**104 tools** across 17 categories — every one has `agent_hints` with natural-language descriptions and example commands.

| Category | Tools | Use Case |
|---|---|---|
| **Data** | jq, yq, csvkit, xsv, dasel, gron, fx, jless | Parse JSON, transform YAML, query CSV |
| **Database** | mycli, pgcli, litecli, iredis, usql | MySQL, Postgres, Redis, SQLite clients |
| **Search & Files** | ripgrep, fd, fzf, bat, eza, lsd, broot, ranger, nnn | Find files, search code, browse directories |
| **Network** | httpie, curl, wget, aria2, ngrok, mosh, nmap | HTTP requests, downloads, tunneling, scanning |
| **Python** | ruff, black, mypy, uv, pipx, poetry | Lint, format, type-check, manage packages |
| **JavaScript** | prettier, eslint, tsx, npm-check-updates | Format, lint, run TypeScript, update deps |
| **Dev Tools** | gh, lazygit, gitui, tokei, hyperfine, just, grex, shellcheck | Git workflows, benchmarks, task running |
| **Docker & Cloud** | lazydocker, k9s, dive, act, awscli, terraform | Containers, Kubernetes, CI, infrastructure |
| **Media** | ffmpeg, imagemagick, yt-dlp, svgo, gifsicle, asciinema | Video, images, downloads, GIFs, recordings |
| **Documents** | pandoc, glow | Convert Markdown/HTML/PDF, render in terminal |
| **Text** | sd, choose, sad | Find-and-replace, cut columns, batch edits |
| **Editors** | neovim, micro, helix | Terminal-based text editing |
| **Productivity** | tmux, tldr, zoxide, starship, taskwarrior, watson, nb | Sessions, navigation, tasks, time tracking |
| **Release** | semantic-release, release-it, commitizen, cookiecutter | Versioning, changelogs, project scaffolding |
| **Security** | openssl, age, mkcert | TLS, encryption, local certificates |
| **System** | htop, btop, procs, bandwhich, pv, ncdu, dust | Processes, bandwidth, disk usage, pipelines |
| **Fun** | lolcat, fortune, cmatrix | Rainbow text, quotes, Matrix rain |

<br>

## Add Your Tool

```bash
clihub convert mytool           # auto-detects version, description, license, homepage
vim clihub.yaml                 # fill in categories, tags, agent_hints
clihub submit clihub.yaml       # validates and prints PR-ready JSON
```

`convert` pulls metadata from `--help`, `--version`, and package managers (brew, pip, npm, cargo). You fill in what makes your tool discoverable to agents — categories, tags, and `agent_hints.when_to_use`:

```yaml
name: mytool
version: "2.1.0"
description: "Do something useful from the terminal"
categories: [utilities]
install:
  method: brew
  package: mytool
agent_hints:
  when_to_use: "When you need to do something useful quickly"
  example_usage:
    - "mytool input.txt --output result.json"
```

Then [open a PR](https://github.com/clihub-ai/clihub).

<br>

## Development

```bash
git clone https://github.com/clihub-ai/clihub.git
cd clihub
pip install -e ".[dev]"
pytest                      # unit tests
ruff check src/ tests/      # lint
```

## Contributing

The easiest way to contribute: `clihub convert <tool>`, fill in the TODOs, [open a PR](https://github.com/clihub-ai/clihub/issues).

## License

MIT &copy; [CliHub](https://clihub.net)
