class HorrorGenreNotAllowedError(Exception):
    def __init__(self) -> None:
        super().__init__("Books with genre 'Horror' cannot be added.")


class BookNotFoundError(Exception):
    def __init__(self, book_id: int) -> None:
        self.book_id = book_id
        super().__init__(f"Book with id {book_id} not found.")
