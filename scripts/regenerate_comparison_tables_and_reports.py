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
Regenerate comparison tables and reports from YAML data.

Usage:
    ./scripts/regenerate_comparison_tables_and_reports.py           # Generate all
    ./scripts/regenerate_comparison_tables_and_reports.py --format md    # Markdown only
    ./scripts/regenerate_comparison_tables_and_reports.py --format html  # HTML only
    ./scripts/regenerate_comparison_tables_and_reports.py --output reports/generated/
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from jinja2 import Environment, BaseLoader

console = Console()

REPO_ROOT = Path(__file__).parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
REPORTS_DIR = REPO_ROOT / "reports"
GENERATED_DIR = REPORTS_DIR / "generated"


def load_yaml(path: Path) -> dict[str, Any] | None:
    """Load and parse a YAML file."""
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (yaml.YAMLError, FileNotFoundError):
        return None


def get_all_project_data() -> list[dict[str, Any]]:
    """Load data for all projects."""
    projects = []

    if not PROJECTS_DIR.exists():
        return projects

    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        project_data = {
            "name": project_dir.name,
            "metadata": None,
            "cli": None,
            "sdk": None,
            "code_references": [],
        }

        # Load metadata
        metadata_path = project_dir / "metadata.project.yaml"
        if metadata_path.exists():
            project_data["metadata"] = load_yaml(metadata_path)

        # Load CLI integration
        cli_path = project_dir / "cli.cli-integration.yaml"
        if cli_path.exists():
            project_data["cli"] = load_yaml(cli_path)

        # Load SDK integration
        sdk_path = project_dir / "sdk.sdk-integration.yaml"
        if sdk_path.exists():
            project_data["sdk"] = load_yaml(sdk_path)

        # Load code references
        for ref_file in project_dir.glob("*.code-reference.yaml"):
            ref_data = load_yaml(ref_file)
            if ref_data:
                project_data["code_references"].append(ref_data)

        projects.append(project_data)

    return projects


def extract_cli_flags(projects: list[dict[str, Any]]) -> dict[str, dict[str, bool]]:
    """Extract CLI flag usage across projects."""
    # Known flags to track
    known_flags = [
        "--session", "--resume", "-c", "-p",
        "--output-format", "--dangerously-skip-permissions",
        "--model", "--max-turns", "--system-prompt",
        "--mcp-config", "--allowedTools", "--verbose"
    ]

    flags_matrix = {flag: {} for flag in known_flags}

    for project in projects:
        name = project["name"]
        cli_data = project.get("cli")

        for flag in known_flags:
            flags_matrix[flag][name] = False

        if cli_data and cli_data.get("cli_integration_detected"):
            # Check invocations for flags
            for invocation in cli_data.get("invocations", []):
                for flag_info in invocation.get("flags_used", []):
                    flag = flag_info.get("flag", "")
                    if flag in flags_matrix:
                        flags_matrix[flag][name] = True

            # Check flags_summary if available
            for flag, info in cli_data.get("flags_summary", {}).items():
                if flag in flags_matrix and info.get("used"):
                    flags_matrix[flag][name] = True

    return flags_matrix


def extract_sdk_patterns(projects: list[dict[str, Any]]) -> dict[str, dict[str, bool]]:
    """Extract SDK pattern usage across projects."""
    known_patterns = [
        "messages-create", "messages-stream", "tool-use",
        "vision", "agent-create", "agent-run",
        "conversation-management", "error-handling"
    ]

    patterns_matrix = {pattern: {} for pattern in known_patterns}

    for project in projects:
        name = project["name"]
        sdk_data = project.get("sdk")

        for pattern in known_patterns:
            patterns_matrix[pattern][name] = False

        if sdk_data and sdk_data.get("sdk_integration_detected"):
            for usage in sdk_data.get("sdk_usage", []):
                pattern = usage.get("pattern", "")
                if pattern in patterns_matrix:
                    patterns_matrix[pattern][name] = True

    return patterns_matrix


MARKDOWN_TEMPLATE = """# Claude Code Integrations Comparison

Generated: {{ generated_at }}

## Projects Overview

| Project | Repository | Status | Integration Types |
|---------|-----------|--------|-------------------|
{% for p in projects %}| {{ p.name }} | {{ p.metadata.repository if p.metadata else '-' }} | {{ p.metadata.analysis_status if p.metadata else 'pending' }} | {{ p.metadata.integration_types|join(', ') if p.metadata and p.metadata.integration_types else '-' }} |
{% endfor %}

## CLI Flags Usage

| Flag | {% for p in projects %}{{ p.name }} | {% endfor %}
|------|{% for p in projects %}:---:| {% endfor %}
{% for flag, usage in cli_flags.items() %}| `{{ flag }}` | {% for p in projects %}{{ '✓' if usage.get(p.name) else '-' }} | {% endfor %}
{% endfor %}

## SDK Patterns Usage

| Pattern | {% for p in projects %}{{ p.name }} | {% endfor %}
|---------|{% for p in projects %}:---:| {% endfor %}
{% for pattern, usage in sdk_patterns.items() %}| {{ pattern }} | {% for p in projects %}{{ '✓' if usage.get(p.name) else '-' }} | {% endfor %}
{% endfor %}

## Integration Details

{% for p in projects %}
### {{ p.name }}

{% if p.metadata %}
* **Repository**: {{ p.metadata.repository }}
* **Analyzed commit**: `{{ p.metadata.analyzed_commit[:8] if p.metadata.analyzed_commit else '-' }}`
* **Status**: {{ p.metadata.analysis_status }}
{% endif %}

{% if p.cli and p.cli.cli_integration_detected %}
#### CLI Integration

{{ p.cli.summary if p.cli.summary else 'CLI integration detected.' }}

**Invocations found**: {{ p.cli.invocations|length if p.cli.invocations else 0 }}
{% endif %}

{% if p.sdk and p.sdk.sdk_integration_detected %}
#### SDK Integration

{{ p.sdk.summary if p.sdk.summary else 'SDK integration detected.' }}

**SDK patterns used**: {{ p.sdk.sdk_usage|length if p.sdk.sdk_usage else 0 }}
{% endif %}

{% endfor %}

---
*Report generated by `scripts/regenerate_comparison_tables_and_reports.py`*
"""


def generate_markdown_report(projects: list[dict[str, Any]], output_path: Path):
    """Generate markdown comparison report."""
    env = Environment(loader=BaseLoader())
    template = env.from_string(MARKDOWN_TEMPLATE)

    cli_flags = extract_cli_flags(projects)
    sdk_patterns = extract_sdk_patterns(projects)

    content = template.render(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        projects=projects,
        cli_flags=cli_flags,
        sdk_patterns=sdk_patterns,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    console.print(f"[green]Generated:[/green] {output_path}")


def generate_summary_json(projects: list[dict[str, Any]], output_path: Path):
    """Generate JSON summary for programmatic use."""
    import json

    summary = {
        "generated_at": datetime.now().isoformat(),
        "project_count": len(projects),
        "projects": [],
        "cli_flags_matrix": extract_cli_flags(projects),
        "sdk_patterns_matrix": extract_sdk_patterns(projects),
    }

    for p in projects:
        proj_summary = {
            "name": p["name"],
            "repository": p["metadata"].get("repository") if p["metadata"] else None,
            "status": p["metadata"].get("analysis_status") if p["metadata"] else "pending",
            "integration_types": p["metadata"].get("integration_types", []) if p["metadata"] else [],
            "cli_detected": bool(p.get("cli") and p["cli"].get("cli_integration_detected")),
            "sdk_detected": bool(p.get("sdk") and p["sdk"].get("sdk_integration_detected")),
        }
        summary["projects"].append(proj_summary)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))
    console.print(f"[green]Generated:[/green] {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate comparison reports")
    parser.add_argument("--format", choices=["md", "html", "json", "all"], default="all",
                        help="Output format")
    parser.add_argument("--output", "-o", type=Path, default=GENERATED_DIR,
                        help="Output directory")

    args = parser.parse_args()

    console.print("[bold]Regenerating comparison tables and reports...[/bold]")

    projects = get_all_project_data()

    if not projects:
        console.print("[yellow]No projects found. Nothing to generate.[/yellow]")
        return

    console.print(f"Found {len(projects)} project(s)")

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    formats = [args.format] if args.format != "all" else ["md", "json"]

    for fmt in formats:
        if fmt == "md":
            generate_markdown_report(projects, output_dir / "comparison.md")
        elif fmt == "json":
            generate_summary_json(projects, output_dir / "summary.json")
        elif fmt == "html":
            console.print("[yellow]HTML format not yet implemented[/yellow]")

    console.print("\n[bold green]Report generation complete![/bold green]")


if __name__ == "__main__":
    main()
