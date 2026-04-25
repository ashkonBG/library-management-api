from fastapi import FastAPI

from src.config.app_settings import app_settings

app = FastAPI(
    title=app_settings.name,
    version=app_settings.version,
    debug=app_settings.debug,
    description="An API for managing a library of books.",
    generate_unique_id_function=lambda route: route.name,
)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "app": app_settings.name,
        "version": app_settings.version,
    }
