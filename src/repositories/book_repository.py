from sqlalchemy.orm import Session

from src.models.book import Book


def create_book(session: Session, book: Book) -> Book:
    session.add(book)
    session.flush()
    session.refresh(book)

    return book


def get_all_books(session: Session) -> list[Book]:
    return session.query(Book).order_by(Book.genre, Book.id).all()
