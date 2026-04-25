from typing import Callable

from sqlalchemy.orm import Session

from src.models.book import Book
from src.repositories import book_repository


def test_create_book_returns_book_with_id(
    db_session: Session, make_unsaved_book: Callable[..., Book]
) -> None:
    book = make_unsaved_book()

    result = book_repository.create_book(db_session, book)

    assert result.id is not None
    assert isinstance(result.id, int)


def test_create_book_persists_all_fields(
    db_session: Session, make_unsaved_book: Callable[..., Book]
) -> None:
    book = make_unsaved_book(
        title="Dune", author="Frank Herbert", publication_year=1965, genre="Fiction"
    )

    result = book_repository.create_book(db_session, book)

    assert result.title == "Dune"
    assert result.author == "Frank Herbert"
    assert result.publication_year == 1965
    assert result.genre == "Fiction"


def test_create_book_multiple_books_get_unique_ids(
    db_session: Session, make_unsaved_book: Callable[..., Book]
) -> None:
    b1 = book_repository.create_book(db_session, make_unsaved_book(title="Book One"))
    b2 = book_repository.create_book(db_session, make_unsaved_book(title="Book Two"))

    assert b1.id != b2.id


def test_get_all_books_empty_database(db_session: Session) -> None:
    assert book_repository.get_all_books(db_session) == []


def test_get_all_books_returns_every_book(
    db_session: Session, sample_books: list[Book]
) -> None:
    result = book_repository.get_all_books(db_session)

    assert len(result) == len(sample_books)


def test_get_all_books_ordered_by_genre_then_id(
    db_session: Session, sample_books: list[Book]
) -> None:
    result = book_repository.get_all_books(db_session)
    genres = [b.genre for b in result]

    assert genres == sorted(genres)


def test_get_all_books_includes_adult_genre(
    db_session: Session, sample_books: list[Book]
) -> None:
    result = book_repository.get_all_books(db_session)
    genres = {b.genre for b in result}

    assert "18+" in genres
