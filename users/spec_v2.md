# Module Specification: `Users` v2.0

**Version:** 2.0

**Author:** Library Management System Team

**Date:** 2025-08-08

**Previous Version:** v1.0 (Basic user management with registration, authentication, and admin approval)

---

## 1. Purpose and Responsibility

**Description:** This module handles all functionalities related to user management, authentication, authorization, and fine management. It is responsible for the complete user lifecycle, from registration and approval to authentication via JWT, and managing user-related financial obligations.

**Scope:**
-   **IN SCOPE:**
    -   Fine management system (NEW)
    -   User profile management (NEW)
    -   Password reset functionality (NEW)
    -   User activity tracking for reports (NEW)
    -   Membership management (NEW)
    -   Enhanced user validation (NEW)
-   **OUT OF SCOPE:**
    -   Managing user permissions beyond the `admin`/`member` roles
    -   Social authentication (OAuth, etc.)

---

## 2. Dependencies

-   **`django.contrib.auth`**: Used for the underlying user model and password management.
-   **`djangorestframework-simplejwt`**: Required for generating and validating JWT tokens for authentication.
-   **`books` module**: For fine calculations based on borrowing activities.
-   **`reports` module**: For user activity tracking and report generation.
-   **`celery`**: For background tasks like fine calculations and notifications.
-   **`django-email-verification`**: For email verification functionality.
-   **`Pillow`**: For profile image processing.

---

## 3. Data Models / Schema

### 3.1. `User` (Extends Django's AbstractUser) - ENHANCED

**Description:** Represents a user of the system, who can be either an administrator or a member. Enhanced with additional fields for v2.0.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `username`      | `CharField(150)`                        | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `password`      | `CharField(128)`                        | The hashed password for the user account.                    |
| `email`         | `EmailField`                            | The user's email address. Must be unique.                    |
| `first_name`    | `CharField(150)`                        | User's first name.                                           |
| `last_name`     | `CharField(150)`                        | User's last name.                                            |
| `role`          | `CharField(10)`                         | The user's role. Choices are `admin` or `member`.            |
| `is_active`     | `BooleanField`                          | Designates whether this user should be treated as active. Default: `False`. |
| `date_joined`   | `DateTimeField`                         | Timestamp of when the user registered.                       |
| `phone_number`  | `CharField(15)`                         | User's phone number (NEW).                                   |
| `address`       | `TextField`                             | User's address (NEW).                                        |
| `membership_expiry` | `DateField`                         | Date when membership expires (NEW).                          |
| `total_fines_paid` | `DecimalField(10,2)`                | Total amount of fines paid by user (NEW).                    |
| `profile_image` | `ImageField`                            | User's profile picture (NEW).                                |
| `date_of_birth` | `DateField`                             | User's date of birth (NEW).                                  |
| `emergency_contact` | `CharField(15)`                     | Emergency contact number (NEW).                              |
| `preferred_language` | `CharField(10)`                     | User's preferred language (NEW).                             |
| `notification_preferences` | `JSONField`                        | JSON object storing notification preferences (NEW).          |
| `last_login`    | `DateTimeField`                         | Last login timestamp (existing Django field).                |

### 3.2. `Fine` - NEW MODEL

**Description:** Tracks fines imposed on users for overdue books or other violations.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user who is fined.                                       |
| `borrow_record` | `ForeignKey` to `BorrowRecord`          | The borrow record associated with the fine.                  |
| `amount`        | `DecimalField(10,2)`                    | The fine amount in currency units.                           |
| `reason`        | `CharField(100)`                        | Reason for the fine (e.g., "Overdue", "Damaged Book").       |
| `status`        | `CharField(20)`                         | Fine status. Choices: `PENDING`, `PAID`, `WAIVED`. Default: `PENDING`. |
| `due_date`      | `DateField`                             | Date by which the fine should be paid.                       |
| `paid_date`     | `DateField`                             | Date when the fine was paid. Null until paid.                |
| `payment_method` | `CharField(50)`                        | Method used for payment (NEW).                               |
| `payment_reference` | `CharField(100)`                     | Payment reference number (NEW).                              |
| `waived_by`     | `ForeignKey` to `User`                  | Admin who waived the fine (NEW).                             |
| `waived_reason` | `TextField`                             | Reason for waiving the fine (NEW).                           |
| `created_at`    | `DateTimeField`                         | Timestamp of when the fine was created.                      |
| `updated_at`    | `DateTimeField`                         | Timestamp of the last update.                                |

### 3.3. `UserActivity` - NEW MODEL

**Description:** Tracks user activities for reporting purposes.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user who performed the activity.                         |
| `activity_type` | `CharField(50)`                         | Type of activity (e.g., "LOGIN", "REGISTER", "BORROW_REQUEST"). |
| `description`   | `TextField`                             | Description of the activity.                                 |
| `ip_address`    | `GenericIPAddressField`                 | IP address of the user when activity occurred.               |
| `user_agent`    | `TextField`                             | User agent string from the request.                          |
| `session_id`    | `CharField(100)`                        | Session identifier (NEW).                                    |
| `device_type`   | `CharField(20)`                         | Type of device used (NEW).                                   |
| `location`      | `CharField(100)`                        | Geographic location (NEW).                                   |
| `created_at`    | `DateTimeField`                         | Timestamp of when the activity occurred.                     |

### 3.4. `PasswordResetToken` - NEW MODEL

**Description:** Manages password reset tokens for secure password recovery.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user requesting password reset.                          |
| `token`         | `CharField(255)`                        | Unique token for password reset.                             |
| `expires_at`    | `DateTimeField`                         | When the token expires.                                      |
| `used`          | `BooleanField`                          | Whether the token has been used.                             |
| `created_at`    | `DateTimeField`                         | When the token was created.                                  |

### 3.5. `MembershipHistory` - NEW MODEL

**Description:** Tracks membership changes and renewals.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `PK`                                    | The primary key.                                             |
| `user`          | `ForeignKey` to `User`                  | The user whose membership changed.                           |
| `action`        | `CharField(50)`                         | Action taken (e.g., "RENEWED", "EXTENDED", "SUSPENDED").     |
| `old_expiry`    | `DateField`                             | Previous membership expiry date.                             |
| `new_expiry`    | `DateField`                             | New membership expiry date.                                  |
| `performed_by`  | `ForeignKey` to `User`                  | Admin who performed the action.                              |
| `reason`        | `TextField`                             | Reason for the membership change.                            |
| `created_at`    | `DateTimeField`                         | When the change was made.                                    |

---

## 4. API Endpoints

**Base URL:** `/api/users/`

### 4.1. `Password Reset` Endpoints (NEW)

-   **`POST /api/users/password-reset/`**
    -   **Description:** Initiates password reset process by sending email to user.
    -   **Permissions:** Public
    -   **Request Body:** `{ "email": "string" }`
    -   **Success Response (200 OK):** `{ "message": "Password reset email sent." }`
    -   **Error Response (400 Bad Request):** `{ "error": "Email not found." }`
    -   **Error Response (429 Too Many Requests):** `{ "error": "Too many reset attempts. Try again later." }`

-   **`POST /api/users/password-reset-confirm/`**
    -   **Description:** Confirms password reset with token and sets new password.
    -   **Permissions:** Public
    -   **Request Body:** `{ "token": "string", "new_password": "string", "confirm_password": "string" }`
    -   **Success Response (200 OK):** `{ "message": "Password reset successful." }`
    -   **Error Response (400 Bad Request):** `{ "error": "Invalid or expired token." }`

-   **`POST /api/users/password-reset-validate/`**
    -   **Description:** Validates a password reset token without changing password.
    -   **Permissions:** Public
    -   **Request Body:** `{ "token": "string" }`
    -   **Success Response (200 OK):** `{ "valid": true, "user_email": "string" }`
    -   **Error Response (400 Bad Request):** `{ "valid": false, "error": "Invalid or expired token." }`

### 4.2. `User Profile` Endpoints (NEW)

-   **`GET /api/users/profile/`**
    -   **Description:** Retrieves the current user's profile information.
    -   **Permissions:** Authenticated users
    -   **Success Response (200 OK):** `{ "id": "int", "username": "string", "email": "string", "first_name": "string", "last_name": "string", "role": "string", "phone_number": "string", "address": "string", "membership_expiry": "date", "total_fines_paid": "decimal", "profile_image": "string", "date_of_birth": "date", "emergency_contact": "string", "preferred_language": "string", "notification_preferences": "object" }`

-   **`PUT /api/users/profile/`**
    -   **Description:** Updates the current user's profile information.
    -   **Permissions:** Authenticated users
    -   **Request Body:** `{ "first_name": "string", "last_name": "string", "phone_number": "string", "address": "string", "emergency_contact": "string", "preferred_language": "string", "notification_preferences": "object" }`
    -   **Success Response (200 OK):** `{ "id": "int", ... }`
    -   **Error Response (400 Bad Request):** `{ "error": "Invalid phone number format." }`

-   **`POST /api/users/profile/upload-image/`**
    -   **Description:** Uploads a profile image for the current user.
    -   **Permissions:** Authenticated users
    -   **Request Body:** Form data with image file
    -   **Success Response (200 OK):** `{ "message": "Profile image uploaded successfully.", "image_url": "string" }`
    -   **Error Response (400 Bad Request):** `{ "error": "Invalid image format." }`

-   **`POST /api/users/change-password/`**
    -   **Description:** Allows users to change their password.
    -   **Permissions:** Authenticated users
    -   **Request Body:** `{ "current_password": "string", "new_password": "string", "confirm_password": "string" }`
    -   **Success Response (200 OK):** `{ "message": "Password changed successfully." }`
    -   **Error Response (400 Bad Request):** `{ "error": "Current password is incorrect." }`

### 4.3. `Enhanced Admin` Endpoints (NEW)

-   **`GET /api/users/admin/users/`** (ENHANCED)
    -   **Description:** Retrieves a list of all users in the system with enhanced filtering.
    -   **Permissions:** Admin only
    -   **Query Params:** `?is_active=true/false&role=admin/member&has_fines=true/false&membership_expired=true/false&search=string&sort_by=field&order=asc/desc&page=int&page_size=int`
    -   **Success Response (200 OK):** `{ "count": "int", "next": "string", "previous": "string", "results": [ { "id": "int", "username": "string", "email": "string", "role": "string", "is_active": "boolean", "membership_expiry": "date", "total_fines_paid": "decimal", "outstanding_fines": "decimal", "last_login": "datetime" }, ... ] }`

-   **`PATCH /api/users/admin/users/{id}/suspend/`**
    -   **Description:** Suspends a user account (sets is_active to False).
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "reason": "string", "duration_days": "int" }`
    -   **Success Response (200 OK):** `{ "message": "User account suspended successfully.", "suspension_end": "datetime" }`

-   **`PATCH /api/users/admin/users/{id}/reactivate/`**
    -   **Description:** Reactivates a suspended user account.
    -   **Permissions:** Admin only
    -   **Success Response (200 OK):** `{ "message": "User account reactivated successfully." }`

-   **`PATCH /api/users/admin/users/{id}/extend-membership/`**
    -   **Description:** Extends a user's membership expiry date.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "extension_days": "int", "reason": "string" }`
    -   **Success Response (200 OK):** `{ "message": "Membership extended successfully.", "new_expiry": "date" }`

-   **`GET /api/users/admin/users/{id}/membership-history/`**
    -   **Description:** Retrieves membership history for a specific user.
    -   **Permissions:** Admin only
    -   **Success Response (200 OK):** `[ { "id": "int", "action": "string", "old_expiry": "date", "new_expiry": "date", "performed_by": "string", "reason": "string", "created_at": "datetime" }, ... ]`

### 4.4. `Fine Management` Endpoints (NEW)

-   **`GET /api/users/fines/`**
    -   **Description:** Retrieves fines for the current user.
    -   **Permissions:** Authenticated users
    -   **Query Params:** `?status=PENDING/PAID/WAIVED&sort_by=created_at/amount/due_date&order=asc/desc&page=int&page_size=int`
    -   **Success Response (200 OK):** `{ "count": "int", "next": "string", "previous": "string", "results": [ { "id": "int", "amount": "decimal", "reason": "string", "status": "string", "due_date": "date", "created_at": "datetime", "book_title": "string" }, ... ] }`

-   **`GET /api/users/fines/summary/`**
    -   **Description:** Retrieves fine summary for the current user.
    -   **Permissions:** Authenticated users
    -   **Success Response (200 OK):** `{ "total_pending": "decimal", "total_paid": "decimal", "total_waived": "decimal", "overdue_fines": "int", "payment_deadline": "date" }`

-   **`GET /api/users/admin/fines/`**
    -   **Description:** Retrieves all fines in the system (admin view).
    -   **Permissions:** Admin only
    -   **Query Params:** `?status=PENDING/PAID/WAIVED&user_id=int&overdue=true/false&date_from=date&date_to=date&min_amount=decimal&max_amount=decimal&sort_by=field&order=asc/desc&page=int&page_size=int`
    -   **Success Response (200 OK):** `{ "count": "int", "next": "string", "previous": "string", "results": [ { "id": "int", "user": { ... }, "amount": "decimal", "reason": "string", "status": "string", "due_date": "date", "days_overdue": "int" }, ... ] }`

-   **`POST /api/users/admin/fines/`**
    -   **Description:** Creates a new fine for a user.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "user_id": "int", "borrow_record_id": "int", "amount": "decimal", "reason": "string", "due_date": "date" }`
    -   **Success Response (201 Created):** `{ "id": "int", "user": { ... }, "amount": "decimal", "reason": "string", "status": "string", "due_date": "date" }`

-   **`PATCH /api/users/admin/fines/{id}/waive/`**
    -   **Description:** Waives a fine (sets status to WAIVED).
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "reason": "string" }`
    -   **Success Response (200 OK):** `{ "message": "Fine waived successfully.", "waived_amount": "decimal" }`

-   **`POST /api/users/admin/fines/{id}/pay/`**
    -   **Description:** Marks a fine as paid.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "payment_method": "string", "payment_reference": "string", "amount_paid": "decimal" }`
    -   **Success Response (200 OK):** `{ "message": "Fine marked as paid successfully.", "payment_date": "date" }`

-   **`GET /api/users/admin/fines/statistics/`**
    -   **Description:** Retrieves fine statistics for reporting.
    -   **Permissions:** Admin only
    -   **Query Params:** `?start_date=date&end_date=date&group_by=day/week/month`
    -   **Success Response (200 OK):** `{ "total_fines": "decimal", "total_paid": "decimal", "total_waived": "decimal", "overdue_fines": "int", "payment_rate": "decimal", "daily_stats": [ ... ], "top_fine_reasons": [ ... ] }`

### 4.5. `Activity Tracking` Endpoints (NEW)

-   **`GET /api/users/admin/activities/`**
    -   **Description:** Retrieves user activities for reporting.
    -   **Permissions:** Admin only
    -   **Query Params:** `?user_id=int&activity_type=string&start_date=date&end_date=date&page=int&page_size=int`
    -   **Success Response (200 OK):** `{ "count": "int", "next": "string", "previous": "string", "results": [ { "id": "int", "user": { ... }, "activity_type": "string", "description": "string", "ip_address": "string", "device_type": "string", "created_at": "datetime" }, ... ] }`

-   **`GET /api/users/admin/activities/statistics/`**
    -   **Description:** Retrieves activity statistics for reporting.
    -   **Permissions:** Admin only
    -   **Query Params:** `?start_date=date&end_date=date`
    -   **Success Response (200 OK):** `{ "total_activities": "int", "unique_users": "int", "activity_by_type": { ... }, "activity_by_day": [ ... ], "most_active_users": [ ... ] }`

---

## 5. Services and Business Logic

### 5.1. `FineManagementService` (NEW)

-   **Purpose:** To handle fine-related business logic.
-   **Methods:**
    -   `calculate_overdue_fine(borrow_record)`: Calculates fine amount for overdue book based on library policy.
    -   `create_fine(user, borrow_record, amount, reason)`: Creates a new fine record with validation.
    -   `process_fine_payment(fine, payment_method, reference, amount_paid)`: Processes fine payment with receipt generation.
    -   `waive_fine(fine, reason, waived_by)`: Waives a fine with audit trail.
    -   `get_user_total_fines(user)`: Gets total fines for a user (pending, paid, waived).
    -   `check_overdue_books(user)`: Checks for overdue books and creates fines automatically.
    -   `generate_fine_notification(user, fine)`: Generates fine notification for user via email/SMS.
    -   `calculate_fine_statistics(start_date, end_date)`: Calculates fine statistics for reporting.
    -   `process_bulk_fine_operations(operation_type, fine_ids, **kwargs)`: Processes bulk fine operations.

### 5.2. `UserActivityService` (NEW)

-   **Purpose:** To track user activities for reporting and analytics.
-   **Methods:**
    -   `log_activity(user, activity_type, description, request)`: Logs user activity with request metadata.
    -   `get_user_activities(user, start_date, end_date)`: Retrieves user activities for reporting.
    -   `get_new_members_count(start_date, end_date)`: Gets count of new members for reports.
    -   `get_user_activity_statistics(start_date, end_date)`: Gets activity statistics for reporting.
    -   `cleanup_old_activities(days_to_keep)`: Removes old activity records for data management.
    -   `export_activity_data(start_date, end_date, format)`: Exports activity data in various formats.
    -   `detect_suspicious_activity(user)`: Detects unusual user activity patterns.

### 5.3. `PasswordResetService` (NEW)

-   **Purpose:** To handle password reset functionality securely.
-   **Methods:**
    -   `send_reset_email(email)`: Sends password reset email with secure token.
    -   `validate_reset_token(token)`: Validates reset token without changing password.
    -   `reset_password(token, new_password)`: Resets user password with token validation.
    -   `generate_reset_token(user)`: Generates a secure reset token.
    -   `cleanup_expired_tokens()`: Removes expired password reset tokens.
    -   `rate_limit_reset_attempts(email)`: Implements rate limiting for reset attempts.

### 5.4. `MembershipManagementService` (NEW)

-   **Purpose:** To handle membership-related operations.
-   **Methods:**
    -   `validate_membership_expiry(user)`: Checks if user's membership has expired.
    -   `extend_membership(user, days, reason, performed_by)`: Extends user's membership with audit trail.
    -   `suspend_membership(user, reason, duration, performed_by)`: Suspends user membership temporarily.
    -   `reactivate_membership(user, performed_by)`: Reactivates suspended membership.
    -   `get_membership_history(user)`: Gets complete membership history.
    -   `send_expiry_notifications()`: Sends notifications for expiring memberships.
    -   `calculate_membership_statistics()`: Calculates membership statistics for reporting.

### 5.5. `UserProfileService` (NEW)

-   **Purpose:** To handle user profile management operations.
-   **Methods:**
    -   `update_profile(user, profile_data)`: Updates user profile with validation.
    -   `upload_profile_image(user, image_file)`: Uploads and processes profile image.
    -   `validate_phone_number(phone_number)`: Validates phone number format.
    -   `update_notification_preferences(user, preferences)`: Updates user notification preferences.
    -   `get_profile_statistics()`: Gets profile completion statistics.
    -   `export_user_data(user)`: Exports user data for GDPR compliance.

---

## 6. Code Changes Required

### 6.1. Model Changes

**File: `users/models.py`**
- Add new fields to User model: `phone_number`, `address`, `membership_expiry`, `total_fines_paid`, `profile_image`, `date_of_birth`, `emergency_contact`, `preferred_language`, `notification_preferences`
- Create new models: `Fine`, `UserActivity`, `PasswordResetToken`, `MembershipHistory`
- Add model methods for fine calculations, membership validation, and activity tracking
- Add custom managers for fine and activity queries
- Add model validation methods for phone numbers and addresses

### 6.2. Serializer Changes

**File: `users/serializers.py`**
- Create `UserProfileSerializer` for profile management with nested serialization
- Create `FineSerializer` for fine management with user and borrow record details
- Create `PasswordResetSerializer` for password reset with token validation
- Create `MembershipHistorySerializer` for membership tracking
- Create `UserActivitySerializer` for activity logging
- Create `FineStatisticsSerializer` for reporting
- Update existing serializers to include new fields and validation
- Add custom validation methods for phone numbers, addresses, and fine amounts

### 6.3. View Changes

**File: `users/views.py`**
- Add profile management views with image upload functionality
- Add fine management views with bulk operations
- Add password reset views with rate limiting
- Add membership management views with audit trails
- Add activity tracking views with filtering and pagination
- Add statistics endpoints for reporting
- Update existing views to handle new fields and validations
- Add activity logging to existing views
- Implement proper error handling and response formatting

### 6.4. Service Changes

**File: `users/services.py`**
- Add new service classes: `FineManagementService`, `UserActivityService`, `PasswordResetService`, `MembershipManagementService`, `UserProfileService`
- Update existing services to handle new functionality
- Add background task integration for fine calculations
- Add email notification services
- Add data export functionality
- Add rate limiting and security measures

### 6.5. URL Changes

**File: `users/urls.py`**
- Add new URL patterns for profile management, fines, password reset, membership, and activity tracking
- Implement proper URL versioning for API endpoints
- Add nested URL patterns for fine operations
- Add bulk operation endpoints

### 6.6. Admin Changes

**File: `users/admin.py`**
- Register new models in Django admin with custom admin classes
- Add admin actions for fine management (bulk waive, bulk payment)
- Add filters and search for new fields
- Add custom admin views for statistics
- Add export functionality for user data
- Add audit trail display for membership changes

### 6.7. Celery Tasks

**File: `users/tasks.py`** (NEW)
- Create task for automatic fine calculation for overdue books
- Create task for membership expiry notifications
- Create task for password reset email sending
- Create task for user activity cleanup (old records)
- Create task for fine payment reminders
- Create task for suspicious activity detection
- Create task for data export operations

### 6.8. Middleware Changes

**File: `users/middleware.py`** (NEW)
- Create activity tracking middleware
- Create rate limiting middleware for password reset
- Create user session management middleware
- Create fine calculation middleware for overdue books

---

## 7. Events (Optional)

-   **Publishes:**
    -   `fine.created`: When a new fine is created. Carries `fine_id`, `user_id`, `amount`, `reason`.
    -   `fine.paid`: When a fine is paid. Carries `fine_id`, `user_id`, `amount`, `payment_method`.
    -   `fine.waived`: When a fine is waived. Carries `fine_id`, `user_id`, `amount`, `waived_by`.
    -   `membership.extended`: When membership is extended. Carries `user_id`, `old_expiry`, `new_expiry`, `performed_by`.
    -   `membership.suspended`: When membership is suspended. Carries `user_id`, `reason`, `duration`.
    -   `membership.reactivated`: When membership is reactivated. Carries `user_id`, `performed_by`.
    -   `user.activity`: When user performs any tracked activity. Carries `user_id`, `activity_type`, `ip_address`.
    -   `password.reset.requested`: When password reset is requested. Carries `user_id`, `email`.
    -   `password.reset.completed`: When password reset is completed. Carries `user_id`.

---

## 8. Integration Points

### 8.1. Books Module Integration
- Fine creation triggered by overdue book returns
- User suspension affects borrowing privileges
- Membership expiry affects borrowing privileges
- Activity tracking for borrowing operations

### 8.2. Reports Module Integration
- User activity data for weekly reports
- Fine statistics for financial reports
- Membership statistics for user reports
- Password reset statistics for security reports

### 8.3. Celery Tasks
- Automatic fine calculation for overdue books
- Membership expiry notifications
- Password reset email sending
- User activity cleanup (old records)
- Fine payment reminders
- Suspicious activity detection

### 8.4. External Services
- Email service for notifications
- SMS service for urgent notifications
- File storage service for profile images
- Analytics service for user behavior tracking

---

## 9. Configuration Requirements

### 9.1. Settings Updates
- Fine calculation rates and rules (daily rate, maximum fine, grace period)
- Membership duration settings (default duration, renewal policies)
- Password reset email configuration (template, expiry time, rate limiting)
- Activity tracking settings (retention period, sensitive activities)
- Notification preferences (email, SMS, push notifications)
- File upload settings (image size limits, allowed formats)
- Rate limiting settings (password reset, login attempts)

### 9.2. Environment Variables
- Email service configuration (SMTP settings, API keys)
- Fine calculation parameters (rates, policies, currencies)
- Membership policy settings (durations, renewal rules)
- File storage configuration (AWS S3, local storage)
- Notification service API keys
- Analytics service configuration

### 9.3. Database Configuration
- Indexes for fine queries (user_id, status, due_date)
- Indexes for activity tracking (user_id, created_at, activity_type)
- Indexes for membership history (user_id, created_at)
- Partitioning for large activity tables

---

## 10. Testing Requirements

### 10.1. Unit Tests
- Fine calculation logic with various scenarios
- Membership validation and extension logic
- Password reset flow with token validation
- User activity tracking and logging
- Profile image upload and processing
- Phone number and address validation
- Notification preference handling

### 10.2. Integration Tests
- Fine creation from overdue books
- User suspension effects on borrowing
- Report generation with user data
- Email notification delivery
- File upload and storage
- Rate limiting functionality
- Bulk operations on fines

### 10.3. API Tests
- All new endpoints with proper authentication
- Permission validation for admin operations
- Error handling scenarios (invalid data, missing fields)
- Rate limiting and throttling
- File upload endpoints
- Bulk operation endpoints
- Statistics and reporting endpoints

### 10.4. Performance Tests
- Fine calculation performance with large datasets
- Activity tracking performance under load
- User search and filtering performance
- Bulk fine operations performance
- Report generation performance

### 10.5. Security Tests
- Password reset token security
- Fine manipulation prevention
- User data access control
- Rate limiting effectiveness
- Input validation and sanitization
- SQL injection prevention
- XSS protection

---

## 11. Deployment Considerations

### 11.1. Database Migrations
- Careful migration strategy for adding new fields to User model
- Data migration for existing users (default values, membership expiry)
- Index creation for performance optimization
- Partitioning strategy for activity tables

### 11.2. Background Tasks
- Celery worker configuration for fine calculations
- Task queue monitoring and alerting
- Failed task handling and retry logic
- Task scheduling for periodic operations

### 11.3. File Storage
- Profile image storage configuration
- Image processing and optimization
- Backup and recovery procedures
- CDN integration for image delivery

### 11.4. Monitoring and Logging
- Fine calculation monitoring
- User activity tracking
- Performance metrics collection
- Error tracking and alerting
- Audit trail maintenance

---

## 12. Documentation Requirements

### 12.1. API Documentation
- Complete OpenAPI/Swagger documentation
- Request/response examples for all endpoints
- Error code documentation
- Authentication and authorization details
- Rate limiting information

### 12.2. User Documentation
- Fine payment instructions
- Password reset process
- Profile management guide
- Membership renewal process
- Notification preferences setup

### 12.3. Admin Documentation
- Fine management procedures
- User suspension guidelines
- Membership extension policies
- Activity monitoring tools
- Report generation instructions

---

## 13. Future Enhancements

### 13.1. Advanced Features
- Multi-factor authentication
- Social login integration
- Advanced user analytics
- Automated fine collection
- User behavior prediction
- Advanced notification system

### 13.2. Performance Optimizations
- Database query optimization
- Caching strategies
- Background job optimization
- API response optimization
- File storage optimization

### 13.3. Security Enhancements
- Advanced rate limiting
- Fraud detection
- Security audit logging
- Data encryption
- Privacy compliance features 