# Library Management API

![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)

A RESTful API for managing a library of books, built with **FastAPI**, **SQLAlchemy**, **SQLite**, and **Pydantic**.

---

## Table of Contents

- [Requirements Coverage](#requirements-coverage)
    - [Functional Requirements](#functional-requirements)
    - [Technical Requirements](#technical-requirements)
- [Extra Features](#extra-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)

---

## Requirements Coverage

### Functional Requirements

| Requirement                        | Status | Details                                                                       |
|------------------------------------|--------|-------------------------------------------------------------------------------|
| **Add a New Book**                 | ✅      | `POST /books/` - validates and persists a new book                            |
| Horror genre blocked on create     | ✅      | Rejected by Pydantic schema validation; returns `422 Unprocessable Entity`    |
| **Retrieve All Books**             | ✅      | `GET /books/` - returns all books grouped by genre                            |
| Grouped by genre with count        | ✅      | Response includes `genre`, `count`, and a `books` list per group              |
| Mask titles for `"18+"` genre      | ✅      | Titles of `18+` books are replaced with `"***"` in the list response          |
| **Update a Book by ID**            | ✅      | `PUT /books/` - supports bulk (multiple books) partial updates in one request |
| Horror genre blocked on update     | ✅      | Rejected by Pydantic schema validation; returns `422 Unprocessable Entity`    |
| **Delete a Book by ID**            | ✅      | `DELETE /books/{book_id}` - removes a book by its ID                          |
| Cannot delete last book in genre   | ✅      | Returns `400 Bad Request` if the book is the last remaining one in its genre  |
| **Search Books**                   | ✅      | `GET /books/search` - search by title and/or author                           |
| `"18+"` books excluded from search | ✅      | Search results never include books of the `18+` genre                         |

### Technical Requirements

| Requirement           | Status | Details                                                                                                         |
|-----------------------|--------|-----------------------------------------------------------------------------------------------------------------|
| **FastAPI**           | ✅      | All endpoints built with FastAPI; auto-generated OpenAPI docs at `/docs`                                        |
| **Pydantic**          | ✅      | All request/response models use Pydantic v2; business rules (e.g. Horror block) enforced via `@field_validator` |
| **pytest unit tests** | ✅      | 126 tests across repository, service, route, schema, and exception layers - **94% coverage**                    |
| **SQLite database**   | ✅      | SQLite via SQLAlchemy ORM; schema managed with Alembic migrations                                               |

---

## Extra Features

Beyond the stated requirements, the following extra features were implemented:

### Advanced Search Filters

`GET /books/search` supports four independent, combinable query parameters:

- `q` - searches across **both** title and author simultaneously (case-insensitive)
- `title` - partial, case-insensitive match on title only
- `author` - partial, case-insensitive match on author only
- `publication_year` - exact filter by year

### Bulk Book Updates

`PUT /books/` accepts a **list** of update objects in a single request, allowing multiple books to be partially updated
atomically. Each item only requires the `id` and the fields to change (all other fields are optional).

### Alembic Database Migrations

Database schema is version-controlled using **Alembic**, with:

- `create_books_table` - initial migration creating the `books` table
- `seed_books` - seeds the database with sample books on startup

### Pydantic-settings Configuration

Application and database settings are managed via `pydantic-settings`, supporting overrides through environment
variables or a `.env` file:

- `APP_NAME`, `APP_VERSION`, `APP_DEBUG`
- `DATABASE_URL`

### Health Check Endpoint

`GET /` returns the application status, name, and version - useful for liveness probes in containerized environments.

### Pre-commit Hooks

Code quality is enforced automatically on every commit via **pre-commit**. The following hooks run before each commit is
accepted:

| Hook                  | Purpose                                       |
|-----------------------|-----------------------------------------------|
| `sort-pyproject`      | Keeps `pyproject.toml` sections sorted        |
| `end-of-file-fixer`   | Ensures files end with a newline              |
| `trailing-whitespace` | Removes trailing whitespace                   |
| `black`               | Opinionated Python code formatter             |
| `isort`               | Sorts and organises import statements         |
| `ruff`                | Fast Python linter (with auto-fix)            |
| `mypy`                | Static type checking                          |
| `uv-lock`             | Keeps `uv.lock` in sync with `pyproject.toml` |

### Docker Support

A `Dockerfile` and `docker-compose.yml` are included for containerized deployment.

### Layered Architecture

The codebase follows a clean separation of concerns:

```
routes → services → repositories → models
```

- **Routes** - HTTP handling, request/response serialisation
- **Services** - business logic and rule enforcement
- **Repositories** - data access and query logic
- **Models** - SQLAlchemy ORM definitions
- **Schemas** - Pydantic models for validation

---

## Project Structure

```
library-management-api/
├── alembic/                  # Database migrations
│   └── versions/
├── src/
│   ├── config/               # App & DB settings (pydantic-settings)
│   ├── database/             # SQLAlchemy session factory
│   ├── models/               # ORM models (Book, BookGenre)
│   ├── repositories/         # Data access layer
│   ├── routes/               # FastAPI routers & DI dependencies
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # Business logic layer
│   ├── exceptions.py         # Custom domain exceptions
│   └── main.py               # FastAPI app entry point
├── tests/                    # pytest test suite (126 tests, 94% coverage)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── alembic.ini
```

---

## Getting Started

### Prerequisites

- Python ≥ 3.12
- [uv](https://docs.astral.sh/uv/) package manager

### Install dependencies

```bash
uv sync
```

### Install pre-commit hooks

```bash
uv run pre-commit install
```

> After this, code quality checks (formatting, linting, type checking) run automatically on every `git commit`.

### Run database migrations

```bash
uv run alembic upgrade head
```

### Start the development server

```bash
uv run uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive docs: `http://127.0.0.1:8000/docs`

### Using Docker

```bash
docker-compose up --build
```

---

## API Endpoints

| Method   | Path               | Description                            |
|----------|--------------------|----------------------------------------|
| `GET`    | `/`                | Health check                           |
| `POST`   | `/books/`          | Add a new book                         |
| `GET`    | `/books/`          | List all books grouped by genre        |
| `PUT`    | `/books/`          | Bulk update one or more books          |
| `DELETE` | `/books/{book_id}` | Delete a book by ID                    |
| `GET`    | `/books/search`    | Search books by title, author, or year |

### Supported Genres

`Fiction`, `Nonfiction`, `Mystery`, `Fantasy`, `18+`

> **Note:** `Horror` is a valid enum value but is rejected by Pydantic schema validation on both create and update,
> returning `422 Unprocessable Entity`.

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing
```

**Current test results:** 126 passed · 94% coverage
