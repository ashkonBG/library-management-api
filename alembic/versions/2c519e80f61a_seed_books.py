"""seed books

Revision ID: 2c519e80f61a
Revises: 26adb41a2178
Create Date: 2026-04-25 16:27:40.924881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c519e80f61a'
down_revision: Union[str, Sequence[str], None] = '26adb41a2178'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEED_DATA = [
    {
        "id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott",
        "publication_year": 1925,
        "genre": "Fiction",
    },
    {
        "id": 2,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "publication_year": 1960,
        "genre": "Fiction",
    },
    {
        "id": 3,
        "title": "1984",
        "author": "George Orwell",
        "publication_year": 1949,
        "genre": "Fiction",
    },
    {
        "id": 4,
        "title": "Moby Dick",
        "author": "Herman Melville",
        "publication_year": 1851,
        "genre": "Fiction",
    },
    {
        "id": 5,
        "title": "Fifty Shades of Grey",
        "author": "E.L. James",
        "publication_year": 2011,
        "genre": "18+",
    },
    {
        "id": 6,
        "title": "The Da Vinci Code",
        "author": "Dan Brown",
        "publication_year": 2003,
        "genre": "Mystery",
    },
    {
        "id": 7,
        "title": "The Shining",
        "author": "Stephen King",
        "publication_year": 1977,
        "genre": "Horror",
    },
    {
        "id": 8,
        "title": "A Brief History of Time",
        "author": "Stephen Hawking",
        "publication_year": 1988,
        "genre": "Nonfiction",
    },
    {
        "id": 9,
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "publication_year": 1951,
        "genre": "Fiction",
    },
    {
        "id": 10,
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "publication_year": 1937,
        "genre": "Fantasy",
    },
]


def upgrade() -> None:
    books_table = sa.table(
        "books",
        sa.column("id", sa.Integer),
        sa.column("title", sa.String),
        sa.column("author", sa.String),
        sa.column("publication_year", sa.Integer),
        sa.column("genre", sa.String),
    )
    op.bulk_insert(books_table, SEED_DATA)


def downgrade() -> None:
    op.execute("DELETE FROM books")
