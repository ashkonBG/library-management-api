from sqlalchemy.orm import Session

from src.models.book import Book


def create_book(session: Session, book: Book) -> Book:
    session.add(book)
    session.flush()
    session.refresh(book)

    return book
