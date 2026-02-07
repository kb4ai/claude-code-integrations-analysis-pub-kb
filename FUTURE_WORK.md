# Future Work & Priorities

Roadmap for Claude Code integrations research.

## Completed

### 1. Core Project Analysis (12/12 Complete)

All core projects have been analyzed to "comprehensive" status:

| # | Project | Type | Key Finding |
|---|---------|------|-------------|
| 1 | goose | CLI | Persistent subprocess, bidirectional NDJSON |
| 2 | aider | SDK | LiteLLM + cache warming (background thread) |
| 3 | continue | SDK | Direct SDK + 4 caching strategies + Azure detection |
| 4 | cline | CLI+SDK | Dual integration, --max-turns 1 + --disallowedTools |
| 5 | claude-code-action | SDK | Official Agent SDK, query() async iterator |
| 6 | claude-code-mcp | CLI | Per-request spawn, agent-in-agent MCP wrapper |
| 7 | claude-flow | CLI | Multi-instance spawn, DAG orchestration |
| 8 | openhands | SDK | LiteLLM + model-specific workarounds |
| 9 | fastmcp | SDK+CLI | MCP sampling + `claude mcp add` + skills |
| 10 | gptme | SDK | Richest Anthropic SDK feature set |
| 11 | alphacodium | SDK | Minimal LiteLLM (GPT-4 default, Claude optional) |
| 12 | anthropic-cookbook | All | Official canonical examples for all patterns |

### 2. Comparison Tables

* [x] `reports/generated/comparison.md` auto-generated
* [x] `reports/generated/summary.json` auto-generated
* [x] `reports/committed/comparison.md` committed snapshot

### 3. Pattern Extraction Reports

* [x] `reports/committed/patterns/cli-integration-patterns.md` - 5 CLI patterns
* [x] `reports/committed/patterns/sdk-integration-patterns.md` - 3 SDK layers + features
* [x] `reports/committed/patterns/decision-guide.md` - Integration decision tree

### 4. Success Criteria Met

* [x] At least 5 projects analyzed to "comprehensive" status (12 achieved)
* [x] Common patterns documented in reports/
* [x] Comparison tables generated and meaningful
* [x] Fresh agent can understand and continue work from docs alone

## Remaining Priorities

### Medium Priority

#### 5. Discover Additional Projects

Search for more projects integrating with Claude Code:

```bash
# GitHub search queries to run:
# - "claude --session" language:python
# - "claude -p" language:typescript
# - "from anthropic import" language:python
# - "@anthropic-ai/sdk" language:typescript
# - "claude-agents-sdk"
# - "@anthropic-ai/claude-agent-sdk"
```

See `DISCOVERED_PROJECTS.md` for the full discovery list (50+ candidates).
Many may be trivial wrappers; prioritize projects with unique integration patterns.

#### 6. SDK Deep Dive

Investigate Claude Agents SDK specifically:

* Official documentation analysis (latest API reference)
* TypeScript vs Python SDK differences
* query() vs ClaudeSDKClient API comparison
* Version history and breaking changes

#### 7. Checklist Gap Analysis

For each analyzed project, verify all applicable checklist items are covered:

* [ ] `checklists/cli-flags.checklist.yaml` - All CLI flags documented
* [ ] `checklists/sdk-features.checklist.yaml` - All SDK patterns documented
* [ ] `checklists/skills-plugins.checklist.yaml` - Skills/plugins support checked
* [ ] `checklists/research-completeness.checklist.yaml` - Quality criteria met

Run `./scripts/research_status.py --missing` to identify specific gaps.

### Low Priority

#### 8. Automation Improvements

Enhance scripts:

* [ ] `scripts/discover_projects.py` - Automate GitHub search
* [ ] `scripts/verify_snippets.py` - Verify code snippets match source
* [ ] `scripts/update_submodules.py` - Batch update and re-analyze
* [ ] `scripts/coverage_report.py` - Detailed checklist coverage

#### 9. Keep Analysis Current

* Set up periodic review (monthly?) to update analyses
* Track Claude Code CLI/SDK version changes
* Document breaking changes in integration patterns
* When updating, bump `analyzed_commit` and `analyzed_at` fields

#### 10. Expand Pattern Reports

Additional reports that could be valuable:

* Error handling patterns across projects
* Authentication and API key management patterns
* Session lifecycle management patterns
* Tool restriction strategies comparison

## How to Pick What to Work On

```bash
# 1. Check current status
./scripts/research_status.py

# 2. See what's missing
./scripts/research_status.py --missing

# 3. Pick highest priority incomplete item from this file

# 4. Follow AGENTS.md methodology
```
