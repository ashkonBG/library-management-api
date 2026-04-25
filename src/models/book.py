import enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class BookGenre(str, enum.Enum):
    FICTION = "Fiction"
    NONFICTION = "Nonfiction"
    MYSTERY = "Mystery"
    HORROR = "Horror"
    FANTASY = "Fantasy"
    ADULT = "18+"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    author: Mapped[str] = mapped_column(sa.String, nullable=False)
    publication_year: Mapped[int] = mapped_column(nullable=False)
    genre: Mapped[BookGenre] = mapped_column(
        sa.Enum(BookGenre, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
