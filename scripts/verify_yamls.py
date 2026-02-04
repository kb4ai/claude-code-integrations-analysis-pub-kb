#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
#     "rich>=13.0",
# ]
# ///
"""
Verify YAML files conform to their specifications.

Usage:
    ./scripts/verify_yamls.py                    # Verify all
    ./scripts/verify_yamls.py projects/goose/    # Verify specific project
    ./scripts/verify_yamls.py --spec-only        # Only validate specs
"""

import sys
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table

console = Console()

REPO_ROOT = Path(__file__).parent.parent
SPECS_DIR = REPO_ROOT / "specs"
PROJECTS_DIR = REPO_ROOT / "projects"


def load_yaml(path: Path) -> dict[str, Any] | None:
    """Load and parse a YAML file."""
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        console.print(f"[red]YAML parse error in {path}:[/red] {e}")
        return None
    except FileNotFoundError:
        console.print(f"[red]File not found:[/red] {path}")
        return None


def get_spec_type_from_filename(filename: str) -> str | None:
    """Extract spec type from filename pattern: name.{type}.yaml"""
    parts = filename.rsplit(".", 2)
    if len(parts) >= 3 and parts[-1] == "yaml":
        return parts[-2]
    return None


def load_spec(spec_type: str) -> dict[str, Any] | None:
    """Load a spec file by type."""
    spec_path = SPECS_DIR / f"{spec_type}.spec.yaml"
    return load_yaml(spec_path)


def validate_required_fields(
    data: dict[str, Any],
    spec: dict[str, Any],
    path: str = ""
) -> list[str]:
    """Validate required fields are present."""
    errors = []
    fields = spec.get("fields", {})

    for field_name, field_spec in fields.items():
        if not isinstance(field_spec, dict):
            continue

        field_path = f"{path}.{field_name}" if path else field_name
        is_required = field_spec.get("required", False)

        if is_required and field_name not in data:
            errors.append(f"Missing required field: {field_path}")
        elif field_name in data:
            value = data[field_name]
            field_type = field_spec.get("type")

            # Type validation
            if field_type == "string" and not isinstance(value, str):
                errors.append(f"Field {field_path} should be string, got {type(value).__name__}")
            elif field_type == "boolean" and not isinstance(value, bool):
                errors.append(f"Field {field_path} should be boolean, got {type(value).__name__}")
            elif field_type == "list" and not isinstance(value, list):
                errors.append(f"Field {field_path} should be list, got {type(value).__name__}")
            elif field_type == "object" and not isinstance(value, dict):
                errors.append(f"Field {field_path} should be object, got {type(value).__name__}")
            elif field_type == "enum":
                enum_values = field_spec.get("enum_values", [])
                if value not in enum_values:
                    errors.append(f"Field {field_path} has invalid value '{value}', expected one of: {enum_values}")

            # Format validation (skip for empty strings on optional fields)
            if field_spec.get("format") == "git-sha":
                if isinstance(value, str) and value and len(value) != 40:
                    errors.append(f"Field {field_path} should be 40-char git SHA, got {len(value)} chars")

            if field_spec.get("format") == "url":
                # Skip validation for empty strings on optional fields
                if isinstance(value, str) and value and not (value.startswith("http://") or value.startswith("https://")):
                    errors.append(f"Field {field_path} should be a URL, got: {value[:50]}...")

    return errors


def validate_file(file_path: Path) -> tuple[bool, list[str]]:
    """Validate a single YAML file against its spec."""
    errors = []

    # Load the file
    data = load_yaml(file_path)
    if data is None:
        return False, ["Failed to parse YAML"]

    # Determine spec type from filename
    spec_type = get_spec_type_from_filename(file_path.name)
    if not spec_type:
        # Not a typed file, just check valid YAML
        return True, []

    # Load the spec
    spec = load_spec(spec_type)
    if spec is None:
        errors.append(f"Unknown spec type: {spec_type}")
        return False, errors

    # Validate against spec
    errors.extend(validate_required_fields(data, spec))

    return len(errors) == 0, errors


def validate_specs() -> tuple[int, int]:
    """Validate all spec files are valid YAML."""
    valid = 0
    invalid = 0

    console.print("\n[bold]Validating spec files...[/bold]")

    for spec_file in SPECS_DIR.glob("*.spec.yaml"):
        data = load_yaml(spec_file)
        if data is not None:
            console.print(f"  [green]✓[/green] {spec_file.name}")
            valid += 1
        else:
            console.print(f"  [red]✗[/red] {spec_file.name}")
            invalid += 1

    return valid, invalid


def validate_project(project_path: Path) -> tuple[int, int, list[tuple[str, list[str]]]]:
    """Validate all YAML files in a project directory."""
    valid = 0
    invalid = 0
    all_errors = []

    for yaml_file in project_path.glob("*.yaml"):
        is_valid, errors = validate_file(yaml_file)
        if is_valid:
            valid += 1
        else:
            invalid += 1
            all_errors.append((str(yaml_file.relative_to(REPO_ROOT)), errors))

    return valid, invalid, all_errors


def validate_all_projects() -> tuple[int, int, list[tuple[str, list[str]]]]:
    """Validate all project YAML files."""
    total_valid = 0
    total_invalid = 0
    all_errors = []

    if not PROJECTS_DIR.exists():
        return 0, 0, []

    for project_dir in PROJECTS_DIR.iterdir():
        if project_dir.is_dir():
            valid, invalid, errors = validate_project(project_dir)
            total_valid += valid
            total_invalid += invalid
            all_errors.extend(errors)

    return total_valid, total_invalid, all_errors


def main():
    args = sys.argv[1:]

    spec_only = "--spec-only" in args
    args = [a for a in args if not a.startswith("--")]

    # Validate specs
    spec_valid, spec_invalid = validate_specs()

    if spec_only:
        console.print(f"\nSpecs: {spec_valid} valid, {spec_invalid} invalid")
        sys.exit(0 if spec_invalid == 0 else 1)

    # Validate specific path or all projects
    if args:
        target_path = Path(args[0])
        if target_path.is_dir():
            valid, invalid, errors = validate_project(target_path)
        elif target_path.is_file():
            is_valid, file_errors = validate_file(target_path)
            valid = 1 if is_valid else 0
            invalid = 0 if is_valid else 1
            errors = [(str(target_path), file_errors)] if file_errors else []
        else:
            console.print(f"[red]Path not found:[/red] {target_path}")
            sys.exit(1)
    else:
        valid, invalid, errors = validate_all_projects()

    # Print results
    console.print(f"\n[bold]Results:[/bold]")
    console.print(f"  Specs: {spec_valid} valid, {spec_invalid} invalid")
    console.print(f"  Data files: {valid} valid, {invalid} invalid")

    if errors:
        console.print(f"\n[bold red]Errors:[/bold red]")
        for file_path, file_errors in errors:
            console.print(f"\n  [yellow]{file_path}[/yellow]")
            for error in file_errors:
                console.print(f"    [red]•[/red] {error}")

    total_invalid = spec_invalid + invalid
    if total_invalid == 0:
        console.print("\n[bold green]All validations passed![/bold green]")
    else:
        console.print(f"\n[bold red]{total_invalid} file(s) failed validation[/bold red]")

    sys.exit(0 if total_invalid == 0 else 1)


if __name__ == "__main__":
    main()
