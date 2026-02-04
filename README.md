# Claude Code Integrations Analysis

Research repository analyzing how different projects integrate with Claude Code under the hood.

## Purpose

Systematic analysis of integration patterns across the Claude Code ecosystem:

* CLI flag usage (`--session`, `--resume`, `--output-format`, `--dangerously-skip-permissions`, etc.)
* Claude Agents SDK integration patterns
* Skills and Plugins utilization
* Marketplace integrations
* Common architectural patterns

All findings include **code snippets with precise references** (repository, commit, path, line numbers, function names).

## Repository Structure

```
.
├── CLAUDE.md              # Instructions for AI agents (symlinked as AGENTS.md context)
├── AGENTS.md              # Agent-specific research instructions
├── specs/                 # YAML specifications defining data structure
│   ├── project.spec.yaml          # Schema for project analysis files
│   ├── cli-integration.spec.yaml  # Schema for CLI flag analysis
│   ├── sdk-integration.spec.yaml  # Schema for SDK usage analysis
│   └── code-reference.spec.yaml   # Schema for code snippet references
├── checklists/            # Research criteria checklists
│   ├── cli-flags.checklist.yaml
│   ├── sdk-features.checklist.yaml
│   ├── skills-plugins.checklist.yaml
│   └── research-completeness.checklist.yaml
├── projects/              # Per-project analysis data
│   ├── goose/
│   │   ├── metadata.project.yaml
│   │   ├── cli.cli-integration.yaml
│   │   └── references.code-reference.yaml
│   ├── cursor/
│   ├── continue-dev/
│   └── ...
├── submodules/            # Git submodules of analyzed repositories
├── scripts/               # Analysis and verification tools
│   ├── research_status.py
│   ├── verify_yamls.py
│   └── regenerate_comparison_tables_and_reports.py
├── reports/               # Generated analysis reports
│   ├── generated/         # Auto-generated (gitignored)
│   └── committed/         # Curated reports to commit
└── tmp/                   # Temporary workspace (gitignored)
```

## Quick Start

```bash
# Check research coverage status
./scripts/research_status.py

# Verify all YAML files are valid
./scripts/verify_yamls.py

# Regenerate comparison tables and reports
./scripts/regenerate_comparison_tables_and_reports.py

# Add a new project submodule for analysis
git submodule add https://github.com/org/repo.git submodules/repo-name
```

## Data File Naming Convention

Files follow the pattern: `{descriptive-name}.{spec-type}.yaml`

* `metadata.project.yaml` - Project metadata conforming to `specs/project.spec.yaml`
* `cli.cli-integration.yaml` - CLI integration data conforming to `specs/cli-integration.spec.yaml`
* `sdk.sdk-integration.yaml` - SDK integration data conforming to `specs/sdk-integration.spec.yaml`
* `*.code-reference.yaml` - Code references conforming to `specs/code-reference.spec.yaml`

## Adding a New Project

1. Create project directory: `mkdir -p projects/{project-name}`
2. Add submodule: `git submodule add https://github.com/org/repo.git submodules/{project-name}`
3. Create `metadata.project.yaml` from template
4. Run analysis following `AGENTS.md` instructions
5. Verify: `./scripts/verify_yamls.py projects/{project-name}/`
6. Check coverage: `./scripts/research_status.py --project {project-name}`

## Submodule Management

Submodules are pinned to the commit at which analysis was performed:

```bash
# Update submodule to latest and re-analyze
cd submodules/{project}
git fetch origin
git checkout origin/main
cd ../..
git add submodules/{project}
# Update analysis YAML files with new commit hash
git commit -m "Update {project} analysis to commit {hash}"
```

## Contributing

See `AGENTS.md` for detailed research instructions and criteria coverage requirements.
