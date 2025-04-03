from fastapi import FastAPI
from database import engine, Base
from routes import book,author,publisher,genre, borrow

DEFAULT_PREFIX = "/api"

description = """
## Authors

### Get Author's Books
🔗 `GET /author/{author_id}/books`

📝 **Behavior**:
- Returns all books by specified author
- Returns empty list if no books found
- Response includes full book details with author/genre relationships

### Create Author
🔗 `POST /author/`

📝 **Validations**:
- **Name Uniqueness**: Author name must not exist already (400 if duplicate)
- **Birth Date**: Must be in the past (auto-converts to UTC if naive datetime)
- **Database Integrity**: Atomic transaction with rollback on failure

📝 **Error Responses**:
- 400: Author with same name already exists
- 500: Database operation failed (with automatic rollback)


## Books

### Get All Books
🔗 `GET /books`

📝 **Features & Validations**:
- Pagination support with `limit` (1-100) and `offset` (≥0)
- Sorting by `title`, `publish_date`, or `author` name
- Order direction (`asc` or `desc`)
- Automatic joins with authors for sorting
- Returns 200 even with empty results

### Create Book
🔗 `POST /books/`

📝 **Validations**:
- **ISBN Format**: Must match `^[0-9]{1,5}-[0-9]{1,7}-[0-9]{1,5}-[0-9X]$`
- **Publish Date**: Must be in the past (UTC timezone enforced)
- **Author Check**: Author must exist (404 if not found)
- **Genre Verification**: All genre IDs must exist (404 if any missing)
- **Database Integrity**: Atomic transactions with rollback on failure

### Get Book History
🔗 `GET /books/{book_id}/history`

📝 **Behavior**:
- Returns complete borrow/return history for a book
- 404 if book doesn't exist
- Empty arrays if no history exists
- Includes timestamps for all transactions

## Genres

### Get All Genres
🔗 `GET /genres/`

📝 **Features & Validations**:
- Pagination support with `limit` (1-100) and `offset` (≥0)
- Returns 200 status even with empty results
- Response includes basic genre information

### Create Genre
🔗 `POST /genres/`

📝 **Validations**:
- **Name Uniqueness**: Genre name must not exist already (400 if duplicate)
- **Database Integrity**: Atomic transaction with rollback on failure

📝 **Error Responses**:
- 400: Genre with same name already exists
- 500: Database operation failed (with automatic rollback)


## Publishers

### Get All Publishers
🔗 `GET /publishers/`

📝 **Features & Validations**:
- Pagination support with `limit` (1-100) and `offset` (≥0)
- Returns 200 status even with empty results
- Response includes basic publisher information

### Create Publisher
🔗 `POST /publishers/`

📝 **Validations**:
- **Name Uniqueness**: Publisher name must not exist already (400 if duplicate)
- **Database Integrity**: Atomic transaction with rollback on failure

📝 **Error Responses**:
- 400: Publisher with same name already exists
- 500: Database operation failed (with automatic rollback)

## Borrowing System

### Borrow a Book
🔗 `POST /borrow/`

📝 **Validations**:
- **Book Existence**: Book must exist (404 if not found)
- **Availability**: Book must not be currently borrowed (400 if unavailable)
- **Borrow Limit**: User can't exceed maximum borrow count (currently 3)

📝 **Error Responses**:
- 400: Book already borrowed or user limit reached
- 404: Book not found
- 500: Database operation failed (with rollback)

### Return a Book
🔗 `POST /return/`
📝 **Validations**:
- **Borrow Record**: Must find matching active borrow record (404 if none)
- **Database Integrity**: Updates borrow status and creates return record atomically

📝 **Error Responses**:
- 404: No active borrow found for this book/user combination
- 500: Database operation failed (with rollback)
"""

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library API", description=description)

app.include_router(book.router, prefix=DEFAULT_PREFIX, tags=["Books"])
app.include_router(author.router, prefix=DEFAULT_PREFIX, tags=['Authors'])
app.include_router(publisher.router, prefix=DEFAULT_PREFIX, tags=['Publishers'])
app.include_router(genre.router, prefix=DEFAULT_PREFIX, tags=['Genre'])
app.include_router(borrow.router, prefix=DEFAULT_PREFIX, tags=['Borrow'])
