from sqlalchemy.orm import Session

from src.exceptions import HorrorGenreNotAllowedError
from src.models.book import Book, BookGenre
from src.repositories import book_repository
from src.schemas.book import BookCreate

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
