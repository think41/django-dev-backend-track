# Module Specification: `library`

**Version:** 1.0

**Author:** Sherbin S

**Date:** 01-08-2025

---

## 1. Purpose and Responsibility
 The `library` module is responsible for managing the library system, including book management, user borrowing, and returning books. It provides endpoints for book creation, updating, deleting, and borrowing books.

---

## 2. Dependencies

asgiref<br />
Django<br />
psycopg2-binary<br />
sqlparse<br />
tzdata<br />
djangorestframework<br />
---

## 3. Data Models / Schema

**Class Book**:<br />
    id<br />
    title<br />
    author<br />
    published_date<br />
    available_copies<br />
    total_copies<br />
    created_at<br />
    updated_at<br />

**Class BorrowRecord**:<br />
    id<br />
    user_id<br />
    book_id<br />
    borrow_date<br />
    return_date<br />
    status (e.g., borrowed, returned)<br />
    created_at<br />
    updated_at<br />

---

## 4. API Endpoints
### Book Management

Method: POST library/books/<br />
Description: Creates a new book entry.<br />
Request Body:
```json
{
    "title": "string",
    "author": "string",
    "published_date": "YYYY-MM-DD",
    "total_copies": 0
}
```

Method: GET library/book/{title}<br />
Description: Retrieves a book by its title.<br />
Request Parameters:
```json
{
    "title": "string"
}
```

Method: Post library/book/borrow/<br />
Description: Allows a user to borrow a book.<br />
Request Body:
```json
{
    "user_id": "integer",
    "book_id": "integer",
    "borrow_date": "YYYY-MM-DD",
    "return_date": "YYYY-MM-DD",
    "status": "string"
}
```
---

## 5. Services and Business Logic

## LibraryService
 service handles the business logic for managing books, including creating, updating, deleting, and borrowing books. It interacts with the database to perform these operations and ensures that the business rules are followed, such as checking if a book is available before allowing it to be borrowed.
 
