#!/usr/bin/env python3
"""
Validation script to check if the backend setup is correct.
Runs without installing dependencies.
"""

import sys
from pathlib import Path

def check_file_exists(path: Path, description: str) -> bool:
    """Check if a file exists."""
    if path.exists():
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} MISSING: {path}")
        return False

def main():
    """Validate backend setup."""
    print("=" * 60)
    print("Stonky Backend Setup Validation")
    print("=" * 60)
    print()

    backend_dir = Path(__file__).parent.parent
    checks = []

    # Core files
    print("Core Files:")
    checks.append(check_file_exists(backend_dir / "pyproject.toml", "Poetry config"))
    checks.append(check_file_exists(backend_dir / ".env.example", "Environment template"))
    checks.append(check_file_exists(backend_dir / "alembic.ini", "Alembic config"))
    checks.append(check_file_exists(backend_dir / "README.md", "README"))
    print()

    # App structure
    print("App Structure:")
    app_dir = backend_dir / "app"
    checks.append(check_file_exists(app_dir / "main.py", "FastAPI entry"))
    checks.append(check_file_exists(app_dir / "core" / "config.py", "Configuration"))
    checks.append(check_file_exists(app_dir / "core" / "database.py", "Database setup"))
    checks.append(check_file_exists(app_dir / "core" / "logging.py", "Logging config"))
    checks.append(check_file_exists(app_dir / "core" / "dependencies.py", "Dependencies"))
    print()

    # Models
    print("Models:")
    models_dir = app_dir / "models"
    checks.append(check_file_exists(models_dir / "__init__.py", "Models package"))
    checks.append(check_file_exists(models_dir / "company.py", "Company model"))
    checks.append(check_file_exists(models_dir / "financials.py", "Financials model"))
    checks.append(check_file_exists(models_dir / "snapshot.py", "Snapshot model"))
    checks.append(check_file_exists(models_dir / "price.py", "Price model"))
    print()

    # Repositories
    print("Repositories:")
    repo_dir = app_dir / "repositories"
    checks.append(check_file_exists(repo_dir / "base.py", "Base repository"))
    checks.append(check_file_exists(repo_dir / "company.py", "Company repository"))
    print()

    # Migrations
    print("Migrations:")
    migrations_dir = backend_dir / "migrations"
    checks.append(check_file_exists(migrations_dir / "env.py", "Alembic env"))
    checks.append(check_file_exists(migrations_dir / "script.py.mako", "Migration template"))
    print()

    # Test structure
    print("Test Structure:")
    tests_dir = backend_dir / "tests"
    checks.append(check_file_exists(tests_dir / "unit", "Unit tests dir"))
    checks.append(check_file_exists(tests_dir / "integration", "Integration tests dir"))
    checks.append(check_file_exists(tests_dir / "e2e", "E2E tests dir"))
    print()

    # Summary
    print("=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("✓ All checks passed! Backend setup is complete.")
        print()
        print("Next steps:")
        print("1. Install dependencies: poetry install")
        print("2. Copy .env.example to .env and configure")
        print("3. Start PostgreSQL and Redis")
        print("4. Run migrations: poetry run alembic upgrade head")
        print("5. Start server: poetry run uvicorn app.main:app --reload")
        return 0
    else:
        print(f"✗ {total - passed} checks failed. Please review setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
