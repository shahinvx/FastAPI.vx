# FastAPI + SQLite + Alembic Project Generator

A Python script that generates a complete FastAPI project with SQLite database, async SQLAlchemy, and Alembic migrations. Works on Windows and Ubuntu/Linux.

## 🚀 Quick Start

```bash
# Generate a new project
python create_project.py my_awesome_api

# Navigate to project
cd my_awesome_api

# Setup and run (Windows)
setup.bat

# Setup and run (Linux/Ubuntu)
./setup.sh
```

Your API will be available at: http://localhost:8000

## 📋 Requirements

- Python 3.8+
- pip
- Internet connection (for downloading dependencies)

## 🎯 What Gets Created

### Project Structure
```
my_project_name/
├── .env                        # Environment variables
├── pyproject.toml              # Python dependencies and build config
├── alembic.ini                 # Alembic migration configuration
├── app.db                      # SQLite database (after setup)
├── setup.bat                   # Windows setup script
├── setup.sh                    # Linux setup script
├── README.md                   # Project-specific documentation
├── alembic/                    # Database migrations
│   ├── env.py                  # Async-enabled Alembic environment
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
└── app/                        # Main application
    ├── main.py                 # FastAPI application entry point
    ├── db/
    │   ├── base.py             # SQLAlchemy DeclarativeBase
    │   └── session.py          # Async database session management
    ├── models/
    │   └── user.py             # User & Permission models with relationships
    ├── schemas/
    │   └── user.py             # Pydantic response schemas
    └── api/
        └── v1/                 # API version 1 routes
```

### Pre-built Features
- ✅ **User Management**: User model with email, username, password, active status
- ✅ **Permission System**: Permission model with many-to-many user relationships
- ✅ **Async Database**: SQLAlchemy with aiosqlite for async operations
- ✅ **Migrations**: Alembic with async support for database versioning
- ✅ **API Schemas**: Pydantic models for request/response validation
- ✅ **Environment Config**: .env file for configuration management
- ✅ **Cross-platform**: Setup scripts for Windows and Linux

## 🔧 Usage Examples

### Basic Usage
```bash
python create_project.py blog_api
```

### Different Project Names
```bash
python create_project.py ecommerce_backend
python create_project.py inventory_system
python create_project.py user_management_api
```

## 📖 Generated Project Documentation

Each generated project includes a complete README with:
- Setup instructions
- Database commands
- API endpoints
- Development workflows
- Troubleshooting guide

## 🛠️ Setup Process Details

### What the Setup Scripts Do

#### 1. Install Dependencies
- FastAPI for web framework
- SQLAlchemy + aiosqlite for async database
- Alembic for migrations
- Pydantic for data validation
- Uvicorn for ASGI server
- Python-dotenv for environment variables

#### 2. Initialize Database
- Run `alembic init alembic` (creates migration structure)
- Generate initial migration from models
- Apply migration to create database tables

#### 3. Ready to Use
- Database with User/Permission tables
- FastAPI app with basic endpoints
- Development server ready to start

## 🏃‍♂️ Manual Setup (Alternative)

If you prefer manual setup or need to customize:

```bash
# After generating project
cd your_project_name

# Install dependencies
pip install -e .

# Initialize Alembic (creates alembic/ directory with templates)
alembic init alembic

# Generate migration from models
alembic revision -m "Initial migration" --autogenerate

# Apply migration
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --port 8000
```

## 🗄️ Database Models

### User Model
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
```

### Permission Model
```python
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    users = relationship("User", secondary=user_permissions, back_populates="permissions")
```

### Many-to-Many Relationship
```python
user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True)
)
```

## 🌐 API Endpoints

Generated projects include these basic endpoints:

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## ⚙️ Configuration

### Environment Variables (.env)
```bash
DATABASE_URL="sqlite+aiosqlite:///./app.db"
DB_ECHO="false"  # Set to "true" for SQL query logging
```

### Database Configuration
- **Application**: Uses `sqlite+aiosqlite://` for async operations
- **Migrations**: Uses `sqlite://` for synchronous Alembic operations
- Both access the same `app.db` file

## 🚨 Troubleshooting

### Common Issues

#### 1. "Directory already exists"
```bash
# Remove existing directory first
rm -rf project_name
python create_project.py project_name
```

#### 2. "Alembic command not found"
```bash
# Install alembic
pip install alembic

# Or install in project environment
pip install -e .
```

#### 3. "No module named 'app'"
```bash
# Make sure you're in the project directory
cd your_project_name

# Install project in editable mode
pip install -e .
```

#### 4. Migration Detection Issues
```bash
# Ensure models are imported in alembic/env.py
# Check that Base.metadata includes your models
```

### Platform-Specific Notes

#### Windows
- Use `setup.bat` for automatic setup
- PowerShell alternative: `$env:DATABASE_URL="sqlite+aiosqlite:///./app.db"`
- Ensure Python and pip are in PATH

#### Linux/Ubuntu
- Use `./setup.sh` for automatic setup
- May need to install python3-pip: `sudo apt install python3-pip`
- Make script executable: `chmod +x setup.sh`

## 🔄 Development Workflow

### Adding New Models
1. Create model in `app/models/`
2. Import in `alembic/env.py` (if not auto-imported)
3. Generate migration: `alembic revision -m "add_model" --autogenerate`
4. Review and apply: `alembic upgrade head`

### Adding API Endpoints
1. Create router in `app/api/v1/`
2. Import in `app/main.py`
3. Add to FastAPI app with `app.include_router()`

### Database Operations

#### Migration Management
```bash
# View current migration status
alembic current

# View migration history with details
alembic history --verbose

# View specific migration details
alembic show <revision_id>

# Create new migration
alembic revision -m "description" --autogenerate

# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback to previous migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base

# Generate SQL for migration (don't apply)
alembic upgrade head --sql

# Check if database is up to date
alembic current
```

#### Database Inspection
```bash
# List all tables
sqlite3 app.db ".tables"

# Show database schema for all tables
sqlite3 app.db ".schema"

# Show specific table schema
sqlite3 app.db ".schema users"
sqlite3 app.db ".schema permissions"
sqlite3 app.db ".schema user_permissions"

# Show table info (columns, types, etc.)
sqlite3 app.db ".fullschema users"

# Show indexes
sqlite3 app.db ".indexes"
sqlite3 app.db ".indexes users"

# Database file info
sqlite3 app.db ".dbinfo"

# Show database statistics
sqlite3 app.db ".stats"
```

#### Data Operations
```bash
# View all data in tables
sqlite3 app.db "SELECT * FROM users;"
sqlite3 app.db "SELECT * FROM permissions;"
sqlite3 app.db "SELECT * FROM user_permissions;"
sqlite3 app.db "SELECT * FROM alembic_version;"

# Count records
sqlite3 app.db "SELECT COUNT(*) FROM users;"
sqlite3 app.db "SELECT COUNT(*) FROM permissions;"

# Insert sample data
sqlite3 app.db "INSERT INTO permissions (name, description) VALUES ('admin', 'Administrator access');"
sqlite3 app.db "INSERT INTO permissions (name, description) VALUES ('user', 'Basic user access');"

# Insert user
sqlite3 app.db "INSERT INTO users (username, email, password, is_active) VALUES ('john_doe', 'john@example.com', 'hashed_password', 1);"

# Create user-permission relationship
sqlite3 app.db "INSERT INTO user_permissions (user_id, permission_id) VALUES (1, 1);"

# Query with joins
sqlite3 app.db "
SELECT u.username, u.email, p.name as permission
FROM users u
JOIN user_permissions up ON u.id = up.user_id
JOIN permissions p ON up.permission_id = p.id;"

# Update records
sqlite3 app.db "UPDATE users SET is_active = 0 WHERE username = 'john_doe';"

# Delete records (be careful!)
sqlite3 app.db "DELETE FROM user_permissions WHERE user_id = 1;"
sqlite3 app.db "DELETE FROM users WHERE username = 'john_doe';"
```

#### Database Backup and Restore
```bash
# Backup database
sqlite3 app.db ".backup backup.db"

# Create SQL dump
sqlite3 app.db ".dump" > backup.sql

# Restore from SQL dump
sqlite3 restored.db < backup.sql

# Copy database file
cp app.db backup_$(date +%Y%m%d_%H%M%S).db
```

#### Database Analysis
```bash
# Analyze database performance
sqlite3 app.db "ANALYZE;"

# Show query execution plan
sqlite3 app.db "EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';"

# Show table sizes
sqlite3 app.db "
SELECT
    name,
    COUNT(*) as row_count
FROM (
    SELECT 'users' as name UNION ALL
    SELECT 'permissions' UNION ALL
    SELECT 'user_permissions'
) t
JOIN (
    SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL
    SELECT 'permissions', COUNT(*) FROM permissions UNION ALL
    SELECT 'user_permissions', COUNT(*) FROM user_permissions
) c ON t.name = c.table_name;"

# Check database integrity
sqlite3 app.db "PRAGMA integrity_check;"

# Optimize database
sqlite3 app.db "VACUUM;"
```

#### Advanced Queries
```bash
# Find users with specific permissions
sqlite3 app.db "
SELECT u.username, u.email
FROM users u
JOIN user_permissions up ON u.id = up.user_id
JOIN permissions p ON up.permission_id = p.id
WHERE p.name = 'admin';"

# Find users without any permissions
sqlite3 app.db "
SELECT u.username, u.email
FROM users u
LEFT JOIN user_permissions up ON u.id = up.user_id
WHERE up.user_id IS NULL;"

# Count permissions per user
sqlite3 app.db "
SELECT u.username, COUNT(up.permission_id) as permission_count
FROM users u
LEFT JOIN user_permissions up ON u.id = up.user_id
GROUP BY u.id, u.username
ORDER BY permission_count DESC;"

# Find most common permissions
sqlite3 app.db "
SELECT p.name, COUNT(up.user_id) as user_count
FROM permissions p
LEFT JOIN user_permissions up ON p.id = up.permission_id
GROUP BY p.id, p.name
ORDER BY user_count DESC;"
```

#### Development Database Operations
```bash
# Reset database (remove all data, keep structure)
sqlite3 app.db "DELETE FROM user_permissions;"
sqlite3 app.db "DELETE FROM users;"
sqlite3 app.db "DELETE FROM permissions;"

# Drop and recreate database
rm app.db
alembic upgrade head

# Seed database with test data
sqlite3 app.db < seed_data.sql

# Export specific table data
sqlite3 app.db -header -csv "SELECT * FROM users;" > users_export.csv

# Import CSV data
sqlite3 app.db "
.mode csv
.import users_data.csv users_temp
INSERT INTO users (username, email, password, is_active)
SELECT username, email, password, is_active FROM users_temp;
DROP TABLE users_temp;"
```

#### Database Monitoring
```bash
# Monitor database file size
ls -lh app.db

# Watch database file changes (Linux/Mac)
watch -n 1 "ls -lh app.db && sqlite3 app.db 'SELECT COUNT(*) as users FROM users; SELECT COUNT(*) as permissions FROM permissions;'"

# Check database locks
sqlite3 app.db "PRAGMA lock_status;"

# Show database configuration
sqlite3 app.db "PRAGMA compile_options;"
```

## 📚 Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Async ORM for database operations
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **aiosqlite**: Async SQLite driver
- **Uvicorn**: ASGI server for running FastAPI
- **SQLite**: Lightweight, serverless database

## 🎨 Customization

### Modifying the Generator
The `create_project.py` script can be customized to:
- Change default dependencies in `pyproject_content`
- Modify database models in `models_content`
- Add additional files or directories
- Change the FastAPI application structure

### Generated Project Customization
After generation, you can:
- Add more models and relationships
- Implement authentication and authorization
- Add middleware and dependency injection
- Integrate with external services
- Add testing with pytest

## 📝 Notes

- The generator uses `alembic init alembic` to ensure proper migration templates
- Async SQLAlchemy support is pre-configured in the generated `env.py`
- The project structure follows FastAPI best practices
- All generated projects include comprehensive documentation
- Setup scripts handle cross-platform differences automatically

## 🤝 Contributing

To improve the generator:
1. Modify `create_project.py`
2. Test with: `python create_project.py test_project`
3. Verify all features work correctly
4. Update this documentation if needed

## 📄 License

Use this generator freely for any project. The generated projects are yours to modify and distribute as needed.
