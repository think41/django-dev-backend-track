# Module Specification: `Reports`

**Version:** 1.0

**Author:** Karan Singh

**Date:** 2025-08-12

---

## 1. Purpose and Responsibility

**Description:** This module is responsible for generating, managing, and delivering periodic reports about library activities. It uses Celery for asynchronous report generation and provides APIs for admins to request and access reports.

**Scope:**
-   **IN SCOPE:**
    -   Tracking report generation requests and their status.
    -   Generating weekly library activity reports.
    -   Providing APIs for admins to request reports and check their status.
    -   Storing generated reports and making them accessible to admins.
-   **OUT OF SCOPE:**
    -   Real-time analytics dashboard.
    -   User-customizable reports.
    -   Email delivery of reports (though this could be added in a future version).

---

## 2. Dependencies

-   **`users` module**: To access user data for report generation.
-   **`books` module**: To access book and borrowing data for report generation.
-   **`celery`**: For asynchronous report generation tasks.
-   **`langchain`**: For database querying and report generation.
-   **`llm`**: For natural language processing in report generation.

---

## 3. Data Models / Schema

### 3.1. `Report`

**Description:** Tracks the status and metadata of generated reports.

| Field Name      | Data Type                               | Description                                                  |
| --------------- | --------------------------------------- | ------------------------------------------------------------ |
| `id`            | `CharField(50)`                         | Primary key, timestamp of when the report generation was requested (e.g., "20250812131045"). |
| `report_type`   | `CharField(50)`                         | Type of report. Currently only "weekly_activity" is supported. |
| `status`        | `CharField(20)`                         | Current status of the report. Choices: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `FAILED`. Default: `PENDING`. |
| `file_path`     | `CharField(255)`                        | Path to the generated report file. Null until report is completed. |
| `requested_by`  | `ForeignKey` to `User`                  | The admin who requested the report.                          |
| `error_message` | `TextField`                             | Error message if report generation failed. Null if successful. |
| `created_at`    | `DateTimeField`                         | Timestamp of when the report was requested.                  |
| `updated_at`    | `DateTimeField`                         | Timestamp of the last status update.                         |

---

## 4. API Endpoints

**Base URL:** `/api/reports/`

### 4.1. `Report` Endpoints

-   **`POST /api/reports/generate/`**
    -   **Description:** Triggers the generation of a new report.
    -   **Permissions:** Admin only
    -   **Request Body:** `{ "report_type": "weekly_activity" }`
    -   **Success Response (202 Accepted):** `{ "id": "string", "status": "PENDING", "message": "Report generation has been queued." }`

-   **`GET /api/reports/`**
    -   **Description:** Retrieves a list of all reports, with optional filtering by status.
    -   **Permissions:** Admin only
    -   **Query Params:** `?status=[PENDING/IN_PROGRESS/COMPLETED/FAILED]`
    -   **Success Response (200 OK):** `[ { "id": "string", "report_type": "string", "status": "string", "created_at": "datetime", "file_path": "string" }, ... ]`

-   **`GET /api/reports/{id}/`**
    -   **Description:** Retrieves details of a specific report.
    -   **Permissions:** Admin only
    -   **Success Response (200 OK):** `{ "id": "string", "report_type": "string", "status": "string", "created_at": "datetime", "file_path": "string", "error_message": "string" }`
    -   **Failure Response (404 Not Found):** If the report ID does not exist.

-   **`GET /api/reports/{id}/download/`**
    -   **Description:** Downloads the generated report file.
    -   **Permissions:** Admin only
    -   **Success Response (200 OK):** The report file content with appropriate Content-Type header.
    -   **Failure Response (404 Not Found):** If the report ID does not exist or the report has not been generated yet.
    -   **Failure Response (400 Bad Request):** If the report generation failed.

---

## 5. Services and Business Logic

### 5.1. `ReportService`

-   **Purpose:** To manage the report generation process.
-   **Methods:**
    -   `request_report(report_type, user)`: Creates a new `Report` record with `PENDING` status and dispatches the appropriate Celery task.
    -   `update_report_status(report_id, status, file_path=None, error_message=None)`: Updates the status of a report and, if completed, sets the file path.
    -   `get_report_content(report_id)`: Retrieves the content of a generated report file.

### 5.2. `WeeklyActivityReportGenerator`

-   **Purpose:** To generate the weekly library activity report.
-   **Methods:**
    -   `generate(report_id)`: Generates the weekly activity report, including statistics on new members, borrowed books, and most popular books.
    -   `query_database()`: Uses langchain and LLM to query the database for the required statistics.
    -   `format_report(data)`: Formats the report data into a Markdown document.
    -   `save_report(content, report_id)`: Saves the generated report to the file system and updates the report record.

---

## 6. Celery Tasks

### 6.1. `generate_weekly_activity_report`

-   **Purpose:** Asynchronous task to generate the weekly activity report.
-   **Parameters:**
    -   `report_id`: The ID of the report record to update.
-   **Actions:**
    1. Updates the report status to `IN_PROGRESS`.
    2. Uses `WeeklyActivityReportGenerator` to generate the report.
    3. Updates the report status to `COMPLETED` or `FAILED` based on the outcome.
    4. If successful, saves the file path to the report record.

---

## 7. Events (Optional)

-   **Publishes:**
    -   `report.requested`: When an admin requests a report. Carries `report_id`, `report_type`.
    -   `report.completed`: When a report is successfully generated. Carries `report_id`.
    -   `report.failed`: When report generation fails. Carries `report_id`, `error_message`.
