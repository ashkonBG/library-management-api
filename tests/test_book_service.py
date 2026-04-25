from typing import Callable
from unittest.mock import MagicMock, patch

import pytest

from src.exceptions import (
    BookNotFoundError,
    HorrorGenreNotAllowedError,
    LastBookInGenreError,
)
from src.models.book import Book, BookGenre
from src.schemas.book import BookCreate, BulkUpdateItem
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


@patch("src.services.book_service.book_repository")
def test_bulk_update_books_success_returns_updated_books(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    existing = make_saved_book(id=1, title="Old Title")
    mock_repo.get_book_by_id.return_value = existing

    result = book_service.bulk_update_books(
        [BulkUpdateItem(id=1, title="New Title")], session
    )

    assert result == [existing]


@patch("src.services.book_service.book_repository")
def test_bulk_update_books_calls_update_with_correct_patch(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    existing = make_saved_book(id=1)
    mock_repo.get_book_by_id.return_value = existing

    book_service.bulk_update_books([BulkUpdateItem(id=1, title="Changed")], session)

    mock_repo.update_book.assert_called_once_with(
        session, existing, {"title": "Changed"}
    )


@patch("src.services.book_service.book_repository")
def test_bulk_update_books_excludes_id_from_patch(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    mock_repo.get_book_by_id.return_value = make_saved_book(id=1)

    book_service.bulk_update_books([BulkUpdateItem(id=1, title="T")], session)

    _, _, patch_dict = mock_repo.update_book.call_args[0]
    assert "id" not in patch_dict
    assert "title" in patch_dict


@patch("src.services.book_service.book_repository")
def test_bulk_update_books_not_found_raises_error(mock_repo: MagicMock) -> None:
    session = MagicMock()
    mock_repo.get_book_by_id.return_value = None

    with pytest.raises(BookNotFoundError) as exc_info:
        book_service.bulk_update_books([BulkUpdateItem(id=999, title="X")], session)

    assert exc_info.value.book_id == 999


@patch("src.services.book_service.book_repository")
def test_bulk_update_books_not_found_does_not_call_update(mock_repo: MagicMock) -> None:
    session = MagicMock()
    mock_repo.get_book_by_id.return_value = None

    try:
        book_service.bulk_update_books([BulkUpdateItem(id=999)], session)
    except BookNotFoundError:
        pass

    mock_repo.update_book.assert_not_called()


@patch("src.services.book_service.book_repository")
def test_bulk_update_books_multiple_items(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    b1, b2 = make_saved_book(id=1), make_saved_book(id=2)
    mock_repo.get_book_by_id.side_effect = [b1, b2]

    result = book_service.bulk_update_books(
        [BulkUpdateItem(id=1, title="T1"), BulkUpdateItem(id=2, title="T2")],
        session,
    )

    assert result == [b1, b2]
    assert mock_repo.update_book.call_count == 2


@patch("src.services.book_service.book_repository")
def test_bulk_update_books_only_set_fields_are_patched(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    mock_repo.get_book_by_id.return_value = make_saved_book(id=1)

    book_service.bulk_update_books([BulkUpdateItem(id=1, title="Only Title")], session)

    _, _, patch_dict = mock_repo.update_book.call_args[0]
    assert list(patch_dict.keys()) == ["title"]


@patch("src.services.book_service.book_repository")
def test_delete_book_success_calls_repo_delete(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    book = make_saved_book(id=1, genre="Fiction")
    mock_repo.get_book_by_id.return_value = book
    mock_repo.count_books_in_genre.return_value = 3

    book_service.delete_book(1, session)

    mock_repo.delete_book.assert_called_once_with(session, book)


@patch("src.services.book_service.book_repository")
def test_delete_book_not_found_raises_error(mock_repo: MagicMock) -> None:
    session = MagicMock()
    mock_repo.get_book_by_id.return_value = None

    with pytest.raises(BookNotFoundError) as exc_info:
        book_service.delete_book(404, session)

    assert exc_info.value.book_id == 404


@patch("src.services.book_service.book_repository")
def test_delete_book_not_found_skips_count_and_delete(mock_repo: MagicMock) -> None:
    session = MagicMock()
    mock_repo.get_book_by_id.return_value = None

    try:
        book_service.delete_book(1, session)
    except BookNotFoundError:
        pass

    mock_repo.count_books_in_genre.assert_not_called()
    mock_repo.delete_book.assert_not_called()


@patch("src.services.book_service.book_repository")
def test_delete_book_last_in_genre_raises_error(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    book = make_saved_book(id=1, genre="Mystery")
    mock_repo.get_book_by_id.return_value = book
    mock_repo.count_books_in_genre.return_value = 1

    with pytest.raises(LastBookInGenreError) as exc_info:
        book_service.delete_book(1, session)

    assert exc_info.value.genre == "Mystery"


@patch("src.services.book_service.book_repository")
def test_delete_book_last_in_genre_does_not_call_delete(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    mock_repo.get_book_by_id.return_value = make_saved_book(id=1, genre="Mystery")
    mock_repo.count_books_in_genre.return_value = 1

    try:
        book_service.delete_book(1, session)
    except LastBookInGenreError:
        pass

    mock_repo.delete_book.assert_not_called()


@patch("src.services.book_service.book_repository")
def test_delete_book_with_two_books_in_genre_succeeds(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    mock_repo.get_book_by_id.return_value = make_saved_book(id=1, genre="Fiction")
    mock_repo.count_books_in_genre.return_value = 2

    book_service.delete_book(1, session)

    mock_repo.delete_book.assert_called_once()


@patch("src.services.book_service.book_repository")
def test_search_books_delegates_entirely_to_repo(
    mock_repo: MagicMock, make_saved_book: Callable[..., Book]
) -> None:
    session = MagicMock()
    expected = [make_saved_book(id=1)]
    mock_repo.search_books.return_value = expected

    result = book_service.search_books(session, q="test")

    assert result is expected


@patch("src.services.book_service.book_repository")
def test_search_books_passes_all_keyword_args(mock_repo: MagicMock) -> None:
    session = MagicMock()
    mock_repo.search_books.return_value = []

    book_service.search_books(
        session, q="x", title="y", author="z", publication_year=2000
    )

    mock_repo.search_books.assert_called_once_with(
        session, q="x", title="y", author="z", publication_year=2000
    )


@patch("src.services.book_service.book_repository")
def test_search_books_none_defaults_passed_to_repo(mock_repo: MagicMock) -> None:
    session = MagicMock()
    mock_repo.search_books.return_value = []

    book_service.search_books(session)

    mock_repo.search_books.assert_called_once_with(
        session, q=None, title=None, author=None, publication_year=None
    )


@patch("src.services.book_service.book_repository")
def test_search_books_returns_empty_list_when_repo_returns_empty(
    mock_repo: MagicMock,
) -> None:
    session = MagicMock()
    mock_repo.search_books.return_value = []

    assert book_service.search_books(session) == []
