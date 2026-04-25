from fastapi import APIRouter

books_router = APIRouter(prefix="/books", tags=["Books"])
