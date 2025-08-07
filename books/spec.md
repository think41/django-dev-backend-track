# Module Specification: books

**Version:** 1.0

**Author:** Aviroop

**Date:** 07/08/2025

---

## 1. Purpose and Responsibility

The books module is responsible for managing all book-related operations in the library management system. It handles book data storage, retrieval, and basic book management operations. This module serves as the core data store for all book information and provides APIs for book-related functionality.

---

## 2. Dependencies

- Django ORM for database operations
- Django REST Framework for API endpoints
- Auth module for user authentication and role-based access
- User module for user model references

---

## 3. Data Models / Schema

**Book Model:**
- id: Primary key (auto-generated)
- title: CharField (required, max_length=255)
- author: CharField (required, max_length=255)
- isbn: CharField (unique, max_length=13)
- genre: CharField (max_length=100)
- publication_year: IntegerField
- total_copies: IntegerField (default=1)
- available_copies: IntegerField (default=1)
- created_at: DateTimeField (auto_now_add=True)
- updated_at: DateTimeField (auto_now=True)

---

## 4. API Endpoints

**GET /api/books/**
- Purpose: List all books with optional filtering
- Access: Public (for search), Admin (for management)
- Query params: title, author, genre, isbn
- Response: List of book objects

**GET /api/books/{id}/**
- Purpose: Get specific book details
- Access: Public
- Response: Single book object

**POST /api/books/**
- Purpose: Create new book
- Access: Admin only
- Request body: Book data (title, author, isbn, etc.)
- Response: Created book object

**PUT /api/books/{id}/**
- Purpose: Update book information
- Access: Admin only
- Request body: Updated book data
- Response: Updated book object

**DELETE /api/books/{id}/**
- Purpose: Delete book
- Access: Admin only
- Response: Success message

---

## 5. Services and Business Logic

**BookService:**
- def create_book(book_data): Creates new book and validates ISBN uniqueness
- def update_book(book_id, book_data): Updates book and handles copy count validation
- def delete_book(book_id): Deletes book if no active borrows exist
- def search_books(filters): Searches books by various criteria
- def get_book_availability(book_id): Returns available copies count

**Business Rules:**
- ISBN must be unique across all books
- Cannot delete books that are currently borrowed
- Available copies cannot exceed total copies
- Book title and author are required fields 