from typing import Callable
from unittest.mock import MagicMock, patch

import pytest

from src.exceptions import HorrorGenreNotAllowedError
from src.models.book import Book, BookGenre
from src.schemas.book import BookCreate
from src.services import book_service


@patch("src.services.book_service.book_repository")
def test_create_book_success_returns_db_book(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    expected = make_saved_book(id=10, title="New Book")
    mock_repo.create_book.return_value = expected

    result = book_service.create_book(
        BookCreate(
            title="New Book",
            author="Author",
            publication_year=2020,
            genre=BookGenre.FICTION,
        ),
        session,
    )

    assert result is expected
    mock_repo.create_book.assert_called_once()


def test_create_book_horror_raises_error() -> None:
    session = MagicMock()

    with pytest.raises(HorrorGenreNotAllowedError):
        book_service.create_book(
            BookCreate(
                title="It",
                author="S. King",
                publication_year=1986,
                genre=BookGenre.HORROR,
            ),
            session,
        )


@patch("src.services.book_service.book_repository")
def test_create_book_horror_never_reaches_repo(mock_repo: MagicMock) -> None:
    session = MagicMock()

    try:
        book_service.create_book(
            BookCreate(
                title="It",
                author="S. King",
                publication_year=1986,
                genre=BookGenre.HORROR,
            ),
            session,
        )
    except HorrorGenreNotAllowedError:
        pass

    mock_repo.create_book.assert_not_called()


@patch("src.services.book_service.book_repository")
def test_create_book_non_horror_genres_are_allowed(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    mock_repo.create_book.return_value = make_saved_book(genre="Mystery")

    for genre in [
        BookGenre.FICTION,
        BookGenre.NONFICTION,
        BookGenre.MYSTERY,
        BookGenre.FANTASY,
        BookGenre.ADULT,
    ]:
        book_service.create_book(
            BookCreate(title="T", author="A", publication_year=2000, genre=genre),
            session,
        )

    assert mock_repo.create_book.call_count == 5


@patch("src.services.book_service.book_repository")
def test_get_books_grouped_returns_dict_keyed_by_genre(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    mock_repo.get_all_books.return_value = [
        make_saved_book(id=1, genre="Fiction"),
        make_saved_book(id=2, genre="Fiction"),
        make_saved_book(id=3, genre="Mystery"),
    ]

    result = book_service.get_books_grouped(session)

    assert set(result.keys()) == {"Fiction", "Mystery"}
    assert len(result["Fiction"]) == 2
    assert len(result["Mystery"]) == 1


@patch("src.services.book_service.book_repository")
def test_get_books_grouped_empty_db_returns_empty_dict(mock_repo: MagicMock) -> None:
    session = MagicMock()
    mock_repo.get_all_books.return_value = []

    assert book_service.get_books_grouped(session) == {}


@patch("src.services.book_service.book_repository")
def test_get_books_grouped_includes_adult_genre_in_map(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    mock_repo.get_all_books.return_value = [
        make_saved_book(id=1, genre="Fiction"),
        make_saved_book(id=2, genre="18+"),
    ]

    result = book_service.get_books_grouped(session)

    assert "18+" in result
    assert "Fiction" in result


@patch("src.services.book_service.book_repository")
def test_get_books_grouped_books_belong_to_correct_genre(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    fiction_book = make_saved_book(id=1, genre="Fiction")
    mystery_book = make_saved_book(id=2, genre="Mystery")
    mock_repo.get_all_books.return_value = [fiction_book, mystery_book]

    result = book_service.get_books_grouped(session)

    assert fiction_book in result["Fiction"]
    assert mystery_book in result["Mystery"]


@patch("src.services.book_service.book_repository")
def test_get_books_grouped_calls_get_all_books(mock_repo: MagicMock) -> None:
    session = MagicMock()
    mock_repo.get_all_books.return_value = []

    book_service.get_books_grouped(session)

    mock_repo.get_all_books.assert_called_once_with(session)
