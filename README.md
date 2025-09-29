# FastAPI Project with SQLite + Async SQLAlchemy + Alembic

A FastAPI project using SQLite with async SQLAlchemy for database operations and Alembic for database migrations.

## Project Structure

```
backend/
├── README.md                   # This file
├── .env                        # Environment variables
├── pyproject.toml              # Python project configuration
├── alembic.ini                 # Alembic configuration
├── app.db                      # SQLite database file
├── alembic/                    # Alembic migration files
│   ├── env.py                  # Alembic environment setup (with async support)
│   └── versions/               # Migration files
│       └── 8ded3252ce31_init.py
└── app/                        # Main application code
    ├── main.py                 # FastAPI application entry point
    ├── db/
    │   ├── base.py             # SQLAlchemy DeclarativeBase
    │   └── session.py          # Async database session management
    ├── models/
    │   └── user.py             # User and Permission models
    ├── schemas/                # Pydantic schemas for API validation
    │   └── user.py             # User request/response schemas
    └── api/
        ├── routers.py
        └── v1/
            └── home_router.py
```

## Database Models

### User Model
- `id`: Primary key (Integer)
- `username`: Unique username (String)
- `email`: Unique email address (String)
- `password`: Hashed password (String)
- `is_active`: Account status (Boolean)

### Permission Model
- `id`: Primary key (Integer)
- `name`: Unique permission name (String)
- `description`: Permission description (String)

### Many-to-Many Relationship
- Users and Permissions are linked through `user_permissions` association table
- Allows flexible permission assignment to users

## Environment Setup

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Environment Variables
Create a `.env` file in the backend directory:
```bash
DATABASE_URL="sqlite+aiosqlite:///./app.db"
```

Or set environment variable:
```bash
# Windows Command Prompt
set DATABASE_URL=sqlite+aiosqlite:///./app.db

# Windows PowerShell
$env:DATABASE_URL="sqlite+aiosqlite:///./app.db"

# Linux/Mac
export DATABASE_URL="sqlite+aiosqlite:///./app.db"
```

## Alembic Database Migration Setup

### Initial Setup (Already Done)
```bash
# Initialize Alembic (already completed)
alembic init alembic
```

### Configuration Details

**Key Configuration Files:**

1. **`alembic.ini`**: Uses synchronous SQLite for migrations
   ```ini
   sqlalchemy.url = sqlite:///./app.db
   ```

2. **`alembic/env.py`**: Enhanced with async SQLAlchemy support
   - Automatically detects async vs sync database URLs
   - Handles both `sqlite://` and `sqlite+aiosqlite://` connections
   - Imports all models for autogenerate functionality

3. **`app/db/session.py`**: Async database session for application
   ```python
   DATABASE_URL = "sqlite+aiosqlite:///./app.db"
   engine = create_async_engine(DATABASE_URL)
   ```

### Migration Commands

#### Create New Migration
```bash
cd backend
alembic revision -m "description_of_changes" --autogenerate
```

#### Apply Migrations
```bash
cd backend
alembic upgrade head
```

#### Check Current Migration Status
```bash
cd backend
alembic current
```

#### View Migration History
```bash
cd backend
alembic history --verbose
```

#### Rollback to Previous Migration
```bash
cd backend
alembic downgrade -1
```

#### Rollback to Specific Migration
```bash
cd backend
alembic downgrade <revision_id>
```

## Database Operations

### View Database Tables
```bash
cd backend
sqlite3 app.db ".tables"
```

### View Table Schema
```bash
cd backend
sqlite3 app.db ".schema users"
sqlite3 app.db ".schema permissions"
sqlite3 app.db ".schema user_permissions"
```

### View Table Contents
```bash
cd backend
sqlite3 app.db "SELECT * FROM users;"
sqlite3 app.db "SELECT * FROM permissions;"
sqlite3 app.db "SELECT * FROM alembic_version;"
```

## Running the Application

```bash
cd backend
uvicorn app.main:app --reload --port 8001
```

API will be available at: http://localhost:8001

## Common Workflows

### Adding a New Model
1. Create the model in `app/models/`
2. Import the model in `alembic/env.py` (if not auto-imported)
3. Generate migration:
   ```bash
   alembic revision -m "add_new_model" --autogenerate
   ```
4. Review the generated migration file
5. Apply the migration:
   ```bash
   alembic upgrade head
   ```

### Modifying Existing Models
1. Update the model in `app/models/`
2. Generate migration:
   ```bash
   alembic revision -m "modify_model_description" --autogenerate
   ```
3. Review and edit the migration file if needed
4. Apply the migration:
   ```bash
   alembic upgrade head
   ```

## Troubleshooting

### Common Issues

1. **"Target database is not up to date" Error**
   ```bash
   # Apply pending migrations first
   alembic upgrade head
   # Then create new migration
   alembic revision -m "your_message" --autogenerate
   ```

2. **Async/Sync Database Driver Issues**
   - Application uses `sqlite+aiosqlite://` (async)
   - Alembic uses `sqlite://` (sync)
   - Both access the same `app.db` file

3. **Empty Database File**
   ```bash
   # Remove empty database and re-run migrations
   rm app.db
   alembic upgrade head
   ```

### Database Reset (Development Only)
```bash
cd backend
rm app.db
alembic upgrade head
```

## Project Boilerplate Generator

To create a new project with this structure anywhere (Windows/Ubuntu):

### 1. Copy the boilerplate script
Copy `create_project.py` from this repository to your desired location.

### 2. Run the generator
```bash
# Create a new project
python create_project.py my_new_app

# Navigate to project
cd my_new_app

# Windows setup
setup.bat

# Linux/Ubuntu setup
./setup.sh
```

### 3. What the generator creates:
- Complete project structure with all files
- Cross-platform setup scripts (`.bat` for Windows, `.sh` for Linux)
- Pre-configured Alembic with async support
- Basic FastAPI application
- User/Permission models and schemas
- Project-specific README

### 4. Generated project structure:
```
my_new_app/
├── .env                        # Environment variables
├── pyproject.toml              # Dependencies
├── alembic.ini                 # Alembic config
├── setup.bat / setup.sh        # Platform setup scripts
├── README.md                   # Project-specific README
├── alembic/
│   ├── env.py                  # Async-enabled environment
│   └── versions/               # Migration files
└── app/
    ├── main.py                 # FastAPI entry point
    ├── db/                     # Database setup
    ├── models/                 # SQLAlchemy models
    ├── schemas/                # Pydantic schemas
    └── api/v1/                 # API routes
```

## Notes

- The project uses **async SQLAlchemy** for application database operations
- **Alembic migrations** run synchronously but work with the same database file
- All models must be imported in `alembic/env.py` for autogenerate to work
- Database file location: `./app.db` (relative to project directory)
- Migration files are stored in `alembic/versions/`
- Boilerplate generator works on Windows, Ubuntu, and other Linux distributions

## File Locations (Current Project)
- **Database**: `E:\SWE_Projects\user_app\backend\app.db`
- **Models**: `E:\SWE_Projects\user_app\backend\app\models\`
- **Migrations**: `E:\SWE_Projects\user_app\backend\alembic\versions\`
- **Config**: `E:\SWE_Projects\user_app\backend\alembic.ini`
- **Boilerplate**: `E:\SWE_Projects\user_app\create_project.py`