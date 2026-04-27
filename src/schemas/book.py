from pydantic import field_validator

from src.models.book import BookGenre
from src.schemas.base import BaseModel


class BookBase(BaseModel):
    title: str
    author: str
    publication_year: int
    genre: BookGenre


class BookCreate(BookBase):
    @field_validator("genre")
    @classmethod
    def genre_must_not_be_horror(cls, value: BookGenre) -> BookGenre:
        if value == BookGenre.HORROR:
            raise ValueError("Books with the genre 'Horror' cannot be added.")

        return value


class BookResponse(BookBase):
    id: int


class BookInGenre(BaseModel):
    id: int
    title: str
    author: str
    publication_year: int
    genre: BookGenre


class GenreGroup(BaseModel):
    genre: str
    count: int
    books: list[BookInGenre]


class BooksGroupedResponse(BaseModel):
    genres: list[GenreGroup]


class BulkUpdateItem(BaseModel):
    id: int
    title: str | None = None
    author: str | None = None
    publication_year: int | None = None
    genre: BookGenre | None = None

    @field_validator("genre")
    @classmethod
    def genre_must_not_be_horror(cls, value: BookGenre | None) -> BookGenre | None:
        if value == BookGenre.HORROR:
            raise ValueError("Books with the genre 'Horror' cannot be added.")

        return value
