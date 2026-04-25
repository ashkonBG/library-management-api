from typing import Callable

from sqlalchemy.orm import Session

from src.models.book import Book
from src.repositories import book_repository


def test_create_book_returns_book_with_id(
    db_session: Session, make_unsaved_book: Callable[..., Book]
) -> None:
    book = make_unsaved_book()

    result = book_repository.create_book(db_session, book)

    assert result.id is not None
    assert isinstance(result.id, int)


def test_create_book_persists_all_fields(
    db_session: Session, make_unsaved_book: Callable[..., Book]
) -> None:
    book = make_unsaved_book(
        title="Dune", author="Frank Herbert", publication_year=1965, genre="Fiction"
    )

    result = book_repository.create_book(db_session, book)

    assert result.title == "Dune"
    assert result.author == "Frank Herbert"
    assert result.publication_year == 1965
    assert result.genre == "Fiction"


def test_create_book_multiple_books_get_unique_ids(
    db_session: Session, make_unsaved_book: Callable[..., Book]
) -> None:
    b1 = book_repository.create_book(db_session, make_unsaved_book(title="Book One"))
    b2 = book_repository.create_book(db_session, make_unsaved_book(title="Book Two"))

    assert b1.id != b2.id


def test_get_all_books_empty_database(db_session: Session) -> None:
    assert book_repository.get_all_books(db_session) == []


def test_get_all_books_returns_every_book(
    db_session: Session, sample_books: list[Book]
) -> None:
    result = book_repository.get_all_books(db_session)

    assert len(result) == len(sample_books)


def test_get_all_books_ordered_by_genre_then_id(
    db_session: Session, sample_books: list[Book]
) -> None:
    result = book_repository.get_all_books(db_session)
    genres = [b.genre for b in result]

    assert genres == sorted(genres)


def test_get_all_books_includes_adult_genre(
    db_session: Session, sample_books: list[Book]
) -> None:
    result = book_repository.get_all_books(db_session)
    genres = {b.genre for b in result}

    assert "18+" in genres


def test_get_book_by_id_returns_correct_book(
    db_session: Session, sample_books: list[Book]
) -> None:
    target = sample_books[0]

    result = book_repository.get_book_by_id(db_session, target.id)

    assert result is not None
    assert result.id == target.id
    assert result.title == target.title


def test_get_book_by_id_returns_none_when_missing(db_session: Session) -> None:
    assert book_repository.get_book_by_id(db_session, 9999) is None


def test_get_book_by_id_returns_none_on_empty_db(db_session: Session) -> None:
    assert book_repository.get_book_by_id(db_session, 1) is None


def test_update_book_changes_single_field(
    db_session: Session, sample_books: list[Book]
) -> None:
    book = sample_books[0]

    book_repository.update_book(db_session, book, {"title": "Updated Title"})

    assert book.title == "Updated Title"


def test_update_book_changes_multiple_fields(
    db_session: Session, sample_books: list[Book]
) -> None:
    book = sample_books[0]

    book_repository.update_book(
        db_session, book, {"title": "New Title", "publication_year": 2000}
    )

    assert book.title == "New Title"
    assert book.publication_year == 2000


def test_update_book_does_not_affect_other_fields(
    db_session: Session, sample_books: list[Book]
) -> None:
    book = sample_books[0]
    original_author = book.author

    book_repository.update_book(db_session, book, {"title": "Changed"})

    assert book.author == original_author


def test_update_book_returns_modified_book(
    db_session: Session, sample_books: list[Book]
) -> None:
    book = sample_books[0]

    result = book_repository.update_book(db_session, book, {"title": "Returned"})

    assert result.title == "Returned"


def test_update_book_flushes_to_db(
    db_session: Session, sample_books: list[Book]
) -> None:
    book = sample_books[0]
    book_id = book.id
    book_repository.update_book(db_session, book, {"title": "Flushed Title"})

    # expire the cached instance so SQLAlchemy re-fetches from the DB
    db_session.expire(book)
    refreshed = book_repository.get_book_by_id(db_session, book_id)

    assert refreshed is not None
    assert refreshed.title == "Flushed Title"


def test_count_books_in_genre_correct_count(
    db_session: Session, sample_books: list[Book]
) -> None:
    expected = sum(1 for b in sample_books if b.genre == "Fiction")

    assert book_repository.count_books_in_genre(db_session, "Fiction") == expected


def test_count_books_in_genre_returns_zero_for_unknown_genre(
    db_session: Session,
) -> None:
    assert book_repository.count_books_in_genre(db_session, "Nonexistent") == 0


def test_count_books_in_genre_returns_zero_on_empty_db(db_session: Session) -> None:
    assert book_repository.count_books_in_genre(db_session, "Fiction") == 0


def test_count_books_in_genre_counts_adult_genre(
    db_session: Session, sample_books: list[Book]
) -> None:
    assert book_repository.count_books_in_genre(db_session, "18+") == 1


def test_delete_book_removes_it_from_db(
    db_session: Session, sample_books: list[Book]
) -> None:
    book = sample_books[0]
    book_id = book.id
    book_repository.delete_book(db_session, book)
    db_session.flush()
    assert book_repository.get_book_by_id(db_session, book_id) is None


def test_delete_book_does_not_affect_other_books(
    db_session: Session, sample_books: list[Book]
) -> None:
    book_to_delete = sample_books[0]
    remaining_ids = {b.id for b in sample_books[1:]}
    book_repository.delete_book(db_session, book_to_delete)
    db_session.flush()
    for bid in remaining_ids:
        assert book_repository.get_book_by_id(db_session, bid) is not None


def test_delete_book_reduces_total_count(
    db_session: Session, sample_books: list[Book]
) -> None:
    before = len(book_repository.get_all_books(db_session))
    book_repository.delete_book(db_session, sample_books[0])
    db_session.flush()
    after = len(book_repository.get_all_books(db_session))
    assert after == before - 1


def test_search_books_always_excludes_adult_genre(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session)
    assert all(b.genre != "18+" for b in results)


def test_search_books_adult_author_query_returns_empty(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session, author="E.L. James")
    assert results == []


def test_search_books_no_filters_returns_all_non_adult(
    db_session: Session, sample_books: list[Book]
) -> None:
    expected = sum(1 for b in sample_books if b.genre != "18+")
    assert len(book_repository.search_books(db_session)) == expected


def test_search_books_q_matches_title(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session, q="Gatsby")
    assert len(results) == 1
    assert results[0].title == "The Great Gatsby"


def test_search_books_q_matches_author(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session, q="Orwell")
    assert len(results) == 1
    assert results[0].author == "George Orwell"


def test_search_books_q_is_case_insensitive(
    db_session: Session, sample_books: list[Book]
) -> None:
    lower = book_repository.search_books(db_session, q="gatsby")
    upper = book_repository.search_books(db_session, q="GATSBY")
    assert len(lower) == len(upper) == 1


def test_search_books_q_partial_match(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session, q="Vinci")
    assert any("Da Vinci" in b.title for b in results)


def test_search_books_by_title_filter(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session, title="Da Vinci")
    assert len(results) == 1
    assert results[0].title == "The Da Vinci Code"


def test_search_books_by_author_filter(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session, author="Stephen")
    titles = {b.title for b in results}
    assert "The Shining" in titles
    assert "A Brief History of Time" in titles


def test_search_books_by_publication_year(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session, publication_year=1949)
    assert len(results) == 1
    assert results[0].title == "1984"


def test_search_books_combined_title_and_author(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session, title="1984", author="Orwell")
    assert len(results) == 1


def test_search_books_no_match_returns_empty(
    db_session: Session, sample_books: list[Book]
) -> None:
    assert book_repository.search_books(db_session, q="xyznonexistent") == []


def test_search_books_results_ordered_by_id(
    db_session: Session, sample_books: list[Book]
) -> None:
    results = book_repository.search_books(db_session)
    ids = [b.id for b in results]
    assert ids == sorted(ids)
