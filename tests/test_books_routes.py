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


def test_add_book_horror_returns_400(client: TestClient) -> None:
    payload = {
        "title": "The Shining",
        "author": "Stephen King",
        "publicationYear": 1977,
        "genre": "Horror",
    }
    assert client.post("/books/", json=payload).status_code == 400


def test_add_book_horror_detail_mentions_horror(client: TestClient) -> None:
    payload = {
        "title": "It",
        "author": "S. King",
        "publicationYear": 1986,
        "genre": "Horror",
    }
    detail = client.post("/books/", json=payload).json()["detail"]
    assert "Horror" in detail


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
