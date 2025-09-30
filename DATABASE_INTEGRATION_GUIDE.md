# Database Integration Guide

This guide shows how to integrate PostgreSQL and MongoDB with your FastAPI project created by `create_project.py`.

## Table of Contents

- [PostgreSQL Integration](#postgresql-integration)
- [MongoDB Integration](#mongodb-integration)
- [Switching Between Databases](#switching-between-databases)
- [Environment Configuration](#environment-configuration)

---

## PostgreSQL Integration

### 1. Install PostgreSQL Dependencies

Update your `pyproject.toml` dependencies section:

```toml
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.20.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.28.0",          # PostgreSQL async driver
    "alembic>=1.11.0",
    "pydantic[email]>=2.0.0",
    "python-dotenv>=1.0.0",
    "psycopg2-binary>=2.9.0",   # PostgreSQL sync driver for Alembic
]
```

### 2. Update Database Session Configuration

Modify `app/db/session.py`:

```python
import os
from typing import AsyncGenerator
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Auto-detect and load the nearest .env
load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname")

# Create async engine with PostgreSQL optimizations
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    pool_size=20,               # Connection pool size
    max_overflow=0,             # Additional connections beyond pool_size
    pool_recycle=3600,          # Recycle connections after 1 hour
    echo=os.getenv("DB_ECHO", "false").lower() == "true"
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
```

### 3. Update Alembic Configuration

Modify `alembic.ini`:

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost/dbname

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
```

### 4. Update Environment Variables

Update your `.env` file:

```env
# PostgreSQL Configuration
DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/your_database"
DB_ECHO="false"

# PostgreSQL Connection Details (alternative format)
POSTGRES_USER="username"
POSTGRES_PASSWORD="password"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="your_database"
```

### 5. PostgreSQL Setup Commands

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE your_database;
CREATE USER username WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE your_database TO username;
\q

# Install Python dependencies
pip install asyncpg psycopg2-binary

# Run migrations
alembic revision -m "Initial PostgreSQL migration" --autogenerate
alembic upgrade head
```

---

## MongoDB Integration

### 1. Install MongoDB Dependencies

Update your `pyproject.toml`:

```toml
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.20.0",
    "motor>=3.3.0",             # Async MongoDB driver
    "pymongo>=4.5.0",           # MongoDB driver
    "beanie>=1.23.0",           # MongoDB ODM for FastAPI
    "pydantic[email]>=2.0.0",
    "python-dotenv>=1.0.0",
]
```

### 2. Create MongoDB Configuration

Create `app/db/mongodb.py`:

```python
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fastapi_db")

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    mongodb.client = AsyncIOMotorClient(MONGODB_URL)
    mongodb.database = mongodb.client[DATABASE_NAME]

    # Initialize Beanie with document models
    from app.models.user_mongo import User, Permission
    await init_beanie(
        database=mongodb.database,
        document_models=[User, Permission]
    )
    print("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    if mongodb.client:
        mongodb.client.close()
        print("Disconnected from MongoDB")

async def get_database():
    """Get database instance"""
    return mongodb.database
```

### 3. Create MongoDB Models

Create `app/models/user_mongo.py`:

```python
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import EmailStr
from pymongo import IndexModel

class Permission(Document):
    name: Indexed(str, unique=True)
    description: Optional[str] = None

    class Settings:
        name = "permissions"
        indexes = [
            IndexModel("name", unique=True)
        ]

class User(Document):
    username: Indexed(str, unique=True)
    email: Indexed(EmailStr, unique=True)
    password: str
    is_active: bool = True
    permission_ids: List[str] = []

    class Settings:
        name = "users"
        indexes = [
            IndexModel("username", unique=True),
            IndexModel("email", unique=True),
            IndexModel("is_active")
        ]

    async def get_permissions(self) -> List[Permission]:
        """Get user permissions"""
        return await Permission.find({"_id": {"$in": self.permission_ids}}).to_list()

    async def add_permission(self, permission: Permission):
        """Add permission to user"""
        if str(permission.id) not in self.permission_ids:
            self.permission_ids.append(str(permission.id))
            await self.save()

    async def remove_permission(self, permission: Permission):
        """Remove permission from user"""
        if str(permission.id) in self.permission_ids:
            self.permission_ids.remove(str(permission.id))
            await self.save()
```

### 4. Update MongoDB Schemas

Create `app/schemas/user_mongo.py`:

```python
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_active: bool = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_active: bool
    permissions: List[PermissionResponse] = []
```

### 5. Create MongoDB API Router

Create `app/api/v1/users_mongo_router.py`:

```python
from typing import List
from fastapi import APIRouter, HTTPException
from app.models.user_mongo import User, Permission
from app.schemas.user_mongo import UserCreate, UserResponse, PermissionCreate, PermissionResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["users"])
auth_service = AuthService("your-secret-key")

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    # Check if user already exists
    existing_user = await User.find_one({"$or": [{"username": user_data.username}, {"email": user_data.email}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password
    hashed_password = auth_service.hash_password(user_data.password)

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        is_active=user_data.is_active
    )
    await user.save()

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        permissions=[]
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    permissions = await user.get_permissions()
    permission_responses = [
        PermissionResponse(id=str(p.id), name=p.name, description=p.description)
        for p in permissions
    ]

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        permissions=permission_responses
    )

@router.get("/", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100):
    """List users with pagination"""
    users = await User.find().skip(skip).limit(limit).to_list()

    result = []
    for user in users:
        permissions = await user.get_permissions()
        permission_responses = [
            PermissionResponse(id=str(p.id), name=p.name, description=p.description)
            for p in permissions
        ]

        result.append(UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            permissions=permission_responses
        ))

    return result

@router.post("/permissions/", response_model=PermissionResponse)
async def create_permission(permission_data: PermissionCreate):
    """Create a new permission"""
    existing_permission = await Permission.find_one({"name": permission_data.name})
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission already exists")

    permission = Permission(
        name=permission_data.name,
        description=permission_data.description
    )
    await permission.save()

    return PermissionResponse(
        id=str(permission.id),
        name=permission.name,
        description=permission.description
    )
```

### 6. Update Main Application for MongoDB

Update `app/main.py`:

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.users_mongo_router import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="FastAPI MongoDB App",
    description="A FastAPI application with MongoDB and Beanie ODM",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(users_router, prefix="/api/v1")
```

### 7. MongoDB Environment Variables

Update your `.env` file:

```env
# MongoDB Configuration
MONGODB_URL="mongodb://localhost:27017"
DATABASE_NAME="fastapi_db"

# MongoDB with authentication
# MONGODB_URL="mongodb://username:password@localhost:27017"

# MongoDB Atlas (cloud)
# MONGODB_URL="mongodb+srv://username:password@cluster.mongodb.net"
```

### 8. MongoDB Setup Commands

```bash
# Install MongoDB (Ubuntu/Debian)
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Install Python dependencies
pip install motor pymongo beanie

# Test connection
python -c "from pymongo import MongoClient; print('Connected to MongoDB:', MongoClient().admin.command('ping'))"
```

---

## Switching Between Databases

### 1. Environment-Based Configuration

Create `app/config.py`:

```python
import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"

class Settings:
    DATABASE_TYPE: DatabaseType = DatabaseType(os.getenv("DATABASE_TYPE", "sqlite"))

    # SQLite/PostgreSQL settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "fastapi_db")

    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

settings = Settings()
```

### 2. Database Factory Pattern

Create `app/db/factory.py`:

```python
from app.config import settings, DatabaseType
from app.db.session import get_session
from app.db.mongodb import get_database

async def get_db_session():
    """Get appropriate database session based on configuration"""
    if settings.DATABASE_TYPE in [DatabaseType.SQLITE, DatabaseType.POSTGRESQL]:
        async for session in get_session():
            yield session
    elif settings.DATABASE_TYPE == DatabaseType.MONGODB:
        yield await get_database()
    else:
        raise ValueError(f"Unsupported database type: {settings.DATABASE_TYPE}")
```

---

## Environment Configuration

### Complete .env Example

```env
# Database Type Selection
DATABASE_TYPE="postgresql"  # sqlite, postgresql, mongodb

# SQLite Configuration
# DATABASE_URL="sqlite+aiosqlite:///./app.db"

# PostgreSQL Configuration
DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/fastapi_db"
POSTGRES_USER="username"
POSTGRES_PASSWORD="password"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="fastapi_db"

# MongoDB Configuration
MONGODB_URL="mongodb://localhost:27017"
DATABASE_NAME="fastapi_db"

# General Settings
DB_ECHO="false"
SECRET_KEY="your-super-secret-key-here"
```

### Docker Compose for Development

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: username
      POSTGRES_PASSWORD: password
      POSTGRES_DB: fastapi_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # MongoDB
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  # Redis (optional for caching)
  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  mongodb_data:
```

### Development Commands

```bash
# Start databases with Docker
docker-compose up -d postgres mongodb

# PostgreSQL migration commands
alembic revision -m "Description" --autogenerate
alembic upgrade head

# MongoDB doesn't need migrations, but you can create indexes
python -c "from app.db.mongodb import connect_to_mongo; import asyncio; asyncio.run(connect_to_mongo())"
```

This guide provides comprehensive instructions for integrating both PostgreSQL and MongoDB with your FastAPI project, including configuration options, code examples, and setup procedures.