
## 1. Purpose and Responsibility

The Books module is responsible for managing book inventory in the Library Management System. It provides endpoints for adding, updating, and deleting books, as well as retrieving book details and searching books. Admins manage books through Django's built-in admin panel and API endpoints. This module is part of the Domain Layer, containing the core business entities related to book inventory.

---

## 2. Dependencies

- Django REST Framework for API endpoints
- PostgreSQL database for storage

---

## 3. Data Models / Schema

### Book Model
```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, blank=True, null=True)  # For search functionality
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    # Removed: isbn, published_date, description, updated_at (not required by use_case.md)
```


## 4. API Endpoints

### Public Endpoints

#### Search Books
`/api/books/search/`
- **Method:** `GET`
- **Query Parameters:**
  - `title`: Search by title (optional)
  - `author`: Search by author (optional)
  - `genre`: Filter by genre (optional)
  - `available`: Filter by availability (`true`/`false`, optional)
- **Description:** Allows searching and filtering of books without authentication

#### Get Book Details
`/api/books/{id}/`
- **Method:** `GET`
- **Description:** Retrieves detailed information about a specific book

### Admin Endpoints (via Django Admin Panel)

Admins will use Django's built-in admin panel to:
- Add, update, and delete books
- Manage book inventory and availability
- View book borrowing statistics

#### List All Books (API)
`/api/books/admin/`
- **Method:** `GET`
- **Permission:** `IsAdmin`
- **Description:** Allows admins to view all books in the system

#### Add Book
`/api/books/admin/`
- **Method:** `POST`
- **Permission:** `IsAdmin`
- **Request Body:**
  ```json
  {
    "title": "string",
    "author": "string",
    "genre": "string",
    "total_copies": "integer"
  }
  ```
- **Description:** Allows admins to add a new book to the system

#### Update Book
`/api/books/admin/{id}/`
- **Method:** `PUT/PATCH`
- **Permission:** `IsAdmin`
- **Description:** Allows admins to update book details

#### Delete Book
`/api/books/admin/{id}/`
- **Method:** `DELETE`
- **Permission:** `IsAdmin`
- **Description:** Allows admins to remove a book from the system

---

## 5. Services and Business Logic

### Book Inventory Management
- Books have total_copies and available_copies fields
- When a book is borrowed (approved), available_copies decreases by 1
- When a book is returned, available_copies increases by 1
- Books cannot be borrowed if available_copies is 0

### Search Functionality
- Full-text search on title and author fields
- Filter by genre and availability
- Case-insensitive search

### Admin Operations
- Admins can manage complete book lifecycle through Django admin
- API endpoints provided for programmatic access
- Book availability automatically managed through borrowing workflow
