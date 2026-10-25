# Execution Playbook

This document provides execution guidelines, workflows, and troubleshooting instructions for the report processing pipeline.

---

## Quick Start

### Prerequisites

- **Python 3.11+** installed
- **PostgreSQL** installed and running
- **Git** installed and configured
- **Dev CLI** with MCP support
- **SonarQube** (optional, for quality gates)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/prasadksd279/shared-skills-repo.git
   cd shared-skills-repo
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Configure PostgreSQL:**
   ```bash
   # Set environment variables
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=report_processing
   export DB_USER=your_user
   export DB_PASSWORD=your_password
   ```

4. **Invoke Master Orchestrator:**
   ```bash
   /report-processing
   ```

The orchestrator will execute all phases sequentially and report progress.

---

## Phase-by-Phase Instructions

### Phase 0: Repository & Skill Architecture Bootstrap

**Goal:** Build the foundational structure before executing any application logic.

**Steps:**

1. **Verify directory structure:**
   ```bash
   ls -la src/
   ls -la src/domain/
   ls -la src/application/
   ls -la src/infrastructure/
   ```

2. **Verify master orchestrator skill:**
   ```bash
   /report-processing --help
   ```

3. **Test validation script:**
   ```bash
   python scripts/validate_boundaries.py
   ```
   Expected: "✅ PASSED: No boundary violations found"

4. **Verify sub-agent profiles:**
   ```bash
   ls -la agents/
   ```
   Should show: dependency-gate.md, interface-locker.md, db-migration.md, integration-tester.md

5. **Verify documentation:**
   ```bash
   cat DAG.md
   cat PLAYBOOK.md
   ```

**Success Criteria:**
- All directories exist with __init__.py files
- Master orchestrator skill is discoverable
- Validation script runs without errors
- All 4 agent profiles have content
- DAG.md and PLAYBOOK.md are complete

**Troubleshooting:**
- If validation fails: Check for forbidden imports in src/domain/
- If skill not discoverable: Check SKILL.md frontmatter syntax
- If directories missing: Run Phase 0 again

---

### Phase 1: Centralized Dependency Control

**Goal:** Install required dependencies cleanly without version conflicts.

**Steps:**

1. **Check pyproject.toml:**
   ```bash
   cat pyproject.toml
   ```

2. **Invoke Dependency Gate Agent:**
   ```bash
   /dependency-gate
   ```

3. **Verify installation:**
   ```bash
   pip list | grep -E "openpyxl|pdfplumber|sqlalchemy|alembic|pydantic|psycopg2|pytest|ruff"
   ```

4. **Check lockfile:**
   ```bash
   cat requirements.lock
   ```

5. **Validate dependencies:**
   ```bash
   pip check
   ```

**Success Criteria:**
- All required packages installed
- No version conflicts
- requirements.lock generated
- pip check passes

**Troubleshooting:**
- If conflicts: Use pip-tools for advanced dependency resolution
- If package not found: Check package name in pyproject.toml
- If network error: Check proxy settings or try different package index

---

### Phase 2: Lock-First Interface Baseline

**Goal:** Define pure Pydantic data contracts and commit as immutable baseline.

**Steps:**

1. **Invoke Interface Locker Agent:**
   ```bash
   /interface-locker
   ```

2. **Verify models created:**
   ```bash
   ls -la src/domain/models/
   ```
   Should show: pdf_extracted_data.py, db_query_result.py, report_data.py

3. **Verify event schemas created:**
   ```bash
   ls -la src/domain/contracts/
   ```
   Should show: data_ingestion_event.py, report_generation_event.py

4. **Run validation:**
   ```bash
   python scripts/validate_boundaries.py
   ```

5. **Verify git commit:**
   ```bash
   git log --oneline -1
   git tag
   ```
   Should show commit message "Interface baseline locked" and tag "interface-baseline-v1"

**Success Criteria:**
- All Pydantic models created
- All event schemas created
- Validation passes
- Git commit with baseline message
- Git tag interface-baseline-v1 exists

**Troubleshooting:**
- If validation fails: Remove forbidden imports from domain layer
- If git commit fails: Check git status, ensure working directory is clean
- If models missing: Re-run interface-locker agent

---

### Phase 3: Database & Persistence Setup

**Goal:** Establish ORM models for PostgreSQL and generate linear migration scripts.

**Steps:**

1. **Set DATABASE_URL:**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
   ```

2. **Invoke DB Migration Agent:**
   ```bash
   /db-migration
   ```

3. **Verify models created:**
   ```bash
   ls -la src/infrastructure/persistence/models/
   ```
   Should show: base.py, database_models.py

4. **Verify Alembic configuration:**
   ```bash
   ls -la alembic.ini
   ls -la src/infrastructure/persistence/migrations/
   ```

5. **Check migration:**
   ```bash
   alembic current
   alembic history
   ```

6. **Apply migration (optional):**
   ```bash
   alembic upgrade head
   ```

**Success Criteria:**
- Base model created with PostgreSQL connection
- Database models created (ReportJob, DataSource, ReportTemplate)
- Alembic configured
- Initial migration generated
- Migration tree is linear
- Migration applied to database (if optional step taken)

**Troubleshooting:**
- If connection fails: Verify PostgreSQL is running, check credentials
- If migration not generated: Check DATABASE_URL, verify models are importable
- If migration tree branched: Check alembic history, resolve conflicts
- If autogenerate fails: Ensure models are properly defined with SQLAlchemy

---

### Phase 4: Parallel Fan-Out Execution (Task Delegation)

**Goal:** Implement extractors and handlers in isolated feature branches using git worktrees.

**Steps for Each Task:**

1. **Create worktree:**
   ```bash
   git worktree add ../feature-task-name feature/task-name
   cd ../feature-task-name
   ```

2. **Implement task:**
   - Write code in target file
   - Follow single-responsibility principle
   - Use domain models from src/domain/
   - Import infrastructure from src/infrastructure/

3. **Run linting:**
   ```bash
   ruff check .
   ruff format .
   ```

4. **Run tests:**
   ```bash
   pytest tests/unit/ -v
   ```

5. **Return to main:**
   ```bash
   cd -
   ```

6. **Merge to staging:**
   ```bash
   git checkout staging
   git merge feature/task-name
   ```

7. **Clean up:**
   ```bash
   git worktree remove ../feature-task-name
   git branch -D feature/task-name
   ```

**Parallel Execution:**

All Phase 4 tasks can run simultaneously in separate worktrees:
- feature/pdf-extractor
- feature/db-extractor
- feature/excel-populator
- feature/pdf-handler
- feature/db-handler

**Success Criteria:**
- Each feature branch passes linting
- Each feature branch passes unit tests
- All branches merged to staging
- No conflicts in staging

**Troubleshooting:**
- If worktree creation fails: Check git version, ensure no duplicate worktrees
- If linting fails: Fix style issues, run ruff format
- If tests fail: Fix failing tests, ensure proper mocking
- If merge conflicts: Resolve manually or use merger agent

---

### Phase 5: Fan-In Integration, Smoke Testing, & Clean Merge

**Goal:** Merge feature branches, run integration tests, check quality gates, and merge to main.

**Steps:**

1. **Ensure all Phase 4 tasks complete:**
   ```bash
   git branch -a
   git log staging --oneline
   ```

2. **Invoke Integration Tester Agent:**
   ```bash
   /integration-tester
   ```

3. **Review test results:**
   - Unit tests: Should all pass
   - Integration tests: Should all pass
   - Code coverage: Should be >= 80%
   - SonarQube: Should be green (if configured)

4. **Check contract drift:**
   ```bash
   git diff interface-baseline-v1 src/domain/
   ```
   Review any changes to domain models/contracts

5. **Resolve conflicts (if any):**
   ```bash
   /merger
   ```

6. **Merge staging to main:**
   ```bash
   git checkout main
   git merge staging
   ```

7. **Tag release:**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   ```

8. **Push to remote:**
   ```bash
   git push origin main
   git push origin --tags
   ```

**Success Criteria:**
- All tests pass
- Code coverage >= 80%
- SonarQube quality gates green (if configured)
- No contract drift or drift is approved
- Clean merge to main
- Release tag created
- Changes pushed to remote

**Troubleshooting:**
- If tests fail: Review error logs, fix issues, re-run tests
- If quality gates fail: Fix code smells, improve coverage, re-run
- If contract drift: Review changes, approve if intentional, update baseline
- If merge conflicts: Resolve conflicts, verify tests pass, retry merge

---

## Sub-Agent Invocation Patterns

### Dependency Gate Agent

**Invocation:**
```bash
/dependency-gate
```

**Input:** Reads pyproject.toml or requirements.txt

**Output:**
- Installed packages
- requirements.lock
- Validation report

**Exit Codes:**
- 0: Success
- 1: Conflict
- 2: Missing

---

### Interface Locker Agent

**Invocation:**
```bash
/interface-locker
```

**Input:** Reads specification files

**Output:**
- Pydantic models in src/domain/models/
- Event schemas in src/domain/contracts/
- Git commit with baseline tag

**Exit Codes:**
- 0: Success
- 1: Validation failed
- 2: Error

---

### DB Migration Agent

**Invocation:**
```bash
/db-migration
```

**Input:** DATABASE_URL environment variable

**Output:**
- ORM models in src/infrastructure/persistence/models/
- Alembic configuration
- Migration scripts

**Exit Codes:**
- 0: Success
- 1: Migration conflict
- 2: Error

---

### Integration Tester Agent

**Invocation:**
```bash
/integration-tester
```

**Input:** Test files, SonarQube MCP (if configured)

**Output:**
- Test results
- Coverage report
- Quality gate status
- Contract drift report

**Exit Codes:**
- 0: Success
- 1: Test failure
- 2: Quality gate failure
- 3: Contract drift
- 4: Validation failed

---

## Git Workflow Documentation

### Branch Strategy

**Main Branch:**
- Production-ready code
- Protected, only receives merges from staging
- Tags for releases (v1.0.0, v1.1.0, etc.)

**Staging Branch:**
- Integration testing
- Receives merges from feature branches
- Only merges to main after validation
- Can be force-reset if needed

**Feature Branches:**
- `feature/<task-name>`
- Created via git worktree
- Isolated development environment
- Merged to staging after validation
- Deleted after merge

### Git Worktree Usage

**Create worktree:**
```bash
git worktree add ../feature-task-name feature/task-name
```

**List worktrees:**
```bash
git worktree list
```

**Remove worktree:**
```bash
git worktree remove ../feature-task-name
```

**Clean up orphaned worktrees:**
```bash
git worktree prune
```

### Merge Patterns

**Feature to Staging:**
```bash
git checkout staging
git merge feature/task-name --no-ff
```

**Staging to Main:**
```bash
git checkout main
git merge staging --no-ff
```

**Resolve Conflicts:**
```bash
git checkout main
git merge staging
# Resolve conflicts manually
git add .
git commit
```

---

## Troubleshooting Guide

### Dependency Issues

**Problem:** Version conflicts during installation

**Solution:**
```bash
pip install --upgrade pip
pip install pip-tools
pip-compile pyproject.toml
pip install -r requirements.txt
```

**Problem:** Package not found

**Solution:**
- Check package name spelling
- Verify package index is accessible
- Try with `--extra-index-url`

---

### Database Issues

**Problem:** PostgreSQL connection refused

**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string
echo $DATABASE_URL

# Test connection manually
psql $DATABASE_URL
```

**Problem:** Migration fails

**Solution:**
```bash
# Check current migration
alembic current

# Check migration history
alembic history

# Stamp head if needed
alembic stamp head
```

---

### Validation Issues

**Problem:** Domain layer validation fails

**Solution:**
```bash
# Run validation with details
python scripts/validate_boundaries.py

# Check for forbidden imports
grep -r "sqlalchemy" src/domain/
grep -r "openpyxl" src/domain/
```

**Problem:** Pydantic model validation fails

**Solution:**
- Check field types match
- Verify required fields are present
- Check for circular references

---

### Git Issues

**Problem:** Worktree creation fails

**Solution:**
```bash
# Clean up existing worktrees
git worktree prune

# Remove conflicting branches
git branch -D feature/task-name

# Retry worktree creation
git worktree add ../feature-task-name feature/task-name
```

**Problem:** Merge conflicts

**Solution:**
```bash
# Use merger agent
/merger

# Or resolve manually
git checkout main
git merge staging
# Edit conflicted files
git add .
git commit
```

---

### Test Issues

**Problem:** Tests fail in CI but pass locally

**Solution:**
- Check environment variables
- Verify database connection
- Check for hardcoded paths
- Ensure all dependencies are installed

**Problem:** Coverage is low

**Solution:**
- Add tests for critical paths
- Test edge cases
- Increase integration test coverage
- Use mocking for external dependencies

---

### SonarQube Issues

**Problem:** SonarQube MCP not available

**Solution:**
```bash
# Check MCP configuration
cat .devin/mcp_config.json

# Add SonarQube MCP if missing
devin mcp add sonarqube <url>
```

**Problem:** Quality gate fails

**Solution:**
- Review SonarQube dashboard
- Fix critical issues first
- Improve code coverage
- Reduce code smells
- Re-run analysis after fixes

---

## SonarQube Integration

### Configuration

**Add SonarQube MCP server:**
```bash
devin mcp add sonarqube http://sonarqube-server:9000
```

**Configure in .devin/mcp_config.json:**
```json
{
  "mcpServers": {
    "sonarqube": {
      "url": "http://sonarqube-server:9000",
      "transport": "http"
    }
  }
}
```

### Quality Gate Criteria

**Required:**
- Code coverage >= 80%
- No critical vulnerabilities
- No blocker issues
- Maintainability rating >= A

**Recommended:**
- Code smells < threshold
- Duplicated lines density < 5%
- Reliability rating >= A
- Security rating >= A

### Querying SonarQube

**Get quality gate status:**
```python
mcp_call_tool(
    server_name="sonarqube",
    tool_name="get_quality_gate",
    arguments={"project_key": "report-processing"}
)
```

**Get issues:**
```python
mcp_call_tool(
    server_name="sonarqube",
    tool_name="get_issues",
    arguments={
        "project_key": "report-processing",
        "severities": ["CRITICAL", "MAJOR"]
    }
)
```

**Get measures:**
```python
mcp_call_tool(
    server_name="sonarqube",
    tool_name="get_measures",
    arguments={
        "project_key": "report-processing",
        "metrics": ["coverage", "complexity", "duplicated_lines_density"]
    }
)
```

---

## Continuous Integration

### CI/CD Pipeline

**Recommended CI steps:**
1. Checkout code
2. Set up Python environment
3. Install dependencies
4. Run linting (ruff)
5. Run unit tests (pytest)
6. Run integration tests (pytest)
7. Check domain validation
8. Query SonarQube quality gates
9. Build artifacts
10. Deploy if all checks pass

### GitHub Actions Example

```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.lock
      - name: Run linting
        run: ruff check src/
      - name: Run tests
        run: pytest tests/ -v --cov=src
      - name: Validate domain
        run: python scripts/validate_boundaries.py
```

---

## Performance Optimization

### Database Optimization

**Use connection pooling:**
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

**Use batch inserts:**
```python
session.bulk_insert_mappings(Model, data_list)
```

### Excel Optimization

**Use write_only mode for large datasets:**
```python
wb = Workbook(write_only=True)
ws = wb.create_sheet()
```

**Minimize cell access:**
```python
# Bad
for i in range(1000):
    sheet[f'A{i}'].value = data[i]

# Good
for row in sheet.iter_rows():
    for cell in row:
        cell.value = get_value(cell)
```

### PDF Optimization

**Process pages in parallel:**
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(extract_page, pages)
```

---

## Security Best Practices

### Environment Variables

**Never commit secrets:**
```bash
# Add to .gitignore
.env
*.key
*.pem
```

**Use environment variables:**
```python
import os

DB_PASSWORD = os.getenv("DB_PASSWORD")
```

### Database Security

**Use SSL connections:**
```python
DATABASE_URL = "postgresql://user:password@host:5432/dbname?sslmode=require"
```

**Use least privilege:**
- Create dedicated database user for application
- Grant only necessary permissions
- Rotate credentials regularly

### Input Validation

**Validate all inputs:**
```python
from pydantic import BaseModel, validator

class DataModel(BaseModel):
    field: str

    @validator('field')
    def validate_field(cls, v):
        if not v:
            raise ValueError('Field cannot be empty')
        return v
```

---

## Monitoring and Logging

### Logging Configuration

**Set up logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring Metrics

**Track:**
- Report generation time
- Database query performance
- PDF extraction time
- Excel population time
- Error rates

---

## Backup and Recovery

### Database Backups

**Regular backups:**
```bash
pg_dump dbname > backup.sql
```

**Automated backups:**
```bash
# Cron job
0 2 * * * pg_dump dbname > /backups/dbname_$(date +\%Y\%m\%d).sql
```

### Template Backups

**Version control:**
- Keep Excel templates in git
- Tag template versions
- Document template changes

---

## Appendix

### Useful Commands

**Git:**
```bash
git status
git log --oneline
git branch -a
git worktree list
```

**Python:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip freeze
```

**PostgreSQL:**
```bash
psql -U user -d dbname
pg_dump dbname > backup.sql
psql dbname < backup.sql
```

**Testing:**
```bash
pytest tests/ -v
pytest tests/ --cov=src
pytest tests/ -k "test_name"
```

**Linting:**
```bash
ruff check .
ruff format .
ruff check --fix .
```

**Alembic:**
```bash
alembic current
alembic history
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
```

### Contact and Support

For issues or questions:
- Check this playbook first
- Review DAG.md for task dependencies
- Check agent documentation in agents/
- Review openpyxl best practices in references/

### Version History

- v1.0.0 - Initial playbook creation
