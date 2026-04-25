from collections.abc import Generator
from typing import Any, Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.models.base import Base
from src.models.book import Book, BookGenre
from src.routes.dependencies import get_db_session


@pytest.fixture
def db_session() -> Generator[Session, Any, None]:
    """Create a new in-memory SQLite session for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_local = sessionmaker(autocommit=False, autoflush=True, bind=engine)
    session = session_local()

    yield session

    session.close()
    engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, Any, None]:

    def override_get_db() -> Generator[Session, Any, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def make_unsaved_book() -> Callable[..., Book]:
    def _factory(
        title: str = "Test Book",
        author: str = "Test Author",
        publication_year: int = 2020,
        genre: BookGenre = BookGenre.FICTION,
    ) -> Book:
        return Book(
            title=title,
            author=author,
            publication_year=publication_year,
            genre=genre,
        )

    return _factory


@pytest.fixture
def make_saved_book() -> Callable[..., Book]:
    def _factory(
        id: int = 1,
        title: str = "Test Book",
        author: str = "Test Author",
        publication_year: int = 2020,
        genre: BookGenre = BookGenre.FICTION,
    ) -> Book:
        return Book(
            id=id,
            title=title,
            author=author,
            publication_year=publication_year,
            genre=genre,
        )

    return _factory
