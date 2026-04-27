from fastapi.testclient import TestClient

from src.models.book import Book

# ---------------------------------------------------------------------------
# POST /books
# ---------------------------------------------------------------------------


def test_add_book_returns_201(client: TestClient) -> None:
    payload = {
        "title": "Dune",
        "author": "Frank Herbert",
        "publicationYear": 1965,
        "genre": "Fiction",
    }

    assert client.post("/books/", json=payload).status_code == 201


def test_add_book_response_contains_id(client: TestClient) -> None:
    payload = {
        "title": "Dune",
        "author": "Frank Herbert",
        "publicationYear": 1965,
        "genre": "Fiction",
    }

    data = client.post("/books/", json=payload).json()

    assert "id" in data
    assert isinstance(data["id"], int)


def test_add_book_response_matches_input(client: TestClient) -> None:
    payload = {
        "title": "Dune",
        "author": "Frank Herbert",
        "publicationYear": 1965,
        "genre": "Fiction",
    }

    data = client.post("/books/", json=payload).json()

    assert data["title"] == "Dune"
    assert data["author"] == "Frank Herbert"
    assert data["publicationYear"] == 1965
    assert data["genre"] == "Fiction"


def test_add_book_accepts_snake_case_input(client: TestClient) -> None:
    payload = {
        "title": "Snake",
        "author": "Author",
        "publication_year": 2021,
        "genre": "Fiction",
    }

    assert client.post("/books/", json=payload).status_code == 201


def test_add_book_horror_returns_422(client: TestClient) -> None:
    payload = {
        "title": "The Shining",
        "author": "Stephen King",
        "publicationYear": 1977,
        "genre": "Horror",
    }

    assert client.post("/books/", json=payload).status_code == 422


def test_add_book_horror_detail_mentions_horror(client: TestClient) -> None:
    payload = {
        "title": "It",
        "author": "S. King",
        "publicationYear": 1986,
        "genre": "Horror",
    }

    response = client.post("/books/", json=payload).json()
    # Pydantic validation errors are nested under "detail" -> list of errors
    detail_str = str(response["detail"])

    assert "Horror" in detail_str


def test_add_book_missing_required_field_returns_422(client: TestClient) -> None:
    payload = {"title": "No Author", "publicationYear": 2020, "genre": "Fiction"}

    assert client.post("/books/", json=payload).status_code == 422


def test_add_book_wrong_type_for_year_returns_422(client: TestClient) -> None:
    payload = {
        "title": "T",
        "author": "A",
        "publicationYear": "not-a-number",
        "genre": "Fiction",
    }

    assert client.post("/books/", json=payload).status_code == 422


def test_add_book_adult_genre_is_allowed(client: TestClient) -> None:
    payload = {
        "title": "Adult Book",
        "author": "Author",
        "publicationYear": 2020,
        "genre": "18+",
    }

    assert client.post("/books/", json=payload).status_code == 201


def test_add_book_multiple_books_get_distinct_ids(client: TestClient) -> None:
    def payload(n: int) -> dict[str, object]:
        return {
            "title": f"Book {n}",
            "author": "A",
            "publicationYear": 2020,
            "genre": "Fiction",
        }

    id1 = client.post("/books/", json=payload(1)).json()["id"]
    id2 = client.post("/books/", json=payload(2)).json()["id"]

    assert id1 != id2


# ---------------------------------------------------------------------------
# GET /books
# ---------------------------------------------------------------------------


def test_list_books_returns_200(client: TestClient) -> None:
    assert client.get("/books/").status_code == 200


def test_list_books_empty_db_returns_empty_genres(client: TestClient) -> None:
    assert client.get("/books/").json() == {"genres": []}


def test_list_books_groups_by_genre(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/").json()
    genre_names = {g["genre"] for g in data["genres"]}

    assert "Fiction" in genre_names
    assert "Mystery" in genre_names


def test_list_books_count_matches_number_of_books(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/").json()

    for group in data["genres"]:
        assert group["count"] == len(group["books"])


def test_list_books_fiction_count_is_correct(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/").json()
    fiction_group = next(g for g in data["genres"] if g["genre"] == "Fiction")
    expected = sum(1 for b in sample_books if b.genre == "Fiction")

    assert fiction_group["count"] == expected


def test_list_books_adult_title_is_masked_as_stars(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/").json()
    adult_group = next(g for g in data["genres"] if g["genre"] == "18+")

    for book in adult_group["books"]:
        assert book["title"] == "***"


def test_list_books_adult_other_fields_are_not_masked(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/").json()
    adult_group = next(g for g in data["genres"] if g["genre"] == "18+")

    for book in adult_group["books"]:
        assert book["author"] != "***"
        assert book["genre"] == "18+"


def test_list_books_non_adult_titles_are_not_masked(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/").json()

    for group in data["genres"]:
        if group["genre"] != "18+":
            for book in group["books"]:
                assert book["title"] != "***"


def test_list_books_response_uses_camel_case(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/").json()
    book = data["genres"][0]["books"][0]

    assert "publicationYear" in book
    assert "publication_year" not in book


# ---------------------------------------------------------------------------
# PUT /books
# ---------------------------------------------------------------------------


def test_update_books_returns_200(client: TestClient, sample_books: list[Book]) -> None:
    payload = [{"id": sample_books[0].id, "title": "Updated"}]

    assert client.put("/books/", json=payload).status_code == 200


def test_update_books_title_is_changed(
    client: TestClient, sample_books: list[Book]
) -> None:
    book = sample_books[0]
    payload = [{"id": book.id, "title": "New Title"}]

    data = client.put("/books/", json=payload).json()

    assert data[0]["title"] == "New Title"


def test_update_books_id_stays_the_same(
    client: TestClient, sample_books: list[Book]
) -> None:
    book = sample_books[0]
    payload = [{"id": book.id, "title": "Changed"}]

    assert client.put("/books/", json=payload).json()[0]["id"] == book.id


def test_update_books_partial_update_preserves_other_fields(
    client: TestClient, sample_books: list[Book]
) -> None:
    book = sample_books[0]
    original_author = book.author
    payload = [{"id": book.id, "title": "Only Title Changed"}]

    data = client.put("/books/", json=payload).json()

    assert data[0]["author"] == original_author


def test_update_books_not_found_returns_404(client: TestClient) -> None:
    payload = [{"id": 9999, "title": "Ghost"}]

    assert client.put("/books/", json=payload).status_code == 404


def test_update_books_not_found_detail_contains_id(client: TestClient) -> None:
    payload = [{"id": 9999, "title": "Ghost"}]

    detail = client.put("/books/", json=payload).json()["detail"]

    assert "9999" in detail


def test_update_books_multiple_books_at_once(
    client: TestClient, sample_books: list[Book]
) -> None:
    b1, b2 = sample_books[0], sample_books[1]
    payload = [
        {"id": b1.id, "title": "First Updated"},
        {"id": b2.id, "title": "Second Updated"},
    ]

    data = client.put("/books/", json=payload).json()

    assert len(data) == 2
    titles = {b["title"] for b in data}
    assert "First Updated" in titles
    assert "Second Updated" in titles


def test_update_books_genre_can_be_changed(
    client: TestClient, sample_books: list[Book]
) -> None:
    book = sample_books[0]
    payload = [{"id": book.id, "genre": "Fantasy"}]

    data = client.put("/books/", json=payload).json()

    assert data[0]["genre"] == "Fantasy"


def test_update_books_horror_genre_returns_422(
    client: TestClient, sample_books: list[Book]
) -> None:
    payload = [{"id": sample_books[0].id, "genre": "Horror"}]

    assert client.put("/books/", json=payload).status_code == 422


def test_update_books_horror_genre_detail_message(
    client: TestClient, sample_books: list[Book]
) -> None:
    payload = [{"id": sample_books[0].id, "genre": "Horror"}]

    detail_str = str(client.put("/books/", json=payload).json()["detail"])

    assert "Horror" in detail_str


# ---------------------------------------------------------------------------
# DELETE /books/{book_id}
# ---------------------------------------------------------------------------


def test_delete_book_returns_204(client: TestClient, sample_books: list[Book]) -> None:
    fiction = [b for b in sample_books if b.genre == "Fiction"]

    assert client.delete(f"/books/{fiction[0].id}").status_code == 204


def test_delete_book_not_found_returns_404(client: TestClient) -> None:
    assert client.delete("/books/9999").status_code == 404


def test_delete_book_not_found_detail_contains_id(client: TestClient) -> None:
    detail = client.delete("/books/9999").json()["detail"]

    assert "9999" in detail


def test_delete_book_last_in_genre_returns_400(
    client: TestClient, sample_books: list[Book]
) -> None:
    mystery = next(b for b in sample_books if b.genre == "Mystery")

    assert client.delete(f"/books/{mystery.id}").status_code == 400


def test_delete_book_last_in_genre_detail_mentions_genre(
    client: TestClient, sample_books: list[Book]
) -> None:
    mystery = next(b for b in sample_books if b.genre == "Mystery")

    detail = client.delete(f"/books/{mystery.id}").json()["detail"]

    assert "Mystery" in detail


def test_delete_book_reduces_genre_count(
    client: TestClient, sample_books: list[Book]
) -> None:
    fiction = [b for b in sample_books if b.genre == "Fiction"]
    client.delete(f"/books/{fiction[0].id}")
    # Should still be able to delete the second fiction book only if more exist
    data = client.get("/books/").json()

    fiction_group = next(g for g in data["genres"] if g["genre"] == "Fiction")

    assert fiction_group["count"] == len(fiction) - 1


def test_delete_last_remaining_book_of_non_fiction_genre_blocked(
    client: TestClient, sample_books: list[Book]
) -> None:
    nonfiction = next(b for b in sample_books if b.genre == "Nonfiction")

    assert client.delete(f"/books/{nonfiction.id}").status_code == 400


# ---------------------------------------------------------------------------
# GET /books/search
# ---------------------------------------------------------------------------


def test_search_books_returns_200(client: TestClient, sample_books: list[Book]) -> None:
    assert client.get("/books/search").status_code == 200


def test_search_books_no_params_returns_all_non_adult(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search").json()
    genres = {b["genre"] for b in data}

    assert "18+" not in genres


def test_search_books_excludes_adult_genre_even_with_matching_author(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"author": "E.L. James"}).json()

    assert data == []


def test_search_books_by_q_matches_title(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"q": "Gatsby"}).json()

    assert len(data) == 1
    assert data[0]["title"] == "The Great Gatsby"


def test_search_books_by_q_matches_author(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"q": "Orwell"}).json()

    assert len(data) == 1
    assert data[0]["author"] == "George Orwell"


def test_search_books_by_title_param(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"title": "Da Vinci"}).json()

    assert data[0]["title"] == "The Da Vinci Code"


def test_search_books_by_author_param(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"author": "Orwell"}).json()

    assert data[0]["author"] == "George Orwell"


def test_search_books_by_publication_year(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"publication_year": 1949}).json()

    assert len(data) == 1
    assert data[0]["title"] == "1984"


def test_search_books_no_match_returns_empty_list(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"q": "xyznonexistent"}).json()

    assert data == []


def test_search_books_response_uses_camel_case(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"q": "Gatsby"}).json()

    assert "publicationYear" in data[0]
    assert "publication_year" not in data[0]


def test_search_books_response_schema_has_all_required_fields(
    client: TestClient, sample_books: list[Book]
) -> None:
    data = client.get("/books/search", params={"q": "Gatsby"}).json()
    book = data[0]

    for field in ("id", "title", "author", "publicationYear", "genre"):
        assert field in book


def test_search_books_q_is_case_insensitive(
    client: TestClient, sample_books: list[Book]
) -> None:
    lower = client.get("/books/search", params={"q": "gatsby"}).json()
    upper = client.get("/books/search", params={"q": "GATSBY"}).json()

    assert len(lower) == len(upper) == 1
