class BookNotFoundError(Exception):
    def __init__(self, book_id: int) -> None:
        self.book_id = book_id
        super().__init__(f"Book with id {book_id} not found.")


class LastBookInGenreError(Exception):
    def __init__(self, genre: object) -> None:
        genre_str: str = genre.value if hasattr(genre, "value") else str(genre)
        self.genre = genre_str
        super().__init__(f"Cannot delete the last book in genre '{genre_str}'.")
