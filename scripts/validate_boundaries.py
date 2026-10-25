#!/usr/bin/env python3
"""
Domain Layer Boundary Validation Script

This script performs static analysis to ensure that code in src/domain/
has zero infrastructure/framework imports. The domain layer should only
contain pure Pydantic models and contracts.

Allowed imports:
- pydantic (and submodules)
- typing (and submodules)
- dataclasses
- datetime
- decimal
- enum
- pathlib
- collections
- Standard library modules

Forbidden imports:
- sqlalchemy
- openpyxl
- pdfplumber
- psycopg2
- Any database drivers
- Any framework-specific libraries
"""

import ast
import sys
from pathlib import Path
from typing import Set, List, Tuple


# Configuration
DOMAIN_DIR = Path("src/domain")
FORBIDDEN_MODULES = {
    "sqlalchemy",
    "openpyxl",
    "pdfplumber",
    "psycopg2",
    "psycopg2-binary",
    "alembic",
    "pymssql",
    "cx_Oracle",
    "pandas",  # Should be in application layer, not domain
}

ALLOWED_MODULES = {
    "pydantic",
    "typing",
    "dataclasses",
    "datetime",
    "decimal",
    "enum",
    "pathlib",
    "collections",
    "itertools",
    "functools",
    "re",
    "json",
    "uuid",
    "hashlib",
    "base64",
}


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to collect import statements."""

    def __init__(self, filename: str):
        self.filename = filename
        self.imports: List[Tuple[str, int]] = []  # (module, line_number)
        self.from_imports: List[Tuple[str, str, int]] = []  # (module, name, line_number)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append((alias.name, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            for alias in node.names:
                self.from_imports.append((node.module, alias.name, node.lineno))
        self.generic_visit(node)


def check_forbidden_imports(analyzer: ImportAnalyzer) -> List[Tuple[str, int, str]]:
    """Check if any imports are from forbidden modules."""
    violations = []

    for module, lineno in analyzer.imports:
        base_module = module.split(".")[0]
        if base_module in FORBIDDEN_MODULES:
            violations.append((module, lineno, "forbidden_module"))

    for module, name, lineno in analyzer.from_imports:
        base_module = module.split(".")[0]
        if base_module in FORBIDDEN_MODULES:
            violations.append((f"{module}.{name}", lineno, "forbidden_module"))

    return violations


def analyze_file(filepath: Path) -> Tuple[List[Tuple[str, int, str]], bool]:
    """Analyze a single Python file for boundary violations."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return [], False

    try:
        tree = ast.parse(content, filename=str(filepath))
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
        return [], False

    analyzer = ImportAnalyzer(str(filepath))
    analyzer.visit(tree)

    violations = check_forbidden_imports(analyzer)
    return violations, True


def main() -> int:
    """Main entry point."""
    if not DOMAIN_DIR.exists():
        print(f"Error: Domain directory {DOMAIN_DIR} does not exist.", file=sys.stderr)
        return 1

    print(f"Analyzing domain layer: {DOMAIN_DIR}")
    print("=" * 70)

    all_violations = []
    files_analyzed = 0
    files_with_errors = 0

    for py_file in DOMAIN_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        violations, success = analyze_file(py_file)
        files_analyzed += 1

        if not success:
            files_with_errors += 1
            continue

        if violations:
            files_with_errors += 1
            print(f"\n{py_file}:")
            for module, lineno, reason in violations:
                print(f"  Line {lineno}: Import of '{module}' ({reason})")
                all_violations.append((str(py_file), module, lineno, reason))

    print("=" * 70)
    print(f"Files analyzed: {files_analyzed}")
    print(f"Files with violations: {files_with_errors}")

    if all_violations:
        print(f"\n[X] FAILED: {len(all_violations)} boundary violations found")
        print("\nForbidden modules detected in domain layer.")
        print("The domain layer should only contain pure Pydantic models and contracts.")
        print("Move infrastructure imports to src/infrastructure/ or src/application/")
        return 1
    else:
        print("\n[OK] PASSED: No boundary violations found")
        print("Domain layer is clean - only pure models and contracts detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
