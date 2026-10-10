"""FastAPI application entry point.

Run it with:  uvicorn app.main:app --reload
Interactive docs:  http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager
import logging

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401  (registers the tables on Base.metadata)
from app.config import settings
from app.database import Base, engine, init_db
from app.routers import expenses, summary
from app.schemas import HealthResponse

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context: initialize database tables on startup."""
    init_db()
    yield


app = FastAPI(
    title="Personal Expense Tracker API",
    description=(
        "A simple REST API to create, read, update and delete personal expenses, "
        "with filtering and spending summaries."
    ),
    version="1.0.0",
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
    lifespan=lifespan,
)

# Enable CORS for frontend applications (React, Vue, mobile, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static web assets if available
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(expenses.router)
app.include_router(summary.router)


@app.get("/", tags=["root"], summary="Root endpoint")
def root_endpoint(request: Request):
    """Root endpoint welcoming visitors and providing documentation links.

    Serves the minimalist Single Page Application to browsers (Accept: text/html),
    and returns structured API metadata for machine clients.
    """
    accept = request.headers.get("accept", "")
    index_file = STATIC_DIR / "index.html"
    if "text/html" in accept and index_file.exists():
        return FileResponse(index_file)

    return {
        "title": "Personal Expense Tracker API",
        "status": "online",
        "docs_url": "/docs" if settings.docs_enabled else "disabled",
        "health_check": "/health",
        "app_ui": "/app",
    }


@app.get("/app", include_in_schema=False)
def app_ui():
    """Direct route to the SpendWise web application UI."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse(status_code=404, content={"detail": "Web UI not found"})


@app.get("/health", response_model=HealthResponse, tags=["health"], summary="Health check")
def health_check() -> HealthResponse:
    """Confirm that the API is running."""
    return HealthResponse(status="ok", message="Expense Tracker API is running")




@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Turn FastAPI's validation errors into a clear JSON response."""
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Never expose internal stack traces to API clients."""
    logger.error(
        "Unhandled error on %s %s", request.method, request.url.path, exc_info=exc
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
