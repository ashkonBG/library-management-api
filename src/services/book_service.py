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
