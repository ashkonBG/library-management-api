import pytest
from pydantic import ValidationError

from src.models.book import BookGenre
from src.schemas.book import BookCreate, BulkUpdateItem


def test_book_create_non_horror_genres_are_valid() -> None:
    for genre in [
        BookGenre.FICTION,
        BookGenre.NONFICTION,
        BookGenre.MYSTERY,
        BookGenre.FANTASY,
        BookGenre.ADULT,
    ]:
        book = BookCreate(title="T", author="A", publication_year=2000, genre=genre)
        assert book.genre == genre


def test_book_create_horror_genre_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        BookCreate(
            title="It",
            author="S. King",
            publication_year=1986,
            genre=BookGenre.HORROR,
        )


def test_book_create_horror_error_message_mentions_horror() -> None:
    with pytest.raises(ValidationError) as exc_info:
        BookCreate(
            title="It",
            author="S. King",
            publication_year=1986,
            genre=BookGenre.HORROR,
        )
    assert "Horror" in str(exc_info.value)


def test_bulk_update_item_horror_genre_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        BulkUpdateItem(id=1, genre=BookGenre.HORROR)


def test_bulk_update_item_horror_error_message_mentions_horror() -> None:
    with pytest.raises(ValidationError) as exc_info:
        BulkUpdateItem(id=1, genre=BookGenre.HORROR)
    assert "Horror" in str(exc_info.value)


def test_bulk_update_item_non_horror_genres_are_valid() -> None:
    for genre in [
        BookGenre.FICTION,
        BookGenre.NONFICTION,
        BookGenre.MYSTERY,
        BookGenre.FANTASY,
        BookGenre.ADULT,
    ]:
        item = BulkUpdateItem(id=1, genre=genre)
        assert item.genre == genre


def test_bulk_update_item_none_genre_is_valid() -> None:
    item = BulkUpdateItem(id=1)
    assert item.genre is None
