# Jev Computer Use

A computer-use engine and installable Codex skill built around [Browser Use's Jev Ultrafast](https://github.com/browser-use/jev-ultrafast): **Jev selects actions and targets in one request; a small model only writes text when needed.** No per-click planner runs by default. Codex inspects the final page and screenshot to verify the result.

This is Donovan Murray's fork of [Aaron Levin's TypeSafe Computer Use](https://github.com/awlevin/typesafe-computer-use), retaining its MIT license and history. It adds adaptive browser planning, provider fallback, control handling repairs, completion verification, and a portable `$computer-use` skill. It does not train a new model.

**Historical planned-engine result:** 94/104 successes (90.4%) on an adapted MiniWoB++ subset, 5.7 seconds median, about $1.32 estimated inference for all 104 cases. This score belongs to `--engine planned`, not the new default fast engine. These are short browser tasks, not a general desktop success rate or a SOTA claim. See [fast-engine architecture and evaluation](docs/ultrafast.md) for current results. [Protocol, failures, costs and reproduction](docs/benchmark.md).

## Install the Codex skill

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/getting-started/installation/), Google Chrome or Chromium, a [TypeSafe](https://typesafe.ai/) API key, and at least one supported LLM API key. The fast text helper prefers OpenRouter Mercury 2.5, then direct OpenAI nano or Fireworks when no OpenRouter key is configured. The older planned engine retains provider fallback. macOS is the locally tested platform; Linux browser support is included. Native Windows code is inherited and has not been accepted in this fork.

```sh
git clone https://github.com/DunnyBunny1/typesafe-computer-use.git
cd typesafe-computer-use
uv sync --frozen
uv run --frozen python scripts/install_skill.py
```

Configure keys in the ignored checkout `.env`:

```sh
cp .env.example .env
chmod 600 .env
# Edit .env: set TYPESAFE_API_KEY and OPENROUTER_API_KEY (or OPENAI_API_KEY).
uv run --frozen computer-use doctor
```

Keep this checkout and its `.venv` in place: the skill points to that runtime. Installation defaults to `~/.codex/skills/computer-use`, honors `CODEX_HOME`, and accepts `--destination PATH`. Use `--replace` to update an existing skill; its previous files are backed up outside the active skills directory. Start a new Codex conversation if discovery is cached. No separate TypeSafe skill is needed.

### Try it

Ask Codex:

> Use $computer-use to find a round-trip flight from JFK to SFO, November 12–16, 2026, for one adult in economy. Apply nonstop only. Report one matching fare, airline, departure time and source link. Verify the dates and filter; do not book anything.

For a shorter task:

> Use $computer-use to open Python's official documentation, navigate to pathlib.Path.mkdir, and explain what parents=True and exist_ok=True do. Include the documentation URL.

Dates, fares and websites change; these are examples, not guaranteed outcomes. [Skill instructions](skills/computer-use/SKILL.md).

## Standalone CLI

```sh
uv tool install 'git+https://github.com/DunnyBunny1/typesafe-computer-use.git@v0.2.0.post2'
computer-use doctor
computer-use browser --url 'https://docs.python.org/3/library/pathlib.html'   --goal 'Find Path.mkdir and explain parents=True and exist_ok=True with the source URL.'
```

For a wheel/tool installation, put keys in `~/.config/jev-computer-use/.env`, export them, or set `COMPUTER_USE_ENV_FILE` to a private file. Process environment takes precedence, followed by that config file and checkout `.env`. Legacy `~/.env` contributes only `TYPESAFE_API_KEY`. Keys are not included in this repository.

The CLI prints a run folder containing `task.json`, `final-page.json`, `final.png` and per-step evidence (`ultrafast-trace.json` for the fast engine). Default limits are 60 actions and 180 seconds; an in-flight model request can exceed the time limit. Change them with `--steps` and `--seconds`. The optional planned engine also accepts `--rounds` (default 24). `--resume task.json` restores the goal and notes, not a lost browser login/session.

### Packaging

- Python package / CLI: `typesafe_computer_use`, `computer-use`.
- Portable skill: `skills/computer-use/`, installed by `scripts/install_skill.py`.
- Optional Codex plugin manifest: `.codex-plugin/plugin.json`, exposing the same skill. Plugin installation alone does **not** install the Python engine: install the standalone CLI first and put it on the host's PATH. This repository is not listed in a curated marketplace. Avoid installing both copies of the skill.
- Tagged source and wheel: [releases](https://github.com/DunnyBunny1/typesafe-computer-use/releases). The inherited PyPI package is not this fork; install from this GitHub URL or its release assets.

## How it works

```text
User goal + visible DOM → Jev action and compatible target → browser input
                               ↓ only for TYPE_TEXT
                         small text model
```

The default `--engine ultrafast` vendors Browser Use's MIT-licensed loop at a pinned commit. It reads the DOM atomically, keeps observed node identities, checks stale/covered targets and executes browser input. Model output cannot become arbitrary selectors or JavaScript. Screenshots are saved at the end for host verification; no screenshot planner runs per click. `done_unverified` is a completion claim that still requires checking final evidence.

The original architecture remains available with `--engine planned`, including visual planning, nested scrolling, dragging, sliders and bounded recovery. It can be much slower. The fast engine does not automatically fall back to it. [Source attribution, adaptations and measured tradeoffs](docs/ultrafast.md).

## Boundaries

Browser mode uses isolated headless Chrome by default. For login, use `--headed --profile /path/to/dedicated-profile` and sign in yourself. Do not point it at your everyday browser profile. `--attach-port` is for an explicitly selected, dedicated single-tab CDP browser.

Native Mac control is available through `computer-use desktop --app TextEdit --goal 'Read the front document.'`. The named app must already be foreground, and the host needs macOS Accessibility and Screen Recording permissions. It moves the real mouse and keyboard. TextEdit has smoke coverage; no OSWorld desktop score is established. The original `clicker` command remains available; see the upstream documentation for its workflow.

The fast engine does not support nested scrolling, sliders or dragging; the planned engine covers some of these. Small visual references, iframe/shadow-root traversal, automatic tab switching and arbitrary canvas dragging remain weak or unsupported. CAPTCHA and missing login require user help. Verify consequential results: a model saying “done” is not ground truth. The agent does not provide a complete prompt-injection security boundary.

Page text goes to Jev and, for typing, the configured text provider. Use `TEXT_MODEL_API_KEY`, `TEXT_MODEL_BASE_URL`, `TEXT_MODEL` and `TEXT_MODEL_REASONING` for explicit fast-engine configuration. The planned engine may send screenshots; its provider lists are `CLICKER_PLANNER_PROVIDERS` and `CLICKER_WRITER_PROVIDERS`. Run artifacts remain on disk and may contain private page content. Do not publish your `.env`, profiles or run folders.

## Develop and evaluate

```sh
uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv build
```

Offline tests refuse real desktop input, browser connections and external network access. Live evaluations run separately. See [benchmark reproduction](docs/benchmark.md), [writer configuration](docs/writer-endpoints.md), [browser backend](docs/browser-backend.md), and [upstream OSWorld integration](docs/osworld.md). OSWorld integration is included but was not run for this release.

## Attribution

Fast browser loop by [Browser Use](https://github.com/browser-use/jev-ultrafast), MIT notice in `typesafe_computer_use/_vendor/jev_ultrafast/LICENSE`. Original engine by [Aaron Levin](https://github.com/awlevin), powered by [TypeSafe/Jev](https://typesafe.ai/). MiniWoB++ is maintained by the [Farama Foundation](https://github.com/Farama-Foundation/miniwob-plusplus). Benchmark pages are downloaded separately; this fork publishes manifests and results. [MIT license](LICENSE).
