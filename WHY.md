# Why This Research Matters

## The Problem

Claude Code is becoming a core component in the AI coding assistant ecosystem. Many projects integrate with it, but:

* **No central documentation** of how projects actually integrate
* **Hidden patterns** - best practices are buried in source code
* **Fragmented knowledge** - each project reinvents integration approaches
* **Version drift** - integration patterns may break with Claude Code updates

## What We're Building

A systematic, evidence-based knowledge base of:

1. **How projects integrate** - CLI flags, SDK methods, configuration
2. **Common patterns** - session management, streaming, error handling
3. **Best practices** - what works well, what doesn't
4. **Comparison data** - which approach for which use case

## Use Cases

### For Developers Building Claude Integrations

> "I want to integrate Claude Code into my project. How do others do it?"

* Browse analyzed projects for patterns
* See real code snippets with working examples
* Understand trade-offs between CLI vs SDK approaches

### For Claude Code Maintainers

> "Which flags are actually used? What would break if we change X?"

* See which flags/features are used across the ecosystem
* Understand integration patterns before making changes
* Identify documentation gaps

### For AI Assistants

> "Help me integrate Claude Code into this project"

* Reference specific patterns with code snippets
* Provide evidence-based recommendations
* Avoid hallucinating integration approaches

## Research Questions We're Answering

### CLI Integration

* Which flags are commonly used together?
* How is `--session` used for conversation continuity?
* When is `--dangerously-skip-permissions` appropriate?
* How is `--output-format=streaming-json` parsed?

### SDK Integration

* SDK vs CLI: when to use which?
* Common tool registration patterns?
* Streaming vs synchronous message handling?
* Error handling and retry strategies?

### Ecosystem

* Do projects support Claude Code Skills?
* How is the Marketplace integrated?
* MCP server integration patterns?

## Expected Outcomes

### Short Term

* 5+ projects analyzed with comprehensive documentation
* Comparison tables showing flag/feature usage
* Searchable YAML data for programmatic access

### Medium Term

* Extracted patterns documented as best practices
* Recommendations for different use cases
* Gap analysis for Claude Code documentation

### Long Term

* Living reference for Claude Code ecosystem
* Automated tracking of integration pattern changes
* Community contribution to expand coverage

## Why YAML + Code References?

### Machine-Readable

```bash
# Query: which projects use --session?
yq '.invocations[].flags_used[] | select(.flag == "--session")' projects/*/cli.cli-integration.yaml
```

### Verifiable

Every claim can be verified:

```bash
cd submodules/goose
git checkout abc123...
sed -n '142,158p' src/client.py
# Should match the snippet in our YAML
```

### Maintainable

* Specs define structure → validation catches errors
* Checklists ensure completeness → nothing forgotten
* Scripts automate → consistency across analyses

## How to Contribute

1. **Pick a project** from `FUTURE_WORK.md`
2. **Follow methodology** in `AGENTS.md`
3. **Document findings** in YAML files
4. **Verify** with scripts
5. **Commit** with clear messages

Every analysis helps build the complete picture.
