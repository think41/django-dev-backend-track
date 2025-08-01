# Module Specification: `[Module Name]`

**Version:** 1.0

**Author:** Nandisha D

**Date:** 1/8/2025

---

## 1. Purpose and Responsibility

---

## 2. Dependencies

---

## 3. Data Models / Schema

1. **Role**
2. **User**
3. **Book**
4. **BookCopy**
5. **BookIssue**

---

## 4. API Endpoints

Here is the **updated list of REST API endpoints** including the `PATCH` method where appropriate—used for **partial updates** (like status changes, approval flags, or specific field edits):

---

### 📘 **Roles**

| Method | Endpoint          | Purpose                    |
| ------ | ----------------- | -------------------------- |
| GET    | `/api/roles`      | Get all roles              |
| POST   | `/api/roles`      | Create a new role          |
| PATCH  | `/api/roles/{id}` | Update role name (partial) |

---

### 👤 **Users**

| Method | Endpoint                  | Purpose                            |
| ------ | ------------------------- | ---------------------------------- |
| POST   | `/api/register`           | Register a new user                |
| POST   | `/api/login`              | Login a user                       |
| GET    | `/api/users`              | Get list of all users (admin)      |
| GET    | `/api/users/{id}`         | Get user details                   |
| PUT    | `/api/users/{id}`         | Fully update user info             |
| PATCH  | `/api/users/{id}`         | Partially update user (e.g. email) |
| PATCH  | `/api/users/{id}/approve` | Approve or disapprove a user       |
| DELETE | `/api/users/{id}`         | Delete user                        |

---

### 📚 **Books**

| Method | Endpoint          | Purpose                   |
| ------ | ----------------- | ------------------------- |
| GET    | `/api/books`      | List all books            |
| GET    | `/api/books/{id}` | Get book by ID            |
| POST   | `/api/books`      | Create a new book (admin) |
| PUT    | `/api/books/{id}` | Fully update book details |
| PATCH  | `/api/books/{id}` | Partially update book     |
| DELETE | `/api/books/{id}` | Delete a book (admin)     |

---

### 🔖 **Book Copies**

| Method | Endpoint                     | Purpose                             |
| ------ | ---------------------------- | ----------------------------------- |
| GET    | `/api/books/{id}/copies`     | Get copies of a book                |
| GET    | `/api/book-copies/{copy_id}` | Get specific copy info              |
| POST   | `/api/book-copies`           | Add a new book copy (admin)         |
| PUT    | `/api/book-copies/{copy_id}` | Fully update book copy              |
| PATCH  | `/api/book-copies/{copy_id}` | Partially update copy (e.g. status) |
| DELETE | `/api/book-copies/{copy_id}` | Delete book copy                    |

---

### 📝 **Book Issues**

| Method | Endpoint                        | Purpose                              |
| ------ | ------------------------------- | ------------------------------------ |
| GET    | `/api/book-issues`              | List all book issues                 |
| GET    | `/api/book-issues/{id}`         | View issue details                   |
| POST   | `/api/book-issues`              | Request a book copy                  |
| PUT    | `/api/book-issues/{id}`         | Fully update book issue record       |
| PATCH  | `/api/book-issues/{id}`         | Partially update issue (e.g. status) |
| PATCH  | `/api/book-issues/{id}/approve` | Approve issue request (admin)        |
| PATCH  | `/api/book-issues/{id}/reject`  | Reject issue request (admin)         |
| PATCH  | `/api/book-issues/{id}/return`  | Mark book as returned                |
| DELETE | `/api/book-issues/{id}`         | Cancel/delete issue request          |

---

## 5. Services and Business Logic

---

## ✅ **Project Overview**

```plaintext
lms_project/
├── lms_project/                   # Django project config (settings, root URLs, etc.)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py

├── apps/                          # Custom Django apps
│   ├── users/                     # Handles auth, roles, user approval
│   │   ├── models.py              # User, Role
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── enums.py               # RoleEnum, UserStatus, etc.
│   │   ├── constants.py           # Role choices, error messages, etc.
│   │   └── Readme.md
│
│   └── library/                   # Book, BookCopies, BookIssues logic
│       ├── models.py
│       ├── enums.py               # BookStatusEnum, CopyStatus, etc.
│       ├── constants.py           # e.g., MAX_BORROW_LIMIT, default statuses
│       ├── views/
│       │   ├── __init__.py
│       │   ├── books.py
│       │   ├── book_copies.py
│       │   └── book_issues.py
│       ├── serializers/
│       │   ├── __init__.py
│       │   ├── books.py
│       │   ├── book_copies.py
│       │   └── book_issues.py
│       ├── urls.py
│       ├── filters.py
│       └── Readme.md

├── data/
│   ├── users.csv
│   ├── books.csv
│   ├── book_issues.csv
│   └── Readme.md

├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt

├── Readme.md                      # Project-level docs

└── manage.py
```

---

## 5. DB Schema
