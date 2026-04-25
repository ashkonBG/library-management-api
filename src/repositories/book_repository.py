from sqlalchemy.orm import Session

from src.models.book import Book


def create_book(session: Session, book: Book) -> Book:
    session.add(book)
    session.flush()
    session.refresh(book)

    return book


def get_all_books(session: Session) -> list[Book]:
    return session.query(Book).order_by(Book.genre, Book.id).all()


def get_book_by_id(session: Session, book_id: int) -> Book | None:
    return session.query(Book).filter(Book.id == book_id).first()


def update_book(session: Session, book: Book, patch: dict) -> Book:
    for field, value in patch.items():
        setattr(book, field, value)

    session.flush()

    return book
