# Module Specification: auth

**Version:** 1.0

**Author:** Aviroop

**Date:** 07/08/2025

---

## 1. Purpose and Responsibility

The auth module handles all authentication and authorization functionality in the library management system. It manages user registration, login, JWT token generation and validation, and provides the authentication infrastructure for the entire system. This module is responsible for securing the API endpoints and managing user sessions.

---

## 2. Dependencies

-> Django ORM for database operations
-> Django REST Framework for API endpoints
-> djangorestframework-simplejwt for JWT authentication
-> Django's built-in authentication system
-> User module for user model and profile management

---

## 3. Data Models / Schema

**No specific models in auth app - uses User model from user app**

The auth module leverages the User model from the user app and focuses on authentication logic rather than data storage.

**User Types:**
- **User:** Regular library user with standard permissions
- **Admin:** Administrator with elevated permissions for system management

---

## 4. API Endpoints

**POST /api/auth/register/**
- Purpose: User registration
- Access: Public
- Request body: username, email, password, first_name, last_name, role
- Response: User object with success message
- Note: role field accepts "user" or "admin" values

**POST /api/auth/login/**
- Purpose: User login and JWT token generation
- Access: Public
- Request body: username, password
- Response: Access token, refresh token, user info

**POST /api/auth/refresh/**
- Purpose: Refresh JWT access token
- Access: Authenticated users
- Request body: refresh token
- Response: New access token

**POST /api/auth/logout/**
- Purpose: User logout (invalidate refresh token)
- Access: Authenticated users
- Response: Success message

**POST /api/auth/verify/**
- Purpose: Verify JWT token validity
- Access: Authenticated users
- Response: Token validity status and user info

---

## 5. Services and Business Logic

**AuthService:**
- def register_user(user_data): Creates new user account with validation and role assignment
- def authenticate_user(username, password): Authenticates user and generates JWT
- def generate_jwt_tokens(user): Creates access and refresh tokens with user claims including role
- def validate_jwt_token(token): Validates JWT token and extracts user info
- def refresh_access_token(refresh_token): Generates new access token
- def logout_user(refresh_token): Invalidates refresh token for logout
- def verify_token(token): Verifies token validity and returns user info

**JWT Configuration:**
- Access token expiration: 60 minutes
- Refresh token expiration: 7 days
- Custom claims: user_id, role, exp
- Algorithm: HS256

**Business Rules:**
- JWT tokens include user_id, role, and expiration claims
- Role field is required during registration and must be either "user" or "admin"
- Default role for new registrations is "user" if not specified
- Admin users have elevated permissions for system management
- Refresh tokens are invalidated on logout
- Failed login attempts are logged for security
- Password validation follows Django's default security rules
- Tokens are automatically validated on protected endpoints 