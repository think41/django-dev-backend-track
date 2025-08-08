# Module Specification: `Users`

**Version:** 1.0

**Author:** Gemini

**Date:** 2025-08-01

---

## 1. Purpose and Responsibility

**Description:** This module handles all functionalities related to user management, authentication, and authorization. It is responsible for the user lifecycle, from registration and approval to authentication via JWT.

**Scope:**
-   **IN SCOPE:**
    -   User registration with pending approval.
    -   User authentication (login) and JWT generation.
    -   Admin approval of new user accounts.
    -   Retrieving user information.
-   **OUT OF SCOPE:**
    -   User profile management (e.g., updating email, password changes).
    -   Password reset functionality.
    -   Managing user permissions beyond the `admin`/`member` roles.

---

## 2. Dependencies

-   **`django.contrib.auth`**: Used for the underlying user model and password management.
-   **`djangorestframework-simplejwt`**: Required for generating and validating JWT tokens for authentication.

---

## 3. Data Models / Schema

### 3.1. `User` (Extends Django's AbstractUser)

**Description:** Represents a user of the system, who can be either an administrator or a member.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `username`      | `CharField(150)`                        | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `password`      | `CharField(128)`                        | The hashed password for the user account.                    |
| `email`         | `EmailField`                            | The user's email address. Must be unique.                    |
| `role`          | `CharField(10)`                         | The user's role. Choices are `admin` or `member`.            |
| `is_active`     | `BooleanField`                          | Designates whether this user should be treated as active. Unselect this instead of deleting accounts. Default: `False`. |
| `date_joined`   | `DateTimeField`                         | Timestamp of when the user registered.                       |

---

## 4. API Endpoints

**Base URL:** `/api/users/`

### 4.1. `Authentication` Endpoints

-   **`POST /api/users/register/`**
    -   **Description:** Allows a new user to register for an account. The account is created as inactive and requires admin approval.
    -   **Permissions:** Public
    -   **Request Body:** `{ "username": "string", "password": "string", "email": "string" }`
    -   **Success Response (201 Created):** `{ "message": "Registration successful. Your account is pending approval from an administrator." }`
    -   **Failure Response (400 Bad Request):** If `username` or `email` already exist or data is invalid.

-   **`POST /api/users/login/`**
    -   **Description:** Authenticates an active user and provides JWT access and refresh tokens.
    -   **Permissions:** Public
    -   **Request Body:** `{ "username": "string", "password": "string" }`
    -   **Success Response (200 OK):** `{ "access": "string", "refresh": "string" }`
    -   **Failure Response (401 Unauthorized):** If credentials are invalid or the user's account (`is_active`) is `False`.

### 4.2. `Admin` Endpoints

-   **`GET /api/admin/users/`**
    -   **Description:** Retrieves a list of all users in the system.
    -   **Permissions:** Admin only
    -   **Query Params:** `?is_active=true/false` to filter users by their active status.
    -   **Success Response (200 OK):** `[ { "id": "int", "username": "string", "email": "string", "role": "string", "is_active": "boolean" }, ... ]`

-   **`PATCH /api/admin/users/{id}/approve/`**
    -   **Description:** Approves a user's registration by activating their account.
    -   **Permissions:** Admin only
    -   **Request Body:** (empty)
    -   **Success Response (200 OK):** `{ "message": "User account activated successfully." }`
    -   **Failure Response (404 Not Found):** If the user ID does not exist.

---

## 5. Services and Business Logic

### 5.1. `UserRegistrationService`

-   **Purpose:** To handle the logic for creating a new user account.
-   **Methods:**
    -   `create_user(username, password, email)`: Hashes the provided password, sets the default `role` to `member` and `is_active` to `False`, and saves the new user instance.

### 5.2. `UserActivationService`

-   **Purpose:** To handle the logic for activating a user account.
-   **Methods:**
    -   `activate_user(user_id)`: Finds the user by their ID and sets their `is_active` status to `True`.

---

## 6. Events (Optional)

-   **Publishes:**
    -   `user.registered`: Published when a new user completes the registration form. Carries the `user_id` and `email`.
    -   `user.approved`: Published when an admin approves a user account. Carries the `user_id`.