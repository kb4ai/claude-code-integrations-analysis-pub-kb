# Future Work & Priorities

Roadmap for Claude Code integrations research.

## Immediate Priorities

### 1. Analyze Core Projects (High Priority)

These projects are known to integrate with Claude Code and should be analyzed first:

| Project | Repository | Why Important |
|---------|------------|---------------|
| **goose** | https://github.com/block/goose | Block's AI assistant; likely uses CLI integration patterns |
| **aider** | https://github.com/paul-gauthier/aider | Popular AI coding tool; may use SDK or CLI |
| **cline** | https://github.com/cline/cline | VS Code Claude extension; direct Claude integration |
| **continue** | https://github.com/continuedev/continue | IDE extension; multi-model including Claude |
| **claude-dev** | Search GitHub | Official Anthropic examples/templates |

**Action for each:**

```bash
# 1. Add submodule
git submodule add https://github.com/{org}/{repo}.git submodules/{name}

# 2. Copy template
cp -r projects/_template projects/{name}

# 3. Update metadata
# Edit projects/{name}/metadata.project.yaml

# 4. Run discovery (see AGENTS.md Phase 1)
cd submodules/{name}
rg -i "claude" --type py --type ts

# 5. Document findings in YAML files
# 6. Verify
./scripts/verify_yamls.py projects/{name}/
```

### 2. Discover Additional Projects

Search for more projects integrating with Claude Code:

```bash
# GitHub search queries to run:
# - "claude --session" language:python
# - "claude -p" language:typescript
# - "from anthropic import" language:python
# - "@anthropic-ai/sdk" language:typescript
# - "claude-agents-sdk"
# - "claude code" integration
```

Document discovered projects in `DISCOVERED_PROJECTS.md` before analyzing.

### 3. Complete Checklist Coverage

For each analyzed project, ensure all applicable checklist items are investigated:

* [ ] `checklists/cli-flags.checklist.yaml` - All CLI flags documented
* [ ] `checklists/sdk-features.checklist.yaml` - All SDK patterns documented
* [ ] `checklists/skills-plugins.checklist.yaml` - Skills/plugins support checked
* [ ] `checklists/research-completeness.checklist.yaml` - Quality criteria met

## Medium-Term Goals

### 4. Pattern Extraction

After analyzing 3+ projects, extract common patterns:

* **Session management patterns** - How do projects handle `--session`/`--resume`?
* **Output parsing patterns** - How is `--output-format=streaming-json` parsed?
* **Permission handling** - When/why is `--dangerously-skip-permissions` used?
* **Error recovery** - How do projects handle CLI/SDK errors?

Document in `reports/committed/patterns/`.

### 5. Comparison Reports

Generate and commit comparison reports:

```bash
./scripts/regenerate_comparison_tables_and_reports.py
cp reports/generated/comparison.md reports/committed/
git add reports/committed/
git commit -m "Update comparison report"
```

### 6. SDK Deep Dive

Investigate Claude Agents SDK specifically:

* Official documentation analysis
* Example code from Anthropic
* Third-party SDK wrappers
* TypeScript vs Python SDK differences

## Long-Term Goals

### 7. Best Practices Guide

Synthesize findings into actionable guidance:

* "How to integrate with Claude Code CLI"
* "CLI vs SDK: When to use which"
* "Session management best practices"
* "Streaming output handling patterns"

### 8. Automation Improvements

Enhance scripts:

* [ ] `scripts/discover_projects.py` - Automate GitHub search
* [ ] `scripts/verify_snippets.py` - Verify code snippets match source
* [ ] `scripts/update_submodules.py` - Batch update and re-analyze
* [ ] `scripts/coverage_report.py` - Detailed checklist coverage

### 9. Keep Analysis Current

* Set up periodic review (monthly?) to update analyses
* Track Claude Code CLI/SDK version changes
* Document breaking changes in integration patterns

## How to Pick What to Work On

```bash
# 1. Check current status
./scripts/research_status.py

# 2. See what's missing
./scripts/research_status.py --missing

# 3. Pick highest priority incomplete item:
#    - Projects with status "pending" → start analysis
#    - Projects with status "minimal" → expand to comprehensive
#    - No projects? → Add from priority list above

# 4. Follow AGENTS.md methodology
```

## Success Criteria

This research is "done enough" when:

* [ ] At least 5 projects analyzed to "comprehensive" status
* [ ] Common patterns documented in reports/
* [ ] Comparison tables generated and meaningful
* [ ] Fresh agent can understand and continue work from docs alone
