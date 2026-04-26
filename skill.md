# Project Skill: jira-reviewspec

This document defines the operational standards, principles, and mandatory practices for the `jira-reviewspec` project.

---

## 📖 Mandatory Pre-Session Reading

Before starting **ANY** task, AI must read:

1. ✅ [README.md](README.md) — Project overview, setup, API contracts
2. ✅ Latest 3 files in `/agent-history/` — Recent decisions and context
3. ✅ Project structure — Folder layout, existing patterns, conventions

---

## 🧠 Core Principles

- **Always produce runnable, complete solution** — No partial snippets unless explicitly requested
- **Zero errors** — No lint errors, no build errors, no runtime errors
- **Self-consistent code** — All imports resolved, types consistent, dependencies explicit
- **Simplicity over cleverness** — Prefer readable, maintainable solutions
- **No hidden assumptions** — Always infer context from project structure and existing code

---

## 📁 Project Structure Awareness

AI must:

- ✅ Read existing folder structure before coding
- ✅ Follow existing patterns (naming, architecture, file organization, conventions)
- ✅ Do not introduce new patterns unless explicitly justified

---

## 🧾 Mandatory Task Completion Rules

Every task MUST pass ALL of these checks before marking complete:

1. ✅ **Build passes** — `pytest` runs successfully (or build tool for your language)
2. ✅ **No lint errors** — Run `ruff check` and `ruff format` for Python
3. ✅ **No runtime errors** — Basic execution sanity check passed
4. ✅ **All imports resolved** — No missing dependencies or incorrect imports
5. ✅ **No dead code** — Remove unused variables, functions, imports

---

## 🪵 Agent History Logging

**After EVERY completed task**, AI must create a file:

```bash
/{project}/agent-history/YYMMDD-HHMMSS-{topic}.md
```

Example: `260426-143022-implement-orchestrator.md`

Content must include:

```markdown
# Task: [Topic]

## ✅ Task Summary
[Brief summary of what was done and why]

## 📂 Files Changed
- file1.py → reason
- file2.py → reason

## ⚙️ How to Run / Test
[Commands to verify the work]

## 🧠 Key Decisions
- Decision 1 → rationale
- Decision 2 → rationale

## ⚠️ Notes / Limitations
- Limitation 1
- Known issue 1

## 📘 README Update (if any)
[What was added/changed in README]

## 🔗 Related Issues / Context
- Links to previous tasks or tickets
```

---

## 📘 README Synchronization Rule

AI must update [README.md](README.md) IF any of these occur:

- ✅ New feature added
- ✅ New environment variable introduced
- ✅ Setup steps changed
- ✅ API contract changed
- ✅ Architecture changed

---

## 🧱 Output Format Rule

When reporting task completion, use this structure:

```markdown
## ✅ Task Summary
(What was accomplished)

## 📂 Files Changed
- file1.py → reason
- file2.py → reason

## ⚙️ How to Run
(Commands to test)

## 🧠 Key Decisions
(Why this approach)

## ⚠️ Notes / Limitations
(Trade-offs, known issues)

## 📘 README Update
(If applicable)

## 🪵 Agent History File
/{project}/agent-history/YYMMDD-HHMMSS-{topic}.md
```

---

## 🐍 Python Code Quality Standards

### Error Prevention (Must-Haves)

- ✅ No Python syntax errors (verify with `ruff check`)
- ✅ No build/runtime errors (`pytest` must pass)
- ✅ No missing imports (all dependencies explicit)
- ✅ Type hints on all functions and classes
- ✅ No console.log (use proper logging module)

### Best Practices

- ✅ Use type hints (Python 3.8+)
- ✅ Follow PEP 8 (use `ruff format` for auto-formatting)
- ✅ Keep functions small and focused (single responsibility)
- ✅ Use descriptive variable and function names
- ✅ Handle edge cases gracefully
- ✅ Prefer composition over inheritance

### Performance

- ✅ Avoid unnecessary loops
- ✅ Cache expensive operations where appropriate
- ✅ Use generators for large data streams
- ✅ Profile before over-optimizing

### Security

- ✅ Sanitize all user inputs
- ✅ Use environment variables for secrets (NEVER hardcode API keys)
- ✅ Validate data at API boundaries
- ✅ Use parameterized queries (prevent SQL injection)
- ✅ Handle sensitive data carefully (no logging passwords/tokens)

---

## 🛠 Core Responsibilities

- **Mandatory Context**: Always read this `skill.md` and project rules at the start of every session
- **Validation First**: Before completing any task:
  - Check for errors (`ruff check`, `pytest`)
  - Verify imports and type consistency
  - Run basic execution sanity check
- **Documentation**: Keep [README.md](README.md) and this document up-to-date
- **Log Everything**: Create agent history file after each task (see "Agent History Logging" above)

---

## 📋 Checklists

### Before Starting a Task

- [ ] Read README.md
- [ ] Review latest 3 files in `/agent-history/`
- [ ] Understand project structure and existing patterns
- [ ] Identify related files and dependencies

### Before Submitting a Task

- [ ] Run `pytest` — all tests pass
- [ ] Run `ruff check` — no lint errors
- [ ] Run `ruff format` — code is formatted
- [ ] All imports are correct and resolved
- [ ] No dead code or unused variables
- [ ] Code is self-consistent (types, naming, style)

### After Task Completion

- [ ] Create agent history file with required sections
- [ ] Update README.md if needed (new features, env vars, setup changes)
- [ ] Commit/save changes
- [ ] Summarize work clearly
