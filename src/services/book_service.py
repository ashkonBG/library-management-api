from sqlalchemy.orm import Session

from src.exceptions import (
    BookNotFoundError,
    HorrorGenreNotAllowedError,
    LastBookInGenreError,
)
from src.models.book import Book, BookGenre
from src.repositories import book_repository
from src.schemas.book import BookCreate, BulkUpdateItem

HORROR_GENRE = BookGenre.HORROR


def create_book(book: BookCreate, session: Session) -> Book:
    if book.genre == HORROR_GENRE:
        raise HorrorGenreNotAllowedError()

    return book_repository.create_book(session, Book(**book.model_dump()))


def get_books_grouped(session: Session) -> dict[str, list[Book]]:
    books = book_repository.get_all_books(session)
    genre_map: dict[str, list[Book]] = {}

    for book in books:
        genre_map.setdefault(book.genre, []).append(book)

    return genre_map


def bulk_update_books(updates: list[BulkUpdateItem], session: Session) -> list[Book]:
    to_update: list[Book] = []

    for item in updates:
        if item.genre == HORROR_GENRE:
            raise HorrorGenreNotAllowedError()

        book = book_repository.get_book_by_id(session, item.id)

        if not book:
            raise BookNotFoundError(item.id)

        patch = item.model_dump(exclude_unset=True, exclude={"id"})
        book_repository.update_book(session, book, patch)
        to_update.append(book)

    return to_update


def delete_book(book_id: int, session: Session) -> None:
    book = book_repository.get_book_by_id(session, book_id)

    if not book:
        raise BookNotFoundError(book_id)

    genre_count = book_repository.count_books_in_genre(session, book.genre)

    if genre_count <= 1:
        raise LastBookInGenreError(book.genre)

    book_repository.delete_book(session, book)


def search_books(
    session: Session,
    q: str | None = None,
    title: str | None = None,
    author: str | None = None,
    publication_year: int | None = None,
) -> list[Book]:
    return book_repository.search_books(
        session, q=q, title=title, author=author, publication_year=publication_year
    )
