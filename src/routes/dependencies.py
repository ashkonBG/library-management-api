from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.session import create_db_session


def get_db_session() -> Generator[Session, None, None]:
    session = create_db_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


DatabaseDependency = Annotated[Session, Depends(get_db_session)]
