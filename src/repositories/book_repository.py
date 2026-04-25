from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.book import Book, BookGenre

ADULT_GENRE = BookGenre.ADULT


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


def count_books_in_genre(session: Session, genre: str) -> int:
    return session.query(func.count(Book.id)).filter(Book.genre == genre).scalar() or 0


def delete_book(session: Session, book: Book) -> None:
    session.delete(book)


def search_books(
    session: Session,
    q: str | None = None,
    title: str | None = None,
    author: str | None = None,
    publication_year: int | None = None,
) -> list[Book]:
    query = session.query(Book).filter(Book.genre != ADULT_GENRE)

    if q:
        query = query.filter(Book.title.ilike(f"%{q}%") | Book.author.ilike(f"%{q}%"))
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if publication_year is not None:
        query = query.filter(Book.publication_year == publication_year)

    return query.order_by(Book.id).all()
