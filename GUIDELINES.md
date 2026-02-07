# Research Guidelines

Standards and best practices for contributing to this research repository.

## Core Principles

### 1. Evidence-Based Documentation

**Every claim must have a code reference.**

Bad:
> "Goose uses streaming JSON output"

Good:
> "Goose uses streaming JSON output"
> Reference: `goose/src/client.py:142-158`, commit `abc123...`
> ```python
> subprocess.run(["claude", "--output-format", "streaming-json", ...])
> ```

### 2. Reproducibility

All findings must be reproducible by:

* Pinning to specific commit SHA (full 40 chars)
* Including exact file paths and line numbers
* Providing verbatim code snippets
* Using HTTPS URLs (not SSH) for submodules

### 3. Completeness Over Speed

* Investigate all checklist items, even if answer is "not used"
* Document negative findings ("does NOT use --session")
* Cross-reference with similar projects

## YAML File Standards

### Naming Convention

```
{descriptive-name}.{spec-type}.yaml
```

Examples:

* `metadata.project.yaml` - conforms to `specs/project.spec.yaml`
* `cli.cli-integration.yaml` - conforms to `specs/cli-integration.spec.yaml`
* `streaming.code-reference.yaml` - conforms to `specs/code-reference.spec.yaml`

### Required Validation

Before committing, always run:

```bash
./scripts/verify_yamls.py projects/{name}/
```

### Commit Hashes

* Always use full 40-character SHA
* Never use branch names or tags (they move)
* Update `analyzed_commit` when re-analyzing

```yaml
# Good
analyzed_commit: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"

# Bad
analyzed_commit: "main"
analyzed_commit: "v1.2.3"
analyzed_commit: "a1b2c3d"  # Too short
```

## Code Snippet Standards

### Context

Include 2-5 lines of context around the key code:

```yaml
snippet: |
  def invoke_claude(self, prompt: str) -> str:
      """Invoke Claude Code with session management."""  # Context
      cmd = [
          "claude",
          "--session", self.session_id,  # THE KEY PART
          "-p", prompt
      ]
      result = subprocess.run(cmd, capture_output=True)  # Context
      return result.stdout
```

### Preserve Original Formatting

* Keep original indentation
* Don't "clean up" or reformat
* Include comments from original

### Language Annotation

Always specify the language:

```yaml
reference:
  language: python  # or typescript, go, rust, etc.
```

## Git Workflow

### Commit Messages

```
{action} {project} {what}

* Specific change 1
* Specific change 2

Co-Authored-By: Claude <noreply@anthropic.com>
```

Examples:

```
Add goose CLI integration analysis

* Document --session and --output-format usage
* Add code references for invoke_claude function
* Mark as "minimal" status

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Branch Strategy

For multi-project work sessions:

```bash
git checkout -b analysis/{date}-{focus}
# e.g., analysis/2026-02-07-goose-cli
```

### Submodule Commits

Commit submodule pointer updates separately:

```bash
# First: add/update submodule
git add submodules/goose
git commit -m "Add goose submodule at commit abc123"

# Then: add analysis
git add projects/goose/
git commit -m "Add goose CLI integration analysis"
```

## Research Workflow

### Starting a New Project

1. **Check if already exists:**
   ```bash
   ls projects/
   ./scripts/research_status.py
   ```

2. **Add submodule:**
   ```bash
   git submodule add https://github.com/org/repo.git submodules/{name}
   ```

3. **Copy template:**
   ```bash
   cp -r projects/_template projects/{name}
   ```

4. **Update metadata immediately:**
   Edit `projects/{name}/metadata.project.yaml` with correct info

5. **Run discovery (AGENTS.md Phase 1)**

6. **Document findings systematically**

7. **Verify before committing:**
   ```bash
   ./scripts/verify_yamls.py projects/{name}/
   ./scripts/research_status.py --project {name}
   ```

### Updating Existing Analysis

1. **Update submodule:**
   ```bash
   cd submodules/{name}
   git fetch origin
   git log --oneline HEAD..origin/main  # See what changed
   git checkout origin/main
   cd ../..
   ```

2. **Re-run discovery searches**

3. **Update YAML files:**
   * Change `analyzed_commit` to new SHA
   * Add `updated_at` field
   * Update/add new findings

4. **Verify and commit**

## Quality Checklist

Before marking a project as "comprehensive":

* [ ] `metadata.project.yaml` complete with all fields
* [ ] All CLI invocations found and documented
* [ ] All SDK usage patterns documented
* [ ] Skills/plugins support investigated
* [ ] All code snippets verified against source
* [ ] Cross-references to similar projects added
* [ ] `notes.md` with observations and comparisons
* [ ] `./scripts/verify_yamls.py` passes
* [ ] `./scripts/research_status.py --project {name}` shows good coverage

## Common Mistakes to Avoid

1. **Guessing instead of searching** - Always grep/search, don't assume
2. **Short commit hashes** - Use full 40-char SHA
3. **SSH URLs in submodules** - Use HTTPS for reproducibility
4. **Modifying snippets** - Keep verbatim, add notes separately
5. **Skipping negative findings** - Document "not found" explicitly
6. **Forgetting verification** - Always run scripts before committing
