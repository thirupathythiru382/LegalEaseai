from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.routes import router
from backend.schemas import HealthResponse


settings = get_settings()


app = FastAPI(
    title="LegalEase API",
    description=(
        "AI-assisted legal document drafting API "
        "for the LegalEase project."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.cors_origin_list,

    allow_credentials=False,

    allow_methods=[
        "GET",
        "POST",
    ],

    allow_headers=["*"],
)


app.include_router(router)


@app.get(
    "/",
    response_model=HealthResponse,
)
def root():

    return HealthResponse(
        status="ok",
        app=settings.app_name,
    )


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health():

    return HealthResponse(
        status="ok",
        app=settings.app_name,
    )