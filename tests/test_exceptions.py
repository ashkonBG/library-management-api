import pytest

from src.exceptions import BookNotFoundError, LastBookInGenreError


def test_book_not_found_error_is_exception() -> None:
    assert isinstance(BookNotFoundError(1), Exception)


def test_book_not_found_error_message() -> None:
    exc = BookNotFoundError(42)
    assert str(exc) == "Book with id 42 not found."


def test_book_not_found_error_stores_book_id() -> None:
    exc = BookNotFoundError(99)
    assert exc.book_id == 99


def test_book_not_found_error_different_ids() -> None:
    for book_id in (0, 1, 100, 999):
        exc = BookNotFoundError(book_id)
        assert exc.book_id == book_id
        assert str(book_id) in str(exc)


def test_book_not_found_error_can_be_raised_and_caught() -> None:
    with pytest.raises(BookNotFoundError) as exc_info:
        raise BookNotFoundError(7)
    assert exc_info.value.book_id == 7


def test_last_book_in_genre_error_is_exception() -> None:
    assert isinstance(LastBookInGenreError("Mystery"), Exception)


def test_last_book_in_genre_error_message() -> None:
    exc = LastBookInGenreError("Mystery")
    assert str(exc) == "Cannot delete the last book in genre 'Mystery'."


def test_last_book_in_genre_error_stores_genre() -> None:
    exc = LastBookInGenreError("Horror")
    assert exc.genre == "Horror"


def test_last_book_in_genre_error_different_genres() -> None:
    for genre in ("Fiction", "Horror", "18+", "Nonfiction"):
        exc = LastBookInGenreError(genre)
        assert exc.genre == genre
        assert genre in str(exc)


def test_last_book_in_genre_error_can_be_raised_and_caught() -> None:
    with pytest.raises(LastBookInGenreError) as exc_info:
        raise LastBookInGenreError("SciFi")
    assert exc_info.value.genre == "SciFi"
