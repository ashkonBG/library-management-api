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
