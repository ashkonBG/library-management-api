class HorrorGenreNotAllowedError(Exception):
    def __init__(self) -> None:
        super().__init__("Books with genre 'Horror' cannot be added.")
