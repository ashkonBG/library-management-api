from fastapi import APIRouter, HTTPException, status

from src.exceptions import HorrorGenreNotAllowedError
from src.models.book import BookGenre
from src.routes.dependencies import DatabaseDependency
from src.schemas.book import (
    BookCreate,
    BookInGenre,
    BookResponse,
    BooksGroupedResponse,
    GenreGroup,
)
from src.services import book_service

ADULT_GENRE = BookGenre.ADULT
books_router = APIRouter(prefix="/books", tags=["Books"])


@books_router.post(
    path="/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_book(session: DatabaseDependency, book: BookCreate) -> BookResponse:
    try:
        db_book = book_service.create_book(book, session)

        return BookResponse.model_validate(db_book)
    except HorrorGenreNotAllowedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@books_router.get(path="/", response_model=BooksGroupedResponse)
def list_books(session: DatabaseDependency) -> BooksGroupedResponse:
    genre_map = book_service.get_books_grouped(session)
    groups = [
        GenreGroup(
            genre=genre,
            count=len(books),
            books=[
                BookInGenre(
                    id=b.id,
                    title="***" if genre == ADULT_GENRE else b.title,
                    author=b.author,
                    publication_year=b.publication_year,
                    genre=b.genre,
                )
                for b in books
            ],
        )
        for genre, books in genre_map.items()
    ]

    return BooksGroupedResponse(genres=groups)
