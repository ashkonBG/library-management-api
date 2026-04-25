from fastapi import APIRouter, HTTPException, status

from src.exceptions import HorrorGenreNotAllowedError
from src.routes.dependencies import DatabaseDependency
from src.schemas.book import BookCreate, BookResponse
from src.services import book_service

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
