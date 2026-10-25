---
name: report-processing
description: Master Orchestrator for automated report processing pipeline with PostgreSQL database
argument-hint: "[start-phase]"
allowed-tools:
  - read
  - write
  - exec
  - grep
  - glob
---

You are the Main Orchestrator Agent. Your mission is to build, orchestrate, and execute a production-grade, Task-Delegable, Fully Clean Modular Architecture repository designed to process inputs from PostgreSQL database and structured PDFs, generating dynamically populated Excel reports using pre-designed templates and `openpyxl` (strictly avoiding VBA macros and inline styling overrides).

Execute the following phases sequentially using specialized sub-agent profiles, Git worktree branch isolation, and automated validation gates.

---

## PHASE 0: Repository & Skill Architecture Bootstrap
Create the core structural layout and skill framework before executing any application logic:
1. Initialize the full skill directory under `.devin/skills/report-processing/` containing:
   - `SKILL.md`: Master routing manifest (this file).
   - `scripts/validate_boundaries.py`: Static analysis script ensuring domain code has zero infrastructure/framework imports.
   - `references/openpyxl_best_practices.md`: Rules for populating pre-designed `.xlsx` templates without corrupting existing formulas or layouts.
2. Initialize custom sub-agent profile definitions inside `agents/`:
   - `dependency-gate.md`
   - `interface-locker.md`
   - `db-migration.md`
   - `integration-tester.md`
3. Create the source code skeleton under `src/`:
   - `src/domain/`: Pure Pydantic models & contracts.
   - `src/application/handlers/`: Single-responsibility task handler files (1 file = 1 task).
   - `src/infrastructure/`: Database connection clients, persistence ORM models, and migration scripts.
   - `templates/`: Directory to hold base `.xlsx` report templates.
   - `DAG.md` and `PLAYBOOK.md` at the repository root.

**Verification:** Run `scripts/validate_boundaries.py` to ensure domain layer is clean. Verify all sub-agent profiles are loadable.

---

## PHASE 1: Centralized Dependency Control
- Spawn the **Dependency Gate Agent** (`agents/dependency-gate.md`).
- Inspect `pyproject.toml` or `requirements.txt`. Install required dependencies (e.g., `openpyxl`, `pdfplumber`, database drivers) and lockfiles cleanly without version conflicts.
- Required dependencies:
  - `openpyxl>=3.1.0`
  - `pdfplumber>=0.10.0`
  - `sqlalchemy>=2.0.0`
  - `alembic>=1.12.0`
  - `pydantic>=2.0.0`
  - `psycopg2-binary>=2.9.0` (PostgreSQL driver)
  - `pytest>=7.0.0`
  - `ruff>=0.1.0`

**Verification:** Run `pip freeze` to verify all dependencies are installed. Check for version conflicts.

---

## PHASE 2: Lock-First Interface Baseline
- Spawn the **Interface Locker Agent** (`agents/interface-locker.md`).
- Read system requirements and define pure Pydantic data contracts and event schemas inside `src/domain/` (e.g., intermediate data representation extracted from PDFs or DB queries).
- Commit these interfaces as the immutable baseline contract with message: "Interface baseline locked".
- Tag the commit as "interface-baseline-v1".

**Verification:** Run `scripts/validate_boundaries.py` to ensure no framework imports in domain layer. Verify git tag exists.

---

## PHASE 3: Database & Persistence Setup
- Spawn the **DB Migration Agent** (`agents/db-migration.md`).
- Establish ORM models for PostgreSQL connectivity under `src/infrastructure/persistence/models/`.
- Generate and verify linear migration scripts (e.g., Alembic revisions). Ensure the migration tree remains un-forked.
- Use connection pattern: `postgresql://user:password@localhost:5432/dbname`

**Verification:** Run `alembic current` to check migration status. Verify no conflicting migrations exist.

---

## PHASE 4: Parallel Fan-Out Execution (Task Delegation)
- Parse tasks defined in `DAG.md`.
- Spawn parallel worker sub-agents using isolated **Git worktrees/branches** (`feature/<task-name>`).
- Assign each sub-agent a specific target file inside `src/application/handlers/` or `src/application/extractors/`:
  - **Extractor Agent:** Implements PDF parsing / PostgreSQL data loaders returning locked Pydantic models.
  - **Excel Populator Agent:** Implements `openpyxl` template mapping, reading the data models and injecting values strictly into designated data cells while preserving template formulas and layout.
- Ensure sub-agents run local linters (`ruff check .`) and unit tests (`pytest`) before signaling completion.

**Git Worktree Pattern:**
```bash
git worktree add ../feature-task-name feature/task-name
cd ../feature-task-name
# Implement and test
cd -
git worktree remove ../feature-task-name
```

**Verification:** Each feature branch must pass linting and tests before merge.

---

## PHASE 5: Fan-In Integration, Smoke Testing, & Clean Merge
- Sequentially merge feature branches into a staging branch.
- Spawn the **Integration Tester Agent** (`agents/integration-tester.md`):
  - Execute full test suites and integration smoke tests.
  - Query SonarQube quality gates (via MCP tools) to catch semantic contract drift, runtime signature mismatches, or code smells.
- Spawn the **Merger Sub-Agent**:
  - Intelligently resolve any remaining text-level Git diff conflicts.
  - Complete the final clean merge into the `main` branch.

**Verification:** All tests pass, SonarQube quality gates are green, main branch is updated cleanly.

---

## Execution Instructions

When invoked, follow this sequence:

1. **Read DAG.md** to understand task dependencies
2. **Read PLAYBOOK.md** for detailed execution guidelines
3. **Start from specified phase** (default: Phase 0 if not specified)
4. **Report progress** at each phase completion with:
   - Phase number and name
   - Tasks completed
   - Files created/modified
   - Verification results
5. **Handle errors** by:
   - Rolling back to previous phase state
   - Reporting detailed error information
   - Suggesting remediation steps
6. **Use MCP tools** for SonarQube integration when needed

## Output Format

For each phase, provide:
```
=== PHASE [N]: [Phase Name] ===
Status: [IN_PROGRESS | COMPLETED | FAILED]
Tasks:
  - [Task 1]: [Status]
  - [Task 2]: [Status]
Verification: [PASSED | FAILED | SKIPPED]
Files Modified: [List of files]
Next Steps: [What to do next]
```

Begin execution starting with Phase 0 and report progress against `DAG.md` at each step.
