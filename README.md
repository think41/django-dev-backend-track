## How to Use This Project

1.  **Set Up Your Environment (`prerequisite.md`)**

    Before you begin, please follow the instructions in the [**`prerequisite.md`**](./prerequisite.md) file. This will guide you through installing the necessary software and setting up your local development environment.

2.  **Define Your Use Cases (`use_case.md`)**

    Your first and most important task is to open the [**`use_case.md`**](./use_case.md) file. This is where you will define the actors (users or systems) and the specific use cases (the goals they need to achieve).

    **Do not write any code until you have a clear and comprehensive `use_case.md` file.**

3.  **Specify Your Modules (`spec_template.md`)**

    Once your use cases are defined, you can begin to think about the high-level design of your system. For each major component or module you identify, copy the [**`spec_template.md`**](./spec_template.md) to create a detailed specification for that module.

4.  **Start Development**

    With your prerequisites installed, use cases defined, and module specifications outlined, you are now ready to begin development.

## Running with Docker

This project is configured to run with Docker Compose, which simplifies the setup of the web server, database, and Celery services.

To start the application, run:

```bash
docker-compose up --build
```

This will build the Docker images and start the following services:
- `web`: The Django application.
- `db`: The PostgreSQL database.
- `redis`: The Redis server for Celery.
- `celery`: The Celery worker for background tasks.

## Celery and Redis

This project uses Celery with Redis as a message broker to handle asynchronous tasks. This is particularly useful for long-running processes, such as generating reports, that should not block the main application thread.

- **Celery:** A distributed task queue that allows you to run tasks in the background.
- **Redis:** An in-memory data store that Celery uses as a broker to pass messages between the Django application and the Celery workers.