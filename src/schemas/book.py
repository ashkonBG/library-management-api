from src.models.book import BookGenre
from src.schemas.base import BaseModel


class BookBase(BaseModel):
    title: str
    author: str
    publication_year: int
    genre: BookGenre


class BookCreate(BookBase):
    pass


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
