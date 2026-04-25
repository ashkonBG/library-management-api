from fastapi.testclient import TestClient

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
