# Module Specification: user

**Version:** 1.0

**Author:** Aviroop

**Date:** 07/08/2025

---

## 1. Purpose and Responsibility

The user module handles user profile management and user-related operations in the library management system. It manages user accounts, roles (admin/member), and provides user profile functionality. This module is responsible for user data management, role-based access control, and user approval workflows.

---

## 2. Dependencies

- Django ORM for database operations
- Django REST Framework for API endpoints
- Auth module for authentication and JWT token validation

---

## 3. Data Models / Schema

**User Model (extends Django AbstractUser):**
- id: Primary key (auto-generated)
- username: CharField (unique, required)
- email: EmailField (unique, required)
- first_name: CharField (max_length=30)
- last_name: CharField (max_length=30)
- role: CharField (choices: 'admin', 'member', default='member')
- is_active: BooleanField (default=True)
- is_approved: BooleanField (default=False) - for member approval workflow
- date_joined: DateTimeField (auto_now_add=True)
- last_login: DateTimeField

---

## 4. API Endpoints

**GET /api/users/**
- Purpose: List all users (admin only)
- Access: Admin only
- Response: List of user objects

**GET /api/users/{id}/**
- Purpose: Get user profile
- Access: Own profile or admin
- Response: User object

**PUT /api/users/{id}/**
- Purpose: Update user profile
- Access: Own profile or admin
- Request body: Updated user data
- Response: Updated user object

**POST /api/users/{id}/approve/**
- Purpose: Approve member registration (admin only)
- Access: Admin only
- Response: Success message

**GET /api/users/me/**
- Purpose: Get current user's profile
- Access: Authenticated users
- Response: Current user object

---

## 5. Services and Business Logic

**UserService:**
- def get_user_profile(user_id): Retrieves user profile with permissions check
- def update_user_profile(user_id, user_data): Updates user profile with validation
- def approve_member(user_id): Approves member registration
- def get_all_users(): Retrieves all users (admin only)
- def get_current_user(request): Gets current authenticated user

**Business Rules:**
- Username and email must be unique
- Members require admin approval before accessing member features
- Only admins can approve member registrations
- Users can only view/edit their own profile (unless admin)
- Role changes require admin privileges 