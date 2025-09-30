# 🚀 Beginner's Guide to Building APIs

A simple, step-by-step guide for beginners to understand how to create APIs using the FastAPI project structure.

## 📚 What You'll Learn

- How to create a simple API from scratch
- What each folder does and when to use it
- Step-by-step examples with real code
- Testing your API endpoints

## 🏗️ Understanding the Project Structure

```
app/
├── main.py           # 🏠 Main app - where everything starts
├── models/           # 🗄️ Database tables (what data looks like)
├── schemas/          # 📋 API input/output (what users send/receive)
├── services/         # 🔧 External services (email, auth, etc.)
├── api/              # 🌐 API endpoints (URLs people can visit)
└── db/               # 💾 Database connection
```

### 🤔 When to Use Each Folder?

| Folder | When to Use | Example |
|--------|-------------|---------|
| `models/` | Define what data looks like in database | User table, Product table |
| `schemas/` | Define what data users send/receive | User registration form, Product info |
| `services/` | Connect to external services | Send emails, Process payments |
| `api/` | Create endpoints (URLs) | `/users`, `/products` |
| `db/` | Database connection | Usually don't touch this |

## 🎯 Example: Building a Simple "Books" API

Let's build a simple API to manage books. Users can:
- ✅ View all books
- ✅ Add a new book
- ✅ Get a specific book
- ✅ Update a book
- ✅ Delete a book

### Step 1: Create the Database Model 📚

**File: `app/models/book.py`**

```python
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base

class Book(Base):
    __tablename__ = "books"

    # Every book has these fields
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)           # Book title (required)
    author = Column(String, nullable=False)          # Author name (required)
    price = Column(Float, nullable=False)            # Book price (required)
    is_available = Column(Boolean, default=True)     # Is book available?
    description = Column(String)                     # Book description (optional)
```

**💡 What this does:**
- Creates a "books" table in the database
- Defines what information each book has
- `nullable=False` means the field is required
- `default=True` means new books are available by default

### Step 2: Create the API Schemas 📝

**File: `app/schemas/book.py`**

```python
from typing import Optional
from pydantic import BaseModel

# What users send when creating a book
class BookCreate(BaseModel):
    title: str
    author: str
    price: float
    description: Optional[str] = None

# What users send when updating a book
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None
    description: Optional[str] = None

# What users receive when getting book info
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    price: float
    is_available: bool
    description: Optional[str] = None

    class Config:
        from_attributes = True  # This makes it work with database models
```

**💡 What this does:**
- `BookCreate`: When someone adds a new book, they send this data
- `BookUpdate`: When someone updates a book, they can change these fields
- `BookResponse`: When someone asks for book info, they get this data back

### Step 3: Generate Database Migration 🔄

```bash
# Import the new model in alembic/env.py
# Add this line: from app.models.book import Book

# Generate migration
alembic revision -m "add books table" --autogenerate

# Apply migration
alembic upgrade head
```

**💡 What this does:**
- Creates the actual "books" table in the database
- Now you can store real book data

### Step 4: Create the API Endpoints 🌐

**File: `app/api/v1/books.py`**

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate, BookResponse

# Create a router for book endpoints
books_router = APIRouter(prefix="/books", tags=["books"])

# GET /api/v1/books - Get all books
@books_router.get("/", response_model=List[BookResponse])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    """Get all books from the database"""
    result = await session.execute(select(Book))
    books = result.scalars().all()
    return books

# GET /api/v1/books/{book_id} - Get a specific book
@books_router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific book by ID"""
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book

# POST /api/v1/books - Create a new book
@books_router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new book"""
    # Create new book from the data user sent
    new_book = Book(
        title=book_data.title,
        author=book_data.author,
        price=book_data.price,
        description=book_data.description
    )

    # Save to database
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)  # Get the ID that was assigned

    return new_book

# PUT /api/v1/books/{book_id} - Update a book
@books_router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update an existing book"""
    # Find the book
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    # Update only the fields that were sent
    update_data = book_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    await session.commit()
    await session.refresh(book)
    return book

# DELETE /api/v1/books/{book_id} - Delete a book
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a book"""
    result = await session.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    await session.delete(book)
    await session.commit()
```

**💡 What each endpoint does:**
- `GET /books/` → Shows all books
- `GET /books/123` → Shows book with ID 123
- `POST /books/` → Creates a new book
- `PUT /books/123` → Updates book with ID 123
- `DELETE /books/123` → Deletes book with ID 123

### Step 5: Register the Router 📋

**File: `app/api/routers.py`**

```python
from fastapi import APIRouter
from app.api.v1.home_router import home_router
from app.api.v1.books import books_router  # Add this import

api_router = APIRouter()
api_router.include_router(home_router)
api_router.include_router(books_router)    # Add this line
```

### Step 6: Test Your API! 🧪

1. **Start the server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **Visit the docs:** http://localhost:8000/docs

3. **Try these URLs:**
   - `GET http://localhost:8000/api/v1/books/` - See all books
   - `POST http://localhost:8000/api/v1/books/` - Add a book
   - `GET http://localhost:8000/api/v1/books/1` - Get book #1

## 🛠️ Using Services (External Integrations)

Let's say you want to send an email when a new book is added:

**File: `app/api/v1/books.py` (updated)**

```python
from app.services.email_service import EmailService

# Update the create_book function
@books_router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new book and send notification email"""
    # Create new book
    new_book = Book(
        title=book_data.title,
        author=book_data.author,
        price=book_data.price,
        description=book_data.description
    )

    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)

    # Send notification email (using service)
    email_service = EmailService(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your-email@gmail.com",
        password="your-password"
    )

    await email_service.send_email(
        to_emails=["admin@bookstore.com"],
        subject="New Book Added!",
        body=f"New book '{new_book.title}' by {new_book.author} has been added!"
    )

    return new_book
```

## 📝 Common Patterns

### 1. Adding Validation

```python
from pydantic import BaseModel, validator

class BookCreate(BaseModel):
    title: str
    author: str
    price: float
    description: Optional[str] = None

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

### 2. Adding Search

```python
@books_router.get("/search", response_model=List[BookResponse])
async def search_books(
    q: str,  # Search query
    session: AsyncSession = Depends(get_session)
):
    """Search books by title or author"""
    result = await session.execute(
        select(Book).where(
            (Book.title.contains(q)) | (Book.author.contains(q))
        )
    )
    books = result.scalars().all()
    return books
```

### 3. Adding Pagination

```python
@books_router.get("/", response_model=List[BookResponse])
async def get_all_books(
    skip: int = 0,      # How many to skip
    limit: int = 10,    # How many to return
    session: AsyncSession = Depends(get_session)
):
    """Get all books with pagination"""
    result = await session.execute(
        select(Book).offset(skip).limit(limit)
    )
    books = result.scalars().all()
    return books
```

## 🎯 Quick Reference

### Database Operations
```python
# Get all
result = await session.execute(select(Book))
books = result.scalars().all()

# Get one by ID
result = await session.execute(select(Book).where(Book.id == book_id))
book = result.scalar_one_or_none()

# Create
new_book = Book(title="New Book", author="Author")
session.add(new_book)
await session.commit()

# Update
book.title = "Updated Title"
await session.commit()

# Delete
await session.delete(book)
await session.commit()
```

### HTTP Status Codes
- `200` - OK (successful GET, PUT)
- `201` - Created (successful POST)
- `204` - No Content (successful DELETE)
- `404` - Not Found
- `400` - Bad Request (validation error)
- `500` - Internal Server Error

## 🚨 Common Mistakes to Avoid

1. **❌ Forgetting to import models in alembic/env.py**
   ```python
   # Add this in alembic/env.py
   from app.models.book import Book
   ```

2. **❌ Not running migrations after creating models**
   ```bash
   alembic revision -m "add books" --autogenerate
   alembic upgrade head
   ```

3. **❌ Forgetting to register router in routers.py**
   ```python
   # Add in app/api/routers.py
   api_router.include_router(books_router)
   ```

4. **❌ Not handling errors**
   ```python
   if not book:
       raise HTTPException(status_code=404, detail="Book not found")
   ```

## 🎉 Congratulations!

You've learned how to:
- ✅ Create database models
- ✅ Define API schemas
- ✅ Build CRUD endpoints
- ✅ Use external services
- ✅ Test your API

### 🔗 Next Steps

- Read [API_DEVELOPMENT.md](./API_DEVELOPMENT.md) for advanced patterns
- Add authentication to your APIs
- Learn about middleware and error handling
- Explore database relationships (foreign keys)

### 🛠️ Practice Projects

1. **Task Manager API** - Create, update, complete tasks
2. **Recipe API** - Store recipes with ingredients
3. **Library API** - Books, authors, borrowing system
4. **Blog API** - Posts, comments, categories

Happy coding! 🚀