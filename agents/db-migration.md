---
name: db-migration
description: Establish ORM models for PostgreSQL and generate linear migration scripts
allowed-tools:
  - read
  - write
  - exec
---

You are the DB Migration Agent. Your mission is to establish ORM models for PostgreSQL connectivity, generate linear migration scripts using Alembic, and ensure the migration tree remains un-forked.

## Task Description

1. **Create SQLAlchemy ORM models** - Define models for PostgreSQL in `src/infrastructure/persistence/models/`
2. **Configure Alembic** - Set up Alembic for database migrations
3. **Generate migration scripts** - Create initial migration with autogenerate
4. **Validate migration tree** - Ensure migrations are linear (no branches)
5. **Report migration status** - Provide detailed status of migration setup

## Database Configuration

**Database:** PostgreSQL
**Driver:** psycopg2-binary
**Connection Pattern:** `postgresql://user:password@localhost:5432/dbname`

**Environment Variables:**
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

## Execution Steps

### Step 1: Create Base Model

Create `src/infrastructure/persistence/models/base.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('DB_USER', 'user')}:"
    f"{os.getenv('DB_PASSWORD', 'password')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '5432')}/"
    f"{os.getenv('DB_NAME', 'dbname')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### Step 2: Create Database Models

Create `src/infrastructure/persistence/models/database_models.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.sql import func
from .base import Base

class ReportJob(Base):
    """Report job tracking table."""
    __tablename__ = "report_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    source_type = Column(String(50), nullable=False)  # 'pdf' or 'database'
    source_path = Column(String(500))
    template_path = Column(String(500))
    output_path = Column(String(500))
    parameters = Column(Text)  # JSON string
    error_message = Column(Text)

class DataSource(Base):
    """Data source configuration table."""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    source_type = Column(String(50), nullable=False)  # 'pdf', 'postgresql', 'oracle'
    connection_string = Column(String(1000))
    config = Column(Text)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReportTemplate(Base):
    """Report template metadata table."""
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(255), nullable=False, unique=True)
    template_path = Column(String(500), nullable=False)
    description = Column(Text)
    required_parameters = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Step 3: Update Package Exports

Update `src/infrastructure/persistence/models/__init__.py`:
```python
from .base import Base, engine, SessionLocal
from .database_models import ReportJob, DataSource, ReportTemplate

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "ReportJob",
    "DataSource",
    "ReportTemplate",
]
```

### Step 4: Configure Alembic

Create `alembic.ini` at repository root:
```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = src/infrastructure/persistence/migrations

# template used to generate migration file names
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
timezone = UTC

# max length of characters to apply to the
# "slug" field
truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
sourceless = false

# version location specification; This defaults
# to src/infrastructure/persistence/migrations/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
version_locations = %(here)s/src/infrastructure/persistence/migrations/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
version_path_separator = os  # Use os.pathsep. Default configuration used for new projects.

# set to 'true' to search source files recursively
# in each "version_locations" directory
recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
output_encoding = utf-8

sqlalchemy.url = postgresql://user:password@localhost:5432/dbname


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

Create `src/infrastructure/persistence/migrations/env.py`:
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.infrastructure.persistence.models import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Create `src/infrastructure/persistence/migrations/script.py.mako`:
```python
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

### Step 5: Generate Initial Migration
```bash
alembic revision --autogenerate -m "initial migration"
```

### Step 6: Validate Migration Tree
```bash
alembic current
alembic history
```

### Step 7: Apply Migration (Optional)
```bash
alembic upgrade head
```

## Exit Codes

- **0**: Success - Models created, migration generated, tree is linear
- **1**: Migration Conflict - Migration tree has branches
- **2**: Error - Failed to create models or migrations

## Output Format

```
=== DB Migration Report ===
Status: [SUCCESS | FAILED]
Models Created: [count]
Migration Generated: [yes | no]
Migration Tree: [LINEAR | BRANCHED]
Current Migration: [revision id]

Models:
- ReportJob
- DataSource
- ReportTemplate

Migration File:
[Path to migration file]

Errors:
[Any errors encountered]
```

## Validation Rules

- Migration tree must be linear (no branches)
- Each migration must have a single parent
- Down_revision must point to previous migration
- No circular dependencies in migrations

## Error Handling

If migration tree is branched:
1. Check `alembic history` to identify branches
2. Merge branches or delete conflicting migrations
3. Regenerate migration if needed
4. Re-validate tree

If autogenerate fails:
1. Check DATABASE_URL environment variable
2. Verify database connection
3. Ensure models are properly defined
4. Check for syntax errors in models

If database connection fails:
1. Verify PostgreSQL is running
2. Check connection string format
3. Verify credentials
4. Check database exists
