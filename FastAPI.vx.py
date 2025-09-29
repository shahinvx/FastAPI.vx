#!/usr/bin/env python3
"""
FastAPI + SQLite + Alembic Project Boilerplate Creator
Supports Windows and Ubuntu/Linux

Usage:
    python create_project.py <project_name>

Example:
    python create_project.py my_fastapi_app
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, shell=True):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None


def create_directory_structure(project_name):
    """Create the basic project directory structure"""
    base_path = Path(project_name)

    directories = [
        base_path,
        base_path / "app" / "api" / "v1",
        base_path / "app" / "db",
        base_path / "app" / "models",
        base_path / "app" / "schemas",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

    return base_path


def create_file(file_path, content):
    """Create a file with given content"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created file: {file_path}")


def init_alembic(base_path):
    """Initialize Alembic in the project directory"""
    print("Initializing Alembic...")
    original_dir = os.getcwd()
    try:
        os.chdir(base_path)
        result = run_command("alembic init alembic")
        if result is not None:
            print("SUCCESS: Alembic initialized successfully")
            return True
        else:
            print("ERROR: Failed to initialize Alembic")
            return False
    finally:
        os.chdir(original_dir)


def create_project_files(base_path):
    """Create all project files with boilerplate content"""

    # pyproject.toml
    pyproject_content = '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fastapi-sqlite-app"
version = "0.1.0"
description = "FastAPI application with SQLite and Alembic"
requires-python = ">=3.8"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.20.0",
    "sqlalchemy>=2.0.0",
    "aiosqlite>=0.19.0",
    "alembic>=1.11.0",
    "pydantic[email]>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.24.0",
]

[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["alembic*"]
'''

    # .env
    env_content = '''DATABASE_URL="sqlite+aiosqlite:///./app.db"
'''

    # alembic.ini
    alembic_ini_content = '''[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./app.db

[handlers]
keys = console

[loggers]
keys = root, sqlalchemy, alembic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers = console
qualname = sqlalchemy.engine
propagate = 0

[logger_alembic]
level = INFO
handlers = console
qualname = alembic
propagate = 0

[logging]
level = INFO

[formatters]
keys = generic

[formatter_generic]
format = %(asctime)s %(name)s %(levelname)s: %(message)s
datefmt = %Y-%m-%d %H:%M:%S

[handler_console]
class = StreamHandler
args = (sys.stdout,)
level = NOTSET
formatter = generic
'''


    # app/db/base.py
    base_content = '''from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
'''

    # app/db/session.py
    session_content = '''import os
from typing import AsyncGenerator
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Auto-detect and load the nearest .env
load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

# Create async engine with improved configuration
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    echo=os.getenv("DB_ECHO", "false").lower() == "true"  # Enable SQL logging via env var
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    Properly handles session lifecycle with error handling.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
'''

    # app/models/user.py
    models_content = '''# db/models.py

from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

# Association table for many-to-many relationship
user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    users = relationship("User", secondary=user_permissions, back_populates="permissions")
'''

    # app/schemas/user.py
    schemas_content = '''from typing import List, Optional
from pydantic import BaseModel, EmailStr


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True
'''

    # app/main.py
    main_content = '''from fastapi import FastAPI

app = FastAPI(
    title="FastAPI SQLite App",
    description="A FastAPI application with SQLite, SQLAlchemy, and Alembic",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "FastAPI SQLite App is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
'''

    # Create __init__.py files
    init_content = ""

    # Create all files (excluding alembic.ini and alembic/env.py which will be handled separately)
    files_to_create = [
        (base_path / "pyproject.toml", pyproject_content),
        (base_path / ".env", env_content),
        (base_path / "app" / "__init__.py", init_content),
        (base_path / "app" / "db" / "__init__.py", init_content),
        (base_path / "app" / "db" / "base.py", base_content),
        (base_path / "app" / "db" / "session.py", session_content),
        (base_path / "app" / "models" / "__init__.py", init_content),
        (base_path / "app" / "models" / "user.py", models_content),
        (base_path / "app" / "schemas" / "__init__.py", init_content),
        (base_path / "app" / "schemas" / "user.py", schemas_content),
        (base_path / "app" / "api" / "__init__.py", init_content),
        (base_path / "app" / "api" / "v1" / "__init__.py", init_content),
        (base_path / "app" / "main.py", main_content),
    ]

    for file_path, content in files_to_create:
        create_file(file_path, content)


def update_alembic_config(base_path):
    """Update alembic.ini and env.py after alembic init"""
    print("Updating Alembic configuration...")

    # Update alembic.ini
    alembic_ini_path = base_path / "alembic.ini"
    alembic_ini_content = '''[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./app.db

[handlers]
keys = console

[loggers]
keys = root, sqlalchemy, alembic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers = console
qualname = sqlalchemy.engine
propagate = 0

[logger_alembic]
level = INFO
handlers = console
qualname = alembic
propagate = 0

[logging]
level = INFO

[formatters]
keys = generic

[formatter_generic]
format = %(asctime)s %(name)s %(levelname)s: %(message)s
datefmt = %Y-%m-%d %H:%M:%S

[handler_console]
class = StreamHandler
args = (sys.stdout,)
level = NOTSET
formatter = generic
'''
    create_file(alembic_ini_path, alembic_ini_content)

    # Update env.py with async support and model imports
    env_py_path = base_path / "alembic" / "env.py"
    env_py_content = '''import asyncio
import os,sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import Base
from app.models.user import User, Permission

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the database URL from config
    database_url = config.get_main_option("sqlalchemy.url")

    # Check if it's an async URL
    if database_url and "aiosqlite" in database_url:
        # Use async engine for aiosqlite
        asyncio.run(run_async_migrations())
    else:
        # Use synchronous engine for regular sqlite
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations with async engine."""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    """Helper function to run migrations in sync context."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
    create_file(env_py_path, env_py_content)


def create_setup_scripts(base_path):
    """Create platform-specific setup scripts"""

    # Windows setup script
    windows_setup = '''@echo off
echo Setting up FastAPI SQLite project...

echo Installing dependencies...
pip install -e .

echo Initializing Alembic...
alembic init alembic

echo Setting up database...
alembic revision -m "Initial migration" --autogenerate
alembic upgrade head

echo Setup complete!
echo.
echo To run the application:
echo uvicorn app.main:app --reload --port 8000
echo.
echo API will be available at: http://localhost:8000
pause
'''

    # Linux/Ubuntu setup script
    linux_setup = '''#!/bin/bash
echo "Setting up FastAPI SQLite project..."

echo "Installing dependencies..."
pip install -e .

echo "Initializing Alembic..."
alembic init alembic

echo "Setting up database..."
alembic revision -m "Initial migration" --autogenerate
alembic upgrade head

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "uvicorn app.main:app --reload --port 8000"
echo ""
echo "API will be available at: http://localhost:8000"
'''

    # Create setup scripts
    create_file(base_path / "setup.bat", windows_setup)
    create_file(base_path / "setup.sh", linux_setup)

    # Make Linux script executable
    if platform.system() != "Windows":
        os.chmod(base_path / "setup.sh", 0o755)


def create_readme(base_path, project_name):
    """Create project-specific README"""
    readme_content = f'''# {project_name}

A FastAPI project with SQLite, async SQLAlchemy, and Alembic migrations.

## Quick Setup

### Windows
```cmd
cd {project_name}
setup.bat
```

### Linux/Ubuntu
```bash
cd {project_name}
./setup.sh
```

## Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Set up database:**
   ```bash
   alembic revision -m "Initial migration" --autogenerate
   alembic upgrade head
   ```

3. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Project Structure

```
{project_name}/
├── .env                        # Environment variables
├── pyproject.toml              # Python project configuration
├── alembic.ini                 # Alembic configuration
├── app.db                      # SQLite database (created after setup)
├── setup.bat                   # Windows setup script
├── setup.sh                    # Linux setup script
├── alembic/                    # Alembic migration files
│   ├── env.py                  # Alembic environment (async support)
│   └── versions/               # Migration files
└── app/                        # Main application code
    ├── main.py                 # FastAPI entry point
    ├── db/
    │   ├── base.py             # SQLAlchemy base
    │   └── session.py          # Async session management
    ├── models/
    │   └── user.py             # User and Permission models
    ├── schemas/                # Pydantic schemas
    │   └── user.py             # User response schemas
    └── api/
        └── v1/                 # API version 1
```

## Available Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- API Documentation: http://localhost:8000/docs

## Database Models

- **Users**: id, username, email, password, is_active
- **Permissions**: id, name, description
- **User-Permission**: Many-to-many relationship

## Development Commands

```bash
# Create new migration
alembic revision -m "description" --autogenerate

# Apply migrations
alembic upgrade head

# Check migration status
alembic current

# View database tables
sqlite3 app.db ".tables"
```

## Environment Variables

Create/modify `.env` file:
```
DATABASE_URL="sqlite+aiosqlite:///./app.db"
DB_ECHO="false"  # Set to "true" for SQL logging
```
'''

    create_file(base_path / "README.md", readme_content)


def main():
    if len(sys.argv) != 2:
        print("Usage: python create_project.py <project_name>")
        print("Example: python create_project.py my_fastapi_app")
        sys.exit(1)

    project_name = sys.argv[1]

    if Path(project_name).exists():
        print(f"Error: Directory '{project_name}' already exists!")
        sys.exit(1)

    print(f"Creating FastAPI SQLite project: {project_name}")
    print(f"Platform: {platform.system()}")
    print()

    # Create project structure
    base_path = create_directory_structure(project_name)

    # Create all project files
    create_project_files(base_path)

    # Initialize Alembic and update configuration
    if init_alembic(base_path):
        update_alembic_config(base_path)
    else:
        print("WARNING: Alembic initialization failed. You'll need to run 'alembic init alembic' manually.")

    # Create setup scripts
    create_setup_scripts(base_path)

    # Create README
    create_readme(base_path, project_name)

    print(f"""
SUCCESS: Project '{project_name}' created successfully!

Next steps:
  1. cd {project_name}
  2. Run setup script:
     Windows: setup.bat
     Linux:   ./setup.sh
  3. Start coding!

The application will be available at: http://localhost:8000
""")


if __name__ == "__main__":
    main()