# Project Prerequisites & Setup

This document outlines the necessary software and steps required to set up and run the Library Management System project on your local machine for development.

---

## 1. Core Software Requirements

Make sure you have the following software installed on your system.

-   **Python:** This project requires Python `3.10` or newer.
    -   To check your version, run: `python --version`
    -   If you don't have it, download it from [python.org](https://www.python.org/downloads/).

-   **Pip:** Python's package installer. It typically comes with modern Python installations.
    -   To check your version, run: `pip --version`

-   **Git:** For version control and cloning the repository.
    -   To check if it's installed, run: `git --version`

-   **Docker:** For running the PostgreSQL database in a container.
    -   To check if it's installed, run: `docker --version`
    -   If you don't have it, follow the installation instructions at [docker.com](https://www.docker.com/get-started).

-   **Docker Compose:** For defining and running multi-container Docker applications.
    -   To check if it's installed, run: `docker-compose --version`

## 2. Step-by-Step Setup Instructions

Follow these steps in order to get your development environment ready.

### Step 1: Clone the Repository

First, clone the project repository from its source to your local machine.

```bash
# Replace the URL with the actual repository URL
git clone https://github.com/your-username/lms-project.git
cd lms-project
```

### Step 2: Create and Activate a Virtual Environment

It is a strong best practice to use a virtual environment for each Python project to manage dependencies and avoid conflicts. We will use the built-in `venv` module.

```bash
# Activate the virtual environment
# On macOS and Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

Once activated, you will see `(venv)` at the beginning of your command prompt.

### Step 3: Install Project Dependencies

All required Python packages are listed in the `requirements.txt` file. Install them using pip.

```bash
# Ensure your virtual environment is active
pip install -r requirements.txt
```

### Step 4: Set Up the PostgreSQL Database

The project uses a PostgreSQL database running in a Docker container.

```bash
# Start the database container in the background
sudo docker compose up -d
```

### Step 5: Apply Database Migrations

Apply the initial database schema (migrations).

```bash
# Apply database migrations
python manage.py migrate
```

### Step 6: Load Initial Data (Should be only done once models are migrated. This data may differ based on your schema design)

To start with some sample data (users, books, and borrow records), you can run the custom management commands. The data is located in the `data` directory.

```bash
# Load the sample data from the CSV files
python manage.py load_users_data --path data/users.csv
python manage.py load_books_data --path data/books.csv
python manage.py load_borrow_records_data --path data/borrow_records.csv
```

*(Note: This command will be created during the project's development.)*

### Step 7: Run the Development Server

Finally, run the local development server to ensure everything is working correctly.

```bash
python manage.py runserver
```

By default, the server will be accessible at `http://127.0.0.1:8000/`.

---

Your development environment is now set up! You can begin working on the code.
