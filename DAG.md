# Task Dependency Graph

This document defines the task dependencies and execution order for the report processing pipeline.

---

## Phase 0: Repository & Skill Architecture Bootstrap

### Tasks

#### 0.1: Create Directory Structure
- **Description:** Initialize source code skeleton (src/, templates/, tests/, scripts/, references/)
- **Status:** Phase 0 prerequisite
- **Dependencies:** None
- **Output:** Complete directory structure with __init__.py files

#### 0.2: Create Master Orchestrator Skill
- **Description:** Create `.devin/skills/report-processing/SKILL.md` with phase orchestration logic
- **Status:** Phase 0 prerequisite
- **Dependencies:** 0.1
- **Output:** Master orchestrator skill file

#### 0.3: Create Validation Script
- **Description:** Create `scripts/validate_boundaries.py` for domain layer purity checks
- **Status:** Phase 0 prerequisite
- **Dependencies:** 0.1
- **Output:** Validation script

#### 0.4: Create Excel Best Practices Reference
- **Description:** Create `references/openpyxl_best_practices.md` with template population rules
- **Status:** Phase 0 prerequisite
- **Dependencies:** 0.1
- **Output:** Excel best practices document

#### 0.5: Implement Sub-Agent Profiles
- **Description:** Implement 4 sub-agent profiles (dependency-gate, interface-locker, db-migration, integration-tester)
- **Status:** Phase 0 prerequisite
- **Dependencies:** 0.1
- **Output:** Agent profile files with complete content

#### 0.6: Create Documentation
- **Description:** Create DAG.md and PLAYBOOK.md
- **Status:** Phase 0 prerequisite
- **Dependencies:** 0.1
- **Output:** Documentation files

---

## Phase 1: Centralized Dependency Control

### Tasks

#### 1.1: Create Python Project Configuration
- **Description:** Create `pyproject.toml` with all required dependencies
- **Status:** Phase 1 prerequisite
- **Dependencies:** 0.6 (Phase 0 complete)
- **Output:** pyproject.toml file

#### 1.2: Install Dependencies
- **Description:** Spawn Dependency Gate Agent to install and lock dependencies
- **Status:** Phase 1 core task
- **Dependencies:** 1.1
- **Agent:** dependency-gate
- **Output:** Installed packages, requirements.lock

#### 1.3: Validate Dependencies
- **Description:** Verify all dependencies are installed without conflicts
- **Status:** Phase 1 validation
- **Dependencies:** 1.2
- **Output:** Dependency validation report

---

## Phase 2: Lock-First Interface Baseline

### Tasks

#### 2.1: Define Pydantic Models
- **Description:** Create Pydantic models in src/domain/models/
- **Status:** Phase 2 core task
- **Dependencies:** 1.3 (Phase 1 complete)
- **Agent:** interface-locker
- **Output:** PDFExtractedData, DBQueryResult, ReportData models

#### 2.2: Define Event Schemas
- **Description:** Create event contracts in src/domain/contracts/
- **Status:** Phase 2 core task
- **Dependencies:** 1.3
- **Agent:** interface-locker
- **Output:** DataIngestionEvent, ReportGenerationEvent schemas

#### 2.3: Validate Domain Purity
- **Description:** Run validation script to ensure no framework imports
- **Status:** Phase 2 validation
- **Dependencies:** 2.1, 2.2
- **Output:** Validation report

#### 2.4: Commit Interface Baseline
- **Description:** Commit interfaces as immutable baseline with tag
- **Status:** Phase 2 completion
- **Dependencies:** 2.3
- **Output:** Git commit, tag "interface-baseline-v1"

---

## Phase 3: Database & Persistence Setup

### Tasks

#### 3.1: Create Base Model
- **Description:** Create SQLAlchemy base model with PostgreSQL connection
- **Status:** Phase 3 core task
- **Dependencies:** 2.4 (Phase 2 complete)
- **Agent:** db-migration
- **Output:** src/infrastructure/persistence/models/base.py

#### 3.2: Create Database Models
- **Description:** Create ORM models (ReportJob, DataSource, ReportTemplate)
- **Status:** Phase 3 core task
- **Dependencies:** 3.1
- **Agent:** db-migration
- **Output:** src/infrastructure/persistence/models/database_models.py

#### 3.3: Configure Alembic
- **Description:** Set up Alembic for database migrations
- **Status:** Phase 3 core task
- **Dependencies:** 3.2
- **Agent:** db-migration
- **Output:** alembic.ini, env.py, script.py.mako

#### 3.4: Generate Initial Migration
- **Description:** Generate initial migration script with autogenerate
- **Status:** Phase 3 core task
- **Dependencies:** 3.3
- **Agent:** db-migration
- **Output:** Initial migration file

#### 3.5: Validate Migration Tree
- **Description:** Ensure migration tree is linear (no branches)
- **Status:** Phase 3 validation
- **Dependencies:** 3.4
- **Output:** Migration tree validation report

#### 3.6: Apply Migration (Optional)
- **Description:** Apply migration to database
- **Status:** Phase 3 optional
- **Dependencies:** 3.5
- **Agent:** db-migration
- **Output:** Database schema updated

---

## Phase 4: Parallel Fan-Out Execution (Task Delegation)

### Tasks (Parallelizable)

#### 4.1: PDF Extractor Implementation
- **Description:** Implement PDF parsing logic in isolated feature branch
- **Status:** Phase 4 parallel task
- **Dependencies:** 3.5 (Phase 3 complete)
- **Branch:** feature/pdf-extractor
- **Target File:** src/application/extractors/pdf_extractor.py
- **Isolation:** Git worktree
- **Verification:** Ruff check, pytest unit tests

#### 4.2: DB Extractor Implementation
- **Description:** Implement PostgreSQL data loader in isolated feature branch
- **Status:** Phase 4 parallel task
- **Dependencies:** 3.5
- **Branch:** feature/db-extractor
- **Target File:** src/application/extractors/db_extractor.py
- **Isolation:** Git worktree
- **Verification:** Ruff check, pytest unit tests

#### 4.3: Excel Populator Implementation
- **Description:** Implement Excel template population in isolated feature branch
- **Status:** Phase 4 parallel task
- **Dependencies:** 3.5
- **Branch:** feature/excel-populator
- **Target File:** src/application/handlers/excel_population_handler.py
- **Isolation:** Git worktree
- **Verification:** Ruff check, pytest unit tests

#### 4.4: PDF Extraction Handler
- **Description:** Implement PDF extraction handler in isolated feature branch
- **Status:** Phase 4 parallel task
- **Dependencies:** 3.5
- **Branch:** feature/pdf-handler
- **Target File:** src/application/handlers/pdf_extraction_handler.py
- **Isolation:** Git worktree
- **Verification:** Ruff check, pytest unit tests

#### 4.5: DB Query Handler
- **Description:** Implement DB query handler in isolated feature branch
- **Status:** Phase 4 parallel task
- **Dependencies:** 3.5
- **Branch:** feature/db-handler
- **Target File:** src/application/handlers/db_query_handler.py
- **Isolation:** Git worktree
- **Verification:** Ruff check, pytest unit tests

### Parallel Execution Notes

- All Phase 4 tasks (4.1-4.5) can run in parallel using git worktrees
- Each task runs in an isolated branch
- Each task must pass linting and tests before completion
- Tasks can communicate through shared domain models

---

## Phase 5: Fan-In Integration, Smoke Testing, & Clean Merge

### Tasks

#### 5.1: Merge Feature Branches to Staging
- **Description:** Sequentially merge all feature branches to staging
- **Status:** Phase 5 integration
- **Dependencies:** All Phase 4 tasks complete
- **Branch:** staging
- **Output:** Merged code in staging branch

#### 5.2: Run Integration Tests
- **Description:** Spawn Integration Tester Agent to run full test suite
- **Status:** Phase 5 validation
- **Dependencies:** 5.1
- **Agent:** integration-tester
- **Output:** Test results, coverage report

#### 5.3: Query SonarQube Quality Gates
- **Description:** Check SonarQube quality gates via MCP tools
- **Status:** Phase 5 validation
- **Dependencies:** 5.2
- **Agent:** integration-tester
- **Output:** Quality gate status, code quality metrics

#### 5.4: Check Contract Drift
- **Description:** Verify no unexpected changes to domain contracts
- **Status:** Phase 5 validation
- **Dependencies:** 5.2
- **Agent:** integration-tester
- **Output:** Contract drift report

#### 5.5: Resolve Conflicts
- **Description:** Spawn Merger Sub-Agent to resolve any git conflicts
- **Status:** Phase 5 conflict resolution
- **Dependencies:** 5.1
- **Agent:** merger
- **Output:** Conflict-free staging branch

#### 5.6: Merge Staging to Main
- **Description:** Final clean merge to main branch
- **Status:** Phase 5 completion
- **Dependencies:** 5.2, 5.3, 5.4, 5.5
- **Branch:** main
- **Output:** Updated main branch

---

## Dependency Graph Visualization

```
Phase 0:
  0.1 (Directory Structure)
    ├─→ 0.2 (Master Orchestrator)
    ├─→ 0.3 (Validation Script)
    ├─→ 0.4 (Excel Best Practices)
    ├─→ 0.5 (Sub-Agent Profiles)
    └─→ 0.6 (Documentation)

Phase 1:
  0.6 ──→ 1.1 (pyproject.toml) ──→ 1.2 (Install Dependencies) ──→ 1.3 (Validate)

Phase 2:
  1.3 ──→ 2.1 (Pydantic Models) ──┐
                                ├─→ 2.3 (Validate) ──→ 2.4 (Commit Baseline)
  1.3 ──→ 2.2 (Event Schemas) ──┘

Phase 3:
  2.4 ──→ 3.1 (Base Model) ──→ 3.2 (DB Models) ──→ 3.3 (Alembic) ──→ 3.4 (Migration) ──→ 3.5 (Validate)
                                                               └─→ 3.6 (Apply - Optional)

Phase 4 (Parallel):
  3.5 ──┬─→ 4.1 (PDF Extractor)
       ├─→ 4.2 (DB Extractor)
       ├─→ 4.3 (Excel Populator)
       ├─→ 4.4 (PDF Handler)
       └─→ 4.5 (DB Handler)

Phase 5:
  All 4.x ──→ 5.1 (Merge to Staging) ──┬─→ 5.2 (Integration Tests)
                                       ├─→ 5.3 (SonarQube)
                                       ├─→ 5.4 (Contract Drift)
                                       └─→ 5.5 (Resolve Conflicts)
                                    └─→ 5.6 (Merge to Main)
```

---

## Critical Path

The critical path (sequential dependencies) is:
```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 5
```

Phase 4 is the only phase with parallelizable tasks.

---

## Branch Strategy

### Main Branch
- Production-ready code
- Only receives merges from staging

### Staging Branch
- Integration testing
- Receives merges from feature branches
- Only merges to main after validation

### Feature Branches
- `feature/pdf-extractor`
- `feature/db-extractor`
- `feature/excel-populator`
- `feature/pdf-handler`
- `feature/db-handler`
- Created via git worktree
- Merged to staging after validation

---

## Git Worktree Pattern

For each Phase 4 task:
```bash
# Create worktree
git worktree add ../feature-task-name feature/task-name

# Work in isolated environment
cd ../feature-task-name
# Implement and test
ruff check .
pytest tests/

# Return to main
cd -

# Merge to staging
git checkout staging
git merge feature/task-name

# Clean up worktree
git worktree remove ../feature-task-name
git branch -D feature/task-name
```

---

## Execution Order Summary

1. **Phase 0** (Sequential): Build foundation
2. **Phase 1** (Sequential): Install dependencies
3. **Phase 2** (Sequential): Lock interfaces
4. **Phase 3** (Sequential): Setup database
5. **Phase 4** (Parallel): Implement handlers (can run simultaneously)
6. **Phase 5** (Sequential): Integrate and test

---

## Success Criteria

- Phase 0: All skills and profiles created, directory structure complete
- Phase 1: Dependencies installed without conflicts, lockfile generated
- Phase 2: Interfaces defined, committed, tagged, validation passes
- Phase 3: ORM models created, migrations generated, tree is linear
- Phase 4: All feature branches pass linting and tests
- Phase 5: All tests pass, quality gates green, clean merge to main
