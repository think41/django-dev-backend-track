# Library Management System v2.0

## Version History

*   **v1.0:** Initial requirements for core functionality (book management, user roles, borrowing).
*   **v2.0:** Introduction of new features like fine management, book reservations, and an enhanced book model.

## Requirements

*   **Backend Framework:** Django
*   **Authentication:** JWT (JSON Web Tokens)
    *   The JWT payload must include the following claims:
        *   `user_id`: The unique identifier of the user.
        *   `role`: The user's role (`'admin'` or `'member'`).
        *   `exp`: The token's expiration timestamp.
*   **Database:** postgres (for development)
*   **Roles:**
    *   **Admin:** Add/remove books, approve member registrations.
    *   **Member:** Search, borrow, return books.
*   **Module Specifications:** Each Django app (module) must contain a `spec.md` file detailing its purpose, models, API endpoints, and business logic.

## Architectural Approach: Layered Architecture

To ensure a robust and maintainable system, we will adopt a Layered Architecture. This approach enforces strict separation of concerns by organizing the code into four distinct layers. 

### The Four Layers

1.  **Presentation Layer:** The outermost layer. Governs all user interactions and external interfaces. In our case, this is our REST API.
2.  **Application Layer:** Orchestrates the use cases of the application. It contains the application-specific business rules and serves as a controller, directing the flow of data between the Presentation and Domain layers.
3.  **Domain Layer:** The heart of the software. Contains the enterprise-wide business rules, entities, and logic that are independent of any specific application. This layer has no dependencies on any other layer.
4.  **Infrastructure Layer:** The innermost layer. Provides the technical services and integrations, such as databases, external APIs, and the file system. It implements the interfaces defined by the layers above it.


## Milestone 1: Project Setup & Database Schema

*   [ ] Initialize a new Django project.
*   [ ] Create a required Django apps/modules
*   [ ] Create `spec.md` files for each app/module, detailing their responsibilities.
*   [ ] Define required Django models.
*   [ ] Generate and run database migrations to create the tables.
*   [ ] Load the sample data from the CSV file into the database.

## Milestone 2: Authentication & Authorization

*   [ ] Set up Django REST Framework.
*   [ ] Set up `djangorestframework-simplejwt` for JWT authentication.
*   [ ] Implement user registration (sign-up) endpoint.
*   [ ] Implement user login endpoint to generate JWT access and refresh tokens.
*   [ ] Configure permissions for API endpoints (e.g., `IsAuthenticated`, `IsAdminUser`).

## Milestone 3: Member Functionality

*   [ ] Implement an API endpoint for members to search for books (e.g., by title, author, genre).
*   [ ] Implement an API endpoint for members to **request to borrow** a book.
*   [ ] Implement an API endpoint for members to return a book.
*   [ ] Implement an API endpoint for members to view their borrowing history (including the status of their requests).

## Milestone 4: Admin Functionality

*   [ ] Implement API endpoints for admins to perform CRUD operations on books (Create, Read, Update, Delete).
*   [ ] Implement an API endpoint for admins to view all users.
*   [ ] Implement an API endpoint for admins to approve member registrations.
*   [ ] Implement an API endpoint for admins to view all borrow records and filter by status (e.g., PENDING, APPROVED).
*   [ ] Implement an API endpoint for admins to **approve a borrow request**.
*   [ ] Implement an API endpoint for admins to **reject a borrow request**.

## Milestone 5: Finalization

*   [ ] Add API documentation using a tool like `drf-yasg` or `drf-spectacular`.
*   [ ] Write unit and integration tests for the API endpoints and business logic.
*   [ ] Refine error handling and response messages.
*   [ ] Set up Django Admin for easy data management.

## Milestone 6: Book Model Enhancement (v2)

*   [ ] Update the book model to include `ISBN`, `publication_date`, and `cover_image_url`.
*   [ ] Update the book CRUD APIs to reflect the model changes.
*   [ ] Update the data import script to handle the new fields.

## Milestone 7: Fine Management (v2)

*   [ ] Implement a system to track overdue books.
*   [ ] Create a model to store fine information (e.g., amount, reason, status).
*   [ ] Implement an API endpoint for admins to view and manage fines.
*   [ ] Implement a mechanism to automatically calculate fines for overdue books upon return.

## Milestone 8: Weekly Library Activity Report (v2)

*   [ ] Create a new model, `Report`, to track the status of generated reports. The model's primary identifier (`id`) will be a timestamp of when the report generation was requested. It should also include fields for `status` (`pending`, `in_progress`, `completed`, `failed`) and `file_path` (to store the location of the generated report file).
*   [ ] Implement a Celery task to generate a weekly library activity report in Markdown format.Use langchain and llm to query database directly. The report should include statistics like:
    *   Number of new members this week.
    *   Number of books borrowed this week.
    *   Most borrowed books of the week.
*   [ ] The Celery task should save the report to a pre-defined path on the server (e.g., `/var/reports/weekly_activity_<timestamp>.md` (it can be any path)). It should update the `Report` model's status to `in_progress` when it starts, and to `completed` or `failed` when it finishes. Upon completion, it should also save the report's location in the `file_path` field.
*   [ ] Create an API endpoint for admins to trigger the weekly report generation. This endpoint will create a new `Report` record with a `pending` status and dispatch the Celery task.
*   [ ] Create an API endpoint for admins to list generated reports and check their status.
