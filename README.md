<p align="center">
  <br>
  <a href="https://clihub.net">
    <img src="assets/readme-banner-transparent.png" alt="clihub" width="400">
  </a>
  <br>
  <br>
  <strong>Discover, install, and manage 100+ CLI tools. Built for AI agents.</strong>
  <br>
  <sub>App Store is for humans. CliHub is for agents.</sub>
  <br>
  <br>
  <a href="https://clihub.net"><img alt="Website" src="https://img.shields.io/badge/🌐_clihub.net-visit-00ff88?style=for-the-badge&labelColor=1a1a2e"></a>
  <br>
  <br>
  <a href="https://pypi.org/project/clihub-ai"><img alt="PyPI" src="https://img.shields.io/pypi/v/clihub-ai?style=flat-square&color=00ff88&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square&labelColor=1a1a2e"></a>
  <a href="https://github.com/clihub-ai/clihub/actions"><img alt="Tests" src="https://img.shields.io/github/actions/workflow/status/clihub-ai/clihub/ci.yml?style=flat-square&labelColor=1a1a2e&label=tests"></a>
  <br>
  <br>
  <a href="#-the-insight">The Insight</a> &middot;
  <a href="#-get-started">Get Started</a> &middot;
  <a href="#-agent-integration">Agent Integration</a> &middot;
  <a href="#-tool-catalog">Tool Catalog</a> &middot;
  <a href="#-add-your-tool">Add Your Tool</a>
</p>

```python
# pip install clihub-ai

import subprocess, json

# Step 1: Agent reads the full tool catalog (104 tools, ~87KB)
catalog = json.loads(subprocess.run(["clihub", "list", "--json"], capture_output=True, text=True).stdout)

# Step 2: Agent picks the right tool and installs it
subprocess.run(["clihub", "install", "jq"])

# Step 3: Agent uses it — zero tokens wasted on schemas
result = subprocess.run(["jq", ".users[] | .name", "data.json"], capture_output=True, text=True)
```

---

## 💡 The Insight

App stores were built for humans. **Buttons, screenshots, star ratings** — everything optimized for eyes and thumbs. That made sense when the user was a person browsing on a screen.

But the user is changing. AI agents are becoming the primary way software gets discovered, installed, and orchestrated. And agents don't browse — they **query**. They don't click — they **pipe**. They don't read screenshots — they read **structured metadata**.

**The App Store needed a new interface.** Not a GUI — a CLI. Not for humans — for agents.

That's [CliHub](https://clihub.net). The App Store redesigned from the ground up for a world where the user is an LLM.

|  | 🖥️ Traditional App Store | 🤖 CliHub |
|---|---|---|
| 👤 **Built for** | Humans browsing a GUI | AI agents calling a CLI |
| 🔍 **Discovery** | Screenshots, ratings, reviews | `clihub list --json` — structured metadata |
| 📦 **Install** | Click a button | `clihub install jq` — one command |
| 🧠 **Intelligence** | Store ranks and recommends | Agent reads catalog and decides |
| 💸 **Context cost** | N/A | **0 tokens** until `--help` |
| 🔗 **Composability** | Apps are siloed | Unix pipes: `curl \| jq \| grep` |
| 🌍 **Ecosystem** | Walled garden | Open — thousands of CLI tools, built over 50 years |

> 💡 LLMs are already trained on `jq`, `ffmpeg`, `curl`, and `grep`. They don't need a new schema — they need a way to **find** and **install** the right tool. That's all CliHub does.

<br>

## ⚡ Get Started

```bash
pip install clihub-ai
```

**For humans** — search, install, use:

```bash
clihub search "resize images"      # 🔍 fuzzy search across 104 tools
clihub install imagemagick          # 📦 auto-detects brew/pip/npm/cargo
clihub info jq                      # 📖 metadata, examples, and --help output
clihub list                         # 📋 browse all categories
clihub doctor                       # 🩺 check available package managers
```

**For agents** — add `--json` to any command:

```bash
clihub list --json                  # full catalog with descriptions + agent_hints
clihub install jq --json            # {"status": "success", "message": "Installed jq@1.7.1 via brew"}
clihub info ruff --json             # full metadata, install method, example commands
```

> ✅ Every response is valid JSON &nbsp; ✅ Errors go to stderr &nbsp; ✅ Exit codes: `0` success, `1` error, `2` not found

<br>

## 🧩 Agent Integration

The design is simple: **CliHub is a dumb pipe. The agent is the brain.**

An agent doesn't need a search algorithm — it *is* one. CliHub gives it a structured catalog. The agent reads it, picks the right tool, and installs it:

```bash
# 📥 Step 1: Read the catalog (87KB — fits in any context window)
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

# 📦 Step 2: Install what it needs
$ clihub install jq --json
{"status": "success", "message": "Installed jq@1.7.1 via brew"}

# 🚀 Step 3: Use it
$ jq '.users[] | .name' data.json
```

That's the entire integration. Two calls. Done.

### 🔗 Composable with anything

```bash
# Find all installed Python tools
clihub list --installed --json | jq '[.[] | select(.categories[] == "python")]'

# Get example commands for a tool
clihub info ffmpeg --json | jq '.agent_hints.example_usage'

# Check which package managers are missing
clihub doctor --json | jq '[.[] | select(.ok == false) | .check]'
```

### 📚 All Commands

| Command | What it Does |
|---|---|
| `clihub list [--json]` | 📋 Browse the full tool catalog (104 tools with metadata) |
| `clihub search <query> [--json]` | 🔍 Fuzzy-search tools by keyword |
| `clihub install <tool> [--json]` | 📦 Install via auto-detected package manager |
| `clihub info <tool> [--json]` | 📖 Show metadata, agent hints, and `--help` output |
| `clihub doctor [--json]` | 🩺 Check system readiness and available package managers |
| `clihub convert <tool> [--json]` | ⚙️ Auto-generate a manifest from an installed tool |
| `clihub submit <file> [--json]` | ✅ Validate a manifest for registry submission |

<br>

## 📦 Tool Catalog

**104 tools** across 17 categories — every one has `agent_hints` with natural-language descriptions and example commands.

| Category | Tools | Use Case |
|---|---|---|
| 📊 **Data** | jq, yq, csvkit, xsv, dasel, gron, fx, jless | Parse JSON, transform YAML, query CSV |
| 🗄️ **Database** | mycli, pgcli, litecli, iredis, usql | MySQL, Postgres, Redis, SQLite clients |
| 🔍 **Search & Files** | ripgrep, fd, fzf, bat, eza, lsd, broot, ranger, nnn | Find files, search code, browse directories |
| 🌐 **Network** | httpie, curl, wget, aria2, ngrok, mosh, nmap | HTTP requests, downloads, tunneling, scanning |
| 🐍 **Python** | ruff, black, mypy, uv, pipx, poetry | Lint, format, type-check, manage packages |
| 💛 **JavaScript** | prettier, eslint, tsx, npm-check-updates | Format, lint, run TypeScript, update deps |
| 🛠️ **Dev Tools** | gh, lazygit, gitui, tokei, hyperfine, just, grex, shellcheck | Git workflows, benchmarks, task running |
| 🐳 **Docker & Cloud** | lazydocker, k9s, dive, act, awscli, terraform | Containers, Kubernetes, CI, infrastructure |
| 🎬 **Media** | ffmpeg, imagemagick, yt-dlp, svgo, gifsicle, asciinema | Video, images, downloads, GIFs, recordings |
| 📄 **Documents** | pandoc, glow | Convert Markdown/HTML/PDF, render in terminal |
| ✂️ **Text** | sd, choose, sad | Find-and-replace, cut columns, batch edits |
| ✏️ **Editors** | neovim, micro, helix | Terminal-based text editing |
| ⏱️ **Productivity** | tmux, tldr, zoxide, starship, taskwarrior, watson, nb | Sessions, navigation, tasks, time tracking |
| 🚀 **Release** | semantic-release, release-it, commitizen, cookiecutter | Versioning, changelogs, project scaffolding |
| 🔒 **Security** | openssl, age, mkcert | TLS, encryption, local certificates |
| 💻 **System** | htop, btop, procs, bandwhich, pv, ncdu, dust | Processes, bandwidth, disk usage, pipelines |
| 🎉 **Fun** | lolcat, fortune, cmatrix | Rainbow text, quotes, Matrix rain |

<br>

## ➕ Add Your Tool

Got a CLI tool? Add it to CliHub in 30 seconds:

```bash
clihub convert mytool           # ⚙️ auto-detects version, description, license, homepage
vim clihub.yaml                 # ✏️ fill in categories, tags, agent_hints
clihub submit clihub.yaml       # ✅ validates and prints PR-ready JSON
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

Then [open a PR](https://github.com/clihub-ai/clihub). 🎉

<br>

## 🧑‍💻 Development

```bash
git clone https://github.com/clihub-ai/clihub.git
cd clihub
pip install -e ".[dev]"
pytest                      # unit tests
ruff check src/ tests/      # lint
```

## 🤝 Contributing

The easiest way to contribute: `clihub convert <tool>`, fill in the TODOs, [open a PR](https://github.com/clihub-ai/clihub/issues).

## 📄 License

MIT &copy; [CliHub](https://clihub.net)

---

## ⭐ Star History

If CliHub helps your agent get things done, give it a star — it helps others find it too.

<p align="center">
  <a href="https://star-history.com/#clihub-ai/clihub&Date">
    <img src="https://api.star-history.com/svg?repos=clihub-ai/clihub&type=Date" alt="Star History Chart" width="700">
  </a>
</p>

---

<p align="center">
  <a href="https://clihub.net"><strong>clihub.net</strong></a> &middot;
  <a href="https://pypi.org/project/clihub-ai">PyPI</a> &middot;
  <a href="https://github.com/clihub-ai/clihub/issues">Issues</a>
</p>
