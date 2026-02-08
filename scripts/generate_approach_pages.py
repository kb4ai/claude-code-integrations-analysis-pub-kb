#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0",
#     "jinja2>=3.0",
# ]
# ///
"""
Generate per-project detail pages and approaches index from YAML data.

Produces:
  - reports/generated/projects/{name}.md  -- per-project code quotes + GitHub permalinks
  - reports/generated/approaches.md       -- approaches index with educational examples

Usage:
    ./scripts/generate_approach_pages.py
    ./scripts/generate_approach_pages.py --output reports/generated/
"""

import argparse
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, BaseLoader
from rich.console import Console

console = Console()

REPO_ROOT = Path(__file__).parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "generated"

# ── Approach taxonomy (curated) ──────────────────────────────────────────────

APPROACHES: list[dict[str, Any]] = [
    # ── CLI Approaches ───────────────────────────────────────────────────────
    {
        "id": "persistent-subprocess",
        "category": "CLI",
        "title": "Persistent Subprocess (Bidirectional NDJSON)",
        "projects": ["goose"],
        "description": textwrap.dedent("""\
            Spawn Claude Code once as a long-running subprocess. Communicate via
            stdin/stdout using newline-delimited JSON (NDJSON). The process persists
            across many user messages, avoiding cold-start overhead."""),
        "example_lang": "bash",
        "example": textwrap.dedent("""\
            # Start Claude Code as a persistent subprocess with NDJSON I/O
            claude \\
              --input-format stream-json \\
              --output-format stream-json \\
              --verbose \\
              --system-prompt "You are a helpful coding assistant." &
            CLAUDE_PID=$!

            # Send a message via stdin (one JSON object per line)
            echo '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"Hello"}]}}' \\
              > /proc/$CLAUDE_PID/fd/0

            # Read NDJSON responses from stdout:
            #   {"type":"assistant","message":{"role":"assistant","content":[...]}}
            #   {"type":"result","cost":0.003,"duration_ms":1200,"session_id":"..."}"""),
    },
    {
        "id": "per-request-spawn-simple",
        "category": "CLI",
        "title": "Per-Request Spawn (Simple)",
        "projects": ["claude-code-mcp"],
        "description": textwrap.dedent("""\
            Spawn a fresh Claude Code process for each request. Pass the prompt
            with `-p`, collect raw text from stdout. Simplest possible integration."""),
        "example_lang": "bash",
        "example": textwrap.dedent("""\
            # One-shot: spawn, pass prompt, collect output
            result=$(claude --dangerously-skip-permissions -p "Explain this error: $ERROR_MSG")
            echo "$result"

            # With timeout and working directory
            timeout 1800 claude \\
              --dangerously-skip-permissions \\
              -p "Fix the failing test in tests/auth.py" \\
              2>/dev/null"""),
    },
    {
        "id": "per-request-spawn-structured",
        "category": "CLI",
        "title": "Per-Request Spawn (Structured Output)",
        "projects": ["cline"],
        "description": textwrap.dedent("""\
            Spawn per-request with `--output-format stream-json` for structured NDJSON
            events. Use `--max-turns 1` and `--disallowedTools` to make Claude Code act
            as a single-turn LLM while your app handles orchestration."""),
        "example_lang": "bash",
        "example": textwrap.dedent("""\
            # Structured single-turn: get NDJSON events back
            echo '[{"role":"user","content":"Refactor this function"}]' | \\
              claude \\
                --output-format stream-json \\
                --verbose \\
                --max-turns 1 \\
                --model claude-sonnet-4-5-20250929 \\
                --disallowedTools "Bash,Write,Edit" \\
                -p

            # Each line of stdout is a JSON event:
            #   {"type":"assistant","message":{"content":[{"type":"text","text":"..."}]}}
            #   {"type":"result","session_id":"...","cost":0.002}"""),
    },
    {
        "id": "multi-instance-orchestration",
        "category": "CLI",
        "title": "Multi-Instance Orchestration",
        "projects": ["claude-flow"],
        "description": textwrap.dedent("""\
            Spawn multiple Claude Code instances in parallel for multi-agent workflows.
            Tasks within a phase run concurrently; phases run sequentially.
            Stream-chain: pipe stdout of one agent as context to the next."""),
        "example_lang": "bash",
        "example": textwrap.dedent("""\
            # Agent 1: Research
            claude --print --output-format stream-json --verbose \\
              --dangerously-skip-permissions \\
              "Research the authentication options" > /tmp/agent1.ndjson &

            # Agent 2: Implementation (after agent 1 completes)
            wait
            CONTEXT=$(cat /tmp/agent1.ndjson | jq -r 'select(.type=="assistant") | .message.content[].text')
            claude --print --output-format stream-json --verbose \\
              --dangerously-skip-permissions \\
              "Previous research:\\n$CONTEXT\\n\\nNow implement the chosen approach" > /tmp/agent2.ndjson &

            # Agent 3: Testing (parallel with agent 2)
            claude --print --output-format stream-json --verbose \\
              --dangerously-skip-permissions \\
              "Write tests for the auth module" > /tmp/agent3.ndjson &
            wait"""),
    },
    {
        "id": "commands-and-skills",
        "category": "CLI",
        "title": "Commands & Skills (Declarative)",
        "projects": ["anthropic-cookbook", "fastmcp"],
        "description": textwrap.dedent("""\
            No subprocess management code. Use Claude Code's built-in extensibility:
            `.claude/commands/` for slash commands with YAML frontmatter,
            `.claude/skills/` for reusable expertise, `claude mcp add` for MCP servers."""),
        "example_lang": "markdown",
        "example": textwrap.dedent("""\
            <!-- .claude/commands/review-pr.md -->
            ---
            allowed-tools: Bash(gh pr diff:*),Bash(gh pr comment:*),Read,Glob,Grep
            description: Review a pull request
            ---
            Review PR #$ARGUMENTS using best practices.
            Check for security issues, test coverage, and code quality.

            <!-- .claude/skills/python-testing/SKILL.md -->
            ---
            description: Expert at writing Python tests with pytest
            ---
            When writing tests, always use pytest fixtures and parametrize.

            # Register an MCP server with Claude Code
            claude mcp add my-server -e API_KEY=sk-123 -- npx my-mcp-server"""),
    },
    # ── SDK Approaches ───────────────────────────────────────────────────────
    {
        "id": "claude-agent-sdk",
        "category": "SDK",
        "title": "Claude Agent SDK",
        "projects": ["claude-code-action", "anthropic-cookbook"],
        "description": textwrap.dedent("""\
            Higher-level SDK that wraps Claude Code itself. The `query()` async iterator
            yields messages in real-time. Manages sessions, tools, and permissions.
            Works with your Claude subscription (no separate API key needed with some setups).
            This is the official programmatic interface to Claude Code."""),
        "example_lang": "typescript",
        "example": textwrap.dedent("""\
            // TypeScript
            import { query } from "@anthropic-ai/claude-agent-sdk";

            const messages = query({
              model: "claude-sonnet-4-5-20250929",
              prompt: "Add input validation to the signup form",
              maxTurns: 10,
              allowedTools: ["Read", "Write", "Edit", "Bash"],
              systemPrompt: "You are a senior engineer.",
            });

            for await (const msg of messages) {
              if (msg.type === "assistant") console.log(msg.message.content);
              if (msg.type === "result") console.log("Cost:", msg.cost_usd);
            }"""),
        "example2_lang": "python",
        "example2": textwrap.dedent("""\
            # Python
            from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

            options = ClaudeAgentOptions(
                model="claude-sonnet-4-5-20250929",
                allowed_tools=["Read", "Write", "Edit", "Bash"],
                permission_mode="acceptEdits",
            )
            async with ClaudeSDKClient(options=options) as agent:
                await agent.query(prompt="Add input validation to the signup form")
                async for msg in agent.receive_response():
                    print(msg)"""),
    },
    {
        "id": "direct-anthropic-sdk",
        "category": "SDK",
        "title": "Direct Anthropic SDK",
        "projects": ["gptme", "cline", "continue", "fastmcp"],
        "description": textwrap.dedent("""\
            Use the official Anthropic client library directly. Call
            `client.messages.create()` or `client.messages.stream()` for full control
            over API parameters, streaming, prompt caching, and extended thinking."""),
        "example_lang": "python",
        "example": textwrap.dedent("""\
            from anthropic import Anthropic

            client = Anthropic()  # uses ANTHROPIC_API_KEY env var

            with client.messages.stream(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=[{
                    "type": "text",
                    "text": "You are a code reviewer.",
                    "cache_control": {"type": "ephemeral"},  # prompt caching
                }],
                messages=[{"role": "user", "content": "Review this diff: ..."}],
                thinking={"type": "enabled", "budget_tokens": 10000},  # extended thinking
            ) as stream:
                for event in stream:
                    if hasattr(event, "text"):
                        print(event.text, end="")"""),
        "example2_lang": "typescript",
        "example2": textwrap.dedent("""\
            // TypeScript
            import Anthropic from "@anthropic-ai/sdk";

            const client = new Anthropic();
            const stream = await client.messages.create({
              model: "claude-sonnet-4-5-20250929",
              max_tokens: 4096,
              system: [{ type: "text", text: "You are a code reviewer.",
                         cache_control: { type: "ephemeral" } }],
              messages: [{ role: "user", content: "Review this diff: ..." }],
              thinking: { type: "enabled", budget_tokens: 10000 },
              stream: true,
            });
            for await (const chunk of stream) {
              if (chunk.type === "content_block_delta") process.stdout.write(chunk.delta.text ?? "");
            }"""),
    },
    {
        "id": "litellm-abstraction",
        "category": "SDK",
        "title": "LiteLLM Abstraction",
        "projects": ["aider", "openhands", "alphacodium"],
        "description": textwrap.dedent("""\
            Multi-provider abstraction via LiteLLM. Claude is one of many supported
            models. Prefix determines routing: `anthropic/claude-sonnet-4-20250514`.
            Anthropic-specific features (caching, thinking) passed via extra parameters."""),
        "example_lang": "python",
        "example": textwrap.dedent("""\
            import litellm

            # LiteLLM routes to Anthropic based on model prefix
            response = litellm.completion(
                model="anthropic/claude-sonnet-4-20250514",
                messages=[
                    {"role": "system", "content": "You are a coding assistant."},
                    {"role": "user", "content": "Explain this error: ..."},
                ],
                stream=True,
                # Anthropic-specific: prompt caching header
                extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
                # Anthropic-specific: extended thinking
                thinking={"type": "enabled", "budget_tokens": 10000},
            )
            for chunk in response:
                print(chunk.choices[0].delta.content or "", end="")"""),
    },
    # ── Cross-Cutting Patterns ───────────────────────────────────────────────
    {
        "id": "prompt-caching",
        "category": "Cross-Cutting",
        "title": "Prompt Caching",
        "projects": ["gptme", "cline", "aider", "continue", "openhands"],
        "description": textwrap.dedent("""\
            Reduce cost and latency by caching parts of the prompt across requests.
            Add `cache_control: {type: "ephemeral"}` to message content blocks.
            Place breakpoints on stable content (system prompt, tool definitions)
            for highest cache hit rates."""),
        "example_lang": "python",
        "example": textwrap.dedent("""\
            # Prompt caching: mark stable content with cache_control
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=[{
                    "type": "text",
                    "text": LARGE_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},     # breakpoint 1: system
                }],
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": repo_context,
                         "cache_control": {"type": "ephemeral"}},  # breakpoint 2: context
                    ]},
                    {"role": "user", "content": user_question},     # changes each turn
                ],
            )
            # Check cache effectiveness in response.usage:
            #   cache_creation_input_tokens, cache_read_input_tokens"""),
    },
    {
        "id": "extended-thinking",
        "category": "Cross-Cutting",
        "title": "Extended Thinking",
        "projects": ["gptme", "cline", "aider", "continue", "anthropic-cookbook"],
        "description": textwrap.dedent("""\
            Let Claude reason step-by-step before answering. Set a token budget for
            the thinking phase. Temperature MUST be 1 (or omitted) when thinking is enabled.
            Thinking content appears as separate blocks in the response."""),
        "example_lang": "python",
        "example": textwrap.dedent("""\
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8192,
                temperature=1,  # REQUIRED when thinking is enabled
                thinking={"type": "enabled", "budget_tokens": 10000},
                messages=[{"role": "user", "content": "Find the bug in this code: ..."}],
            )

            for block in response.content:
                if block.type == "thinking":
                    print(f"[Reasoning] {block.thinking}")
                elif block.type == "text":
                    print(f"[Answer] {block.text}")"""),
    },
]


# ── YAML loading ─────────────────────────────────────────────────────────────

def load_yaml(path: Path) -> dict[str, Any] | None:
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (yaml.YAMLError, FileNotFoundError):
        return None


def load_all_projects() -> list[dict[str, Any]]:
    projects = []
    for d in sorted(PROJECTS_DIR.iterdir()):
        if not d.is_dir() or d.name == "_template":
            continue
        projects.append({
            "name": d.name,
            "metadata": load_yaml(d / "metadata.project.yaml"),
            "cli": load_yaml(d / "cli.cli-integration.yaml"),
            "sdk": load_yaml(d / "sdk.sdk-integration.yaml"),
        })
    return projects


# ── GitHub permalink builder ─────────────────────────────────────────────────

def github_permalink(ref: dict[str, Any]) -> str:
    """Build a GitHub permalink from a reference dict."""
    repo = ref.get("repository", "")
    commit = ref.get("commit", "")
    path = ref.get("path", "")
    lines = ref.get("lines", [])

    if not repo or not commit or not path:
        return ""

    url = f"{repo}/blob/{commit}/{path}"
    if lines and len(lines) >= 2:
        url += f"#L{lines[0]}-L{lines[1]}"
    elif lines and len(lines) == 1:
        url += f"#L{lines[0]}"
    return url


def short_path_link(ref: dict[str, Any]) -> str:
    """Build markdown link with short path as text."""
    url = github_permalink(ref)
    path = ref.get("path", "")
    lines = ref.get("lines", [])
    if not url:
        return f"`{path}`"

    label = f"`{path}"
    if lines and len(lines) >= 2:
        label += f"` L{lines[0]}-L{lines[1]}"
    elif lines and len(lines) == 1:
        label += f"` L{lines[0]}"
    else:
        label += "`"
    return f"[{label}]({url})"


# ── Per-project page generation ──────────────────────────────────────────────

PROJECT_TEMPLATE = """\
# {{ display_name }}

| Field | Value |
|-------|-------|
| Repository | [{{ repository }}]({{ repository }}) |
| Analyzed commit | `{{ commit_short }}` ([full]({{ repository }}/tree/{{ commit }})) |
| Language | {{ language }} |
| Integration types | {{ integration_types }} |
| Status | {{ status }} |

{% if notes %}
{{ notes }}
{% endif %}

---

{% if cli_detected %}
## CLI Integration

{{ cli_summary }}

{% for inv in invocations %}
### {{ inv.id }}

{{ inv.description }}

{% if inv.permalink %}
**Source:** [{{ inv.ref_label }}]({{ inv.permalink }})
{% if inv.function %}  \u2022 Function: `{{ inv.function }}`{% endif %}
{% if inv.cls %}  \u2022 Class: `{{ inv.cls }}`{% endif %}
{% endif %}

{% if inv.flags %}
**Flags:**

| Flag | Purpose |
|------|---------|
{% for f in inv.flags %}| `{{ f.flag }}` | {{ f.purpose }} |
{% endfor %}
{% endif %}

{% if inv.snippet %}
```{{ inv.language }}
{{ inv.snippet }}```
{% endif %}

{% if inv.env_vars %}
**Environment variables:**

| Variable | Purpose |
|----------|---------|
{% for e in inv.env_vars %}| `{{ e.name }}` | {{ e.purpose }} |
{% endfor %}
{% endif %}

{% if inv.notes %}
> {{ inv.notes }}
{% endif %}

{% endfor %}
{% endif %}

{% if sdk_detected %}
## SDK Integration

{{ sdk_summary }}

**SDK(s) used:**

{% for s in sdks_used %}
* `{{ s.package }}` {{ s.version }}
{% endfor %}

{% for usage in sdk_usages %}
### {{ usage.id }}

{{ usage.description }}

{% if usage.permalink %}
**Source:** [{{ usage.ref_label }}]({{ usage.permalink }})
{% if usage.function %}  \u2022 Function: `{{ usage.function }}`{% endif %}
{% if usage.cls %}  \u2022 Class: `{{ usage.cls }}`{% endif %}
{% endif %}

{% if usage.snippet %}
```{{ usage.language }}
{{ usage.snippet }}```
{% endif %}

{% if usage.notes %}
> {{ usage.notes }}
{% endif %}

{% endfor %}
{% endif %}

---
*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*
"""


def render_project_page(project: dict[str, Any]) -> str:
    meta = project["metadata"] or {}
    cli = project["cli"] or {}
    sdk = project["sdk"] or {}

    commit = meta.get("analyzed_commit", "")
    repository = meta.get("repository", "")

    # ── CLI invocations ──────────────────────────────────────────────────
    invocations = []
    for inv in cli.get("invocations", []):
        ref = inv.get("reference", {})
        plink = github_permalink(ref)
        invocations.append({
            "id": inv.get("id", "unknown"),
            "description": inv.get("description", ""),
            "permalink": plink,
            "ref_label": f'`{ref.get("path", "")}` L{ref.get("lines", [0, 0])[0]}-L{ref.get("lines", [0, 0])[-1]}' if ref.get("path") else "",
            "function": ref.get("function"),
            "cls": ref.get("class"),
            "language": ref.get("language", ""),
            "flags": inv.get("flags_used", []),
            "snippet": (inv.get("snippet") or "").rstrip(),
            "env_vars": inv.get("environment_variables", []),
            "notes": (inv.get("notes") or "").strip().replace("\n", " "),
        })

    # ── SDK usages ───────────────────────────────────────────────────────
    sdk_usages = []
    for usage in sdk.get("sdk_usage", []):
        ref = usage.get("reference", {})
        plink = github_permalink(ref)
        sdk_usages.append({
            "id": usage.get("id", "unknown"),
            "description": usage.get("description", ""),
            "permalink": plink,
            "ref_label": f'`{ref.get("path", "")}` L{ref.get("lines", [0, 0])[0]}-L{ref.get("lines", [0, 0])[-1]}' if ref.get("path") else "",
            "function": ref.get("function"),
            "cls": ref.get("class"),
            "language": ref.get("language", "python"),
            "snippet": (usage.get("snippet") or "").rstrip(),
            "notes": (usage.get("notes") or "").strip().replace("\n", " "),
        })

    sdks_used = []
    for s in sdk.get("sdks_used", []):
        sdks_used.append({
            "package": s.get("package", ""),
            "version": s.get("version_constraint", ""),
        })

    env = Environment(loader=BaseLoader(), keep_trailing_newline=True)
    env.globals["True"] = True
    env.globals["False"] = False
    template = env.from_string(PROJECT_TEMPLATE)

    return template.render(
        display_name=meta.get("display_name", project["name"]),
        repository=repository,
        commit=commit,
        commit_short=commit[:12] if commit else "-",
        language=meta.get("primary_language", "-"),
        integration_types=", ".join(meta.get("integration_types", [])),
        status=meta.get("analysis_status", "pending"),
        notes=(meta.get("notes") or "").strip(),
        cli_detected=cli.get("cli_integration_detected", False),
        cli_summary=(cli.get("summary") or "").strip(),
        invocations=invocations,
        sdk_detected=sdk.get("sdk_integration_detected", False),
        sdk_summary=(sdk.get("summary") or "").strip(),
        sdks_used=sdks_used,
        sdk_usages=sdk_usages,
    )


# ── Approaches index page generation ─────────────────────────────────────────

def render_approaches_page(projects: list[dict[str, Any]]) -> str:
    """Generate the approaches index page with educational examples and project links."""
    proj_map = {p["name"]: p for p in projects}
    lines: list[str] = []

    lines.append("# Claude Code Integration Approaches\n")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n")
    lines.append("A practical reference to every integration approach discovered across "
                 "12 open-source projects.\n")
    lines.append("Each approach includes a copy-pasteable educational example and links "
                 "to real production code in the per-project detail pages.\n")

    # ── Table of contents ────────────────────────────────────────────────
    lines.append("## Approaches at a Glance\n")
    lines.append("| # | Approach | Projects |")
    lines.append("|---|----------|----------|")

    current_cat = ""
    for i, a in enumerate(APPROACHES, 1):
        cat = a["category"]
        if cat != current_cat:
            lines.append(f"| | **{cat}** | |")
            current_cat = cat
        proj_links = ", ".join(
            f"[{p}](projects/{p}.md)" for p in a["projects"]
        )
        anchor = a["title"].lower().replace(" ", "-").replace("(", "").replace(")", "").replace("&", "").replace("/", "").replace(",", "")
        lines.append(f"| {i} | [{a['title']}](#{anchor}) | {proj_links} |")
    lines.append("")

    # ── Approach sections ────────────────────────────────────────────────
    for i, a in enumerate(APPROACHES, 1):
        cat = a["category"]
        # Category header
        if i == 1 or APPROACHES[i - 2]["category"] != cat:
            lines.append(f"\n---\n\n## {cat} Approaches\n")

        lines.append(f"### {a['title']}\n")
        lines.append(a["description"].strip())
        lines.append("")

        # Educational example
        lines.append(f"```{a['example_lang']}")
        lines.append(a["example"].rstrip())
        lines.append("```\n")

        # Second example if present (e.g. both Python and TypeScript)
        if a.get("example2"):
            lines.append(f"```{a['example2_lang']}")
            lines.append(a["example2"].rstrip())
            lines.append("```\n")

        # Project links with brief descriptions
        lines.append("**Projects using this approach:**\n")
        lines.append("| Project | Language | Detail Page |")
        lines.append("|---------|----------|-------------|")
        for pname in a["projects"]:
            p = proj_map.get(pname)
            if not p or not p["metadata"]:
                lines.append(f"| {pname} | - | [view](projects/{pname}.md) |")
                continue
            meta = p["metadata"]
            lang = meta.get("primary_language", "-")
            repo = meta.get("repository", "")
            display = meta.get("display_name", pname)
            lines.append(
                f"| [{display}]({repo}) | {lang} | "
                f"[code quotes & permalinks](projects/{pname}.md) |"
            )
        lines.append("")

    # ── Footer ───────────────────────────────────────────────────────────
    lines.append("\n---")
    lines.append("*Auto-generated from YAML data by `scripts/generate_approach_pages.py`*")
    lines.append("")

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate approach pages and per-project detail pages")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT,
                        help="Output directory (default: reports/generated/)")
    args = parser.parse_args()

    console.print("[bold]Generating approach pages...[/bold]")

    projects = load_all_projects()
    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        return

    console.print(f"Loaded {len(projects)} project(s)")

    output_dir = args.output
    projects_dir = output_dir / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    # Generate per-project pages
    for p in projects:
        page = render_project_page(p)
        out_path = projects_dir / f"{p['name']}.md"
        out_path.write_text(page)
        console.print(f"  [green]Generated:[/green] {out_path}")

    # Generate approaches index
    approaches_page = render_approaches_page(projects)
    approaches_path = output_dir / "approaches.md"
    approaches_path.write_text(approaches_page)
    console.print(f"  [green]Generated:[/green] {approaches_path}")

    console.print(f"\n[bold green]Done![/bold green] {len(projects)} project pages + 1 approaches index")
    console.print(f"\nTo commit: cp -r {output_dir}/approaches.md {output_dir}/projects/ reports/committed/")


if __name__ == "__main__":
    main()
