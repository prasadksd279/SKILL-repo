# Report Processing Pipeline

A production-grade, task-delegable, fully clean modular architecture repository designed to process inputs from PostgreSQL database and structured PDFs, generating dynamically populated Excel reports using pre-designed templates and `openpyxl`.

## Features

- **Modular Architecture**: Clean separation of domain, application, and infrastructure layers
- **PostgreSQL Integration**: ORM-based database access with Alembic migrations
- **PDF Processing**: Extract data from structured PDFs using pdfplumber
- **Excel Report Generation**: Populate pre-designed Excel templates using openpyxl
- **Task Delegation**: Git worktree-based parallel execution with isolated feature branches
- **Quality Gates**: Integration testing with SonarQube quality checks
- **Interface Locking**: Immutable baseline for Pydantic data contracts

## Project Structure

```
.
├── .devin/
│   ├── mcp_config.local.json    # MCP server configuration
│   └── skills/
│       ├── report-processing/   # Master orchestrator skill
│       ├── pdf-parser/          # PDF parsing utility skill
│       ├── excel-parser/        # Excel parsing utility skill
│       └── excel-workbook-populator/  # Excel population utility skill
├── agents/                      # Sub-agent profiles
│   ├── dependency-gate.md
│   ├── interface-locker.md
│   ├── db-migration.md
│   └── integration-tester.md
├── src/
│   ├── domain/                  # Pure Pydantic models & contracts
│   │   ├── models/
│   │   └── contracts/
│   ├── application/             # Task handlers and extractors
│   │   ├── handlers/
│   │   └── extractors/
│   └── infrastructure/          # Database clients, ORM, migrations
│       ├── persistence/
│       │   ├── models/
│       │   └── migrations/
│       └── clients/
├── templates/                   # Excel report templates
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/
│   └── validate_boundaries.py  # Domain layer validation
├── references/
│   └── openpyxl_best_practices.md
├── DAG.md                       # Task dependency graph
├── PLAYBOOK.md                  # Execution playbook
├── pyproject.toml              # Python project configuration
└── README.md
```

## Prerequisites

- Python 3.11+
- PostgreSQL
- Git
- Devin CLI with MCP support
- SonarQube (optional, for quality gates)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/prasadksd279/SKILL-repo.git
cd SKILL-repo
```

### 2. Set Up Python Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

### 4. Configure PostgreSQL

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=report_processing
export DB_USER=your_user
export DB_PASSWORD=your_password
```

### 5. Run Master Orchestrator

```bash
/report-processing
```

The orchestrator will execute all phases sequentially:
- Phase 0: Repository & Skill Architecture Bootstrap
- Phase 1: Centralized Dependency Control
- Phase 2: Lock-First Interface Baseline
- Phase 3: Database & Persistence Setup
- Phase 4: Parallel Fan-Out Execution
- Phase 5: Fan-In Integration & Testing

## Documentation

- **DAG.md**: Task dependency graph and execution order
- **PLAYBOOK.md**: Detailed execution guidelines and troubleshooting
- **references/openpyxl_best_practices.md**: Excel template population rules

## Development

### Running Tests

```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Linting

```bash
ruff check .
ruff format .
```

### Domain Validation

```bash
python scripts/validate_boundaries.py
```

### Database Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Sub-Agents

### Dependency Gate Agent

Installs and validates dependencies without version conflicts.

```bash
/dependency-gate
```

### Interface Locker Agent

Defines Pydantic data contracts and commits as immutable baseline.

```bash
/interface-locker
```

### DB Migration Agent

Creates ORM models and generates linear migration scripts.

```bash
/db-migration
```

### Integration Tester Agent

Runs test suites and checks SonarQube quality gates.

```bash
/integration-tester
```

## Git Workflow

### Branch Strategy

- **main**: Production-ready code
- **staging**: Integration testing
- **feature/***: Isolated feature branches

### Git Worktree Pattern

```bash
git worktree add ../feature-task-name feature/task-name
cd ../feature-task-name
# Implement and test
cd -
git worktree remove ../feature-task-name
```

## Architecture Principles

1. **Domain Layer Purity**: No infrastructure imports in src/domain/
2. **Single Responsibility**: One file = one task
3. **Interface Locking**: Immutable baseline for data contracts
4. **Parallel Execution**: Git worktree-based isolation
5. **Quality Gates**: Automated testing and SonarQube checks

## License

MIT License

## Contributing

Please read PLAYBOOK.md for detailed contribution guidelines.
