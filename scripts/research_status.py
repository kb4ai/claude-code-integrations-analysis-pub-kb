#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0",
# ]
# ///
"""
Display research status and coverage for Claude Code integration analysis.

Usage:
    ./scripts/research_status.py                     # Overview of all projects
    ./scripts/research_status.py --project goose     # Details for specific project
    ./scripts/research_status.py --verbose           # Detailed output
    ./scripts/research_status.py --checklist cli     # Coverage for specific checklist
    ./scripts/research_status.py --missing           # Show only missing items
"""

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

console = Console()

REPO_ROOT = Path(__file__).parent.parent
SPECS_DIR = REPO_ROOT / "specs"
PROJECTS_DIR = REPO_ROOT / "projects"
CHECKLISTS_DIR = REPO_ROOT / "checklists"


def load_yaml(path: Path) -> dict[str, Any] | None:
    """Load and parse a YAML file."""
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (yaml.YAMLError, FileNotFoundError):
        return None


def get_projects() -> list[str]:
    """Get list of project directories."""
    if not PROJECTS_DIR.exists():
        return []
    return [d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()]


def get_project_status(project_name: str) -> dict[str, Any]:
    """Get status information for a project."""
    project_dir = PROJECTS_DIR / project_name
    status = {
        "name": project_name,
        "exists": project_dir.exists(),
        "metadata": None,
        "files": [],
        "integration_types": [],
        "analysis_status": "pending",
        "checklist_coverage": {},
    }

    if not project_dir.exists():
        return status

    # Load metadata
    metadata_path = project_dir / "metadata.project.yaml"
    if metadata_path.exists():
        status["metadata"] = load_yaml(metadata_path)
        if status["metadata"]:
            status["integration_types"] = status["metadata"].get("integration_types", [])
            status["analysis_status"] = status["metadata"].get("analysis_status", "pending")

    # List data files
    for yaml_file in project_dir.glob("*.yaml"):
        status["files"].append(yaml_file.name)

    return status


def load_checklist(checklist_name: str) -> dict[str, Any] | None:
    """Load a checklist file."""
    # Try with and without .checklist.yaml suffix
    if not checklist_name.endswith(".checklist.yaml"):
        checklist_name = f"{checklist_name}.checklist.yaml"
    return load_yaml(CHECKLISTS_DIR / checklist_name)


def get_checklist_items(checklist: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract all items from a checklist."""
    items = []
    for category_name, category in checklist.get("categories", {}).items():
        for item in category.get("items", []):
            item["category"] = category_name
            items.append(item)
    return items


def calculate_coverage(project_status: dict[str, Any], checklist_name: str) -> dict[str, Any]:
    """Calculate coverage for a project against a checklist."""
    checklist = load_checklist(checklist_name)
    if not checklist:
        return {"error": f"Checklist not found: {checklist_name}"}

    items = get_checklist_items(checklist)
    total = len(items)

    # TODO: Implement actual coverage checking by parsing project YAML files
    # For now, return placeholder
    return {
        "checklist": checklist_name,
        "total_items": total,
        "covered": 0,  # Placeholder
        "missing": total,  # Placeholder
        "coverage_pct": 0,  # Placeholder
    }


def display_overview():
    """Display overview of all projects."""
    projects = get_projects()

    console.print(Panel.fit(
        "[bold]Claude Code Integrations Analysis[/bold]\n"
        "Research status overview",
        border_style="blue"
    ))

    if not projects:
        console.print("\n[yellow]No projects found.[/yellow]")
        console.print("Create a project: mkdir -p projects/{name}")
        return

    # Projects table
    table = Table(title="Projects")
    table.add_column("Project", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Integration Types")
    table.add_column("Files")
    table.add_column("Commit")

    for project_name in sorted(projects):
        status = get_project_status(project_name)

        status_style = {
            "pending": "[yellow]pending[/yellow]",
            "minimal": "[blue]minimal[/blue]",
            "in-progress": "[cyan]in-progress[/cyan]",
            "comprehensive": "[green]comprehensive[/green]",
        }.get(status["analysis_status"], status["analysis_status"])

        integration_types = ", ".join(status["integration_types"]) or "-"
        file_count = str(len(status["files"]))

        commit = "-"
        if status["metadata"]:
            commit = status["metadata"].get("analyzed_commit", "-")[:8]

        table.add_row(
            project_name,
            status_style,
            integration_types,
            file_count,
            commit
        )

    console.print(table)

    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total projects: {len(projects)}")

    status_counts = {}
    for project_name in projects:
        status = get_project_status(project_name)
        s = status["analysis_status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    for s, count in sorted(status_counts.items()):
        console.print(f"  {s}: {count}")


def display_project_details(project_name: str, verbose: bool = False):
    """Display detailed status for a specific project."""
    status = get_project_status(project_name)

    if not status["exists"]:
        console.print(f"[red]Project not found:[/red] {project_name}")
        return

    console.print(Panel.fit(
        f"[bold]{project_name}[/bold]\n"
        f"Status: {status['analysis_status']}",
        border_style="blue"
    ))

    # Metadata
    if status["metadata"]:
        meta = status["metadata"]
        console.print("\n[bold]Metadata:[/bold]")
        console.print(f"  Display name: {meta.get('display_name', '-')}")
        console.print(f"  Repository: {meta.get('repository', '-')}")
        console.print(f"  Analyzed commit: {meta.get('analyzed_commit', '-')}")
        console.print(f"  Analyzed at: {meta.get('analyzed_at', '-')}")
        console.print(f"  Primary language: {meta.get('primary_language', '-')}")
        console.print(f"  Integration types: {', '.join(meta.get('integration_types', []))}")
    else:
        console.print("\n[yellow]No metadata.project.yaml found[/yellow]")

    # Files
    console.print("\n[bold]Data files:[/bold]")
    for f in sorted(status["files"]):
        console.print(f"  • {f}")

    if not status["files"]:
        console.print("  [yellow]No data files[/yellow]")

    # Checklist coverage (placeholder)
    if verbose:
        console.print("\n[bold]Checklist coverage:[/bold]")
        for checklist_file in CHECKLISTS_DIR.glob("*.checklist.yaml"):
            checklist_name = checklist_file.stem.replace(".checklist", "")
            coverage = calculate_coverage(status, checklist_name)
            if "error" not in coverage:
                console.print(f"  {checklist_name}: {coverage['covered']}/{coverage['total_items']} ({coverage['coverage_pct']:.0f}%)")


def display_checklist_coverage(checklist_name: str):
    """Display coverage for a specific checklist across all projects."""
    checklist = load_checklist(checklist_name)
    if not checklist:
        console.print(f"[red]Checklist not found:[/red] {checklist_name}")
        return

    console.print(Panel.fit(
        f"[bold]Checklist: {checklist_name}[/bold]\n"
        f"{checklist.get('description', '').strip()[:100]}...",
        border_style="blue"
    ))

    items = get_checklist_items(checklist)

    # Group by category
    by_category = {}
    for item in items:
        cat = item.get("category", "other")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)

    tree = Tree(f"[bold]{checklist_name}[/bold]")
    for category, cat_items in by_category.items():
        branch = tree.add(f"[cyan]{category}[/cyan] ({len(cat_items)} items)")
        for item in cat_items[:5]:  # Show first 5
            item_id = item.get("id", "?")
            desc = item.get("description", "")[:50]
            branch.add(f"{item_id}: {desc}")
        if len(cat_items) > 5:
            branch.add(f"[dim]... and {len(cat_items) - 5} more[/dim]")

    console.print(tree)


def display_missing():
    """Display what's missing across all projects."""
    projects = get_projects()

    console.print(Panel.fit(
        "[bold]Missing Analysis Items[/bold]",
        border_style="yellow"
    ))

    for project_name in sorted(projects):
        status = get_project_status(project_name)
        missing = []

        if not status["metadata"]:
            missing.append("metadata.project.yaml")

        if status["analysis_status"] == "pending":
            missing.append("any analysis data")

        if "cli" in status["integration_types"]:
            if "cli.cli-integration.yaml" not in status["files"]:
                missing.append("cli.cli-integration.yaml")

        if "sdk" in status["integration_types"]:
            if "sdk.sdk-integration.yaml" not in status["files"]:
                missing.append("sdk.sdk-integration.yaml")

        if missing:
            console.print(f"\n[cyan]{project_name}[/cyan]")
            for item in missing:
                console.print(f"  [yellow]•[/yellow] Missing: {item}")


def main():
    parser = argparse.ArgumentParser(description="Research status for Claude Code integrations")
    parser.add_argument("--project", "-p", help="Show details for specific project")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--checklist", "-c", help="Show coverage for specific checklist")
    parser.add_argument("--missing", "-m", action="store_true", help="Show missing items")

    args = parser.parse_args()

    if args.project:
        display_project_details(args.project, args.verbose)
    elif args.checklist:
        display_checklist_coverage(args.checklist)
    elif args.missing:
        display_missing()
    else:
        display_overview()


if __name__ == "__main__":
    main()
