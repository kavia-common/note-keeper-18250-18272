from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from .core.config import get_settings
from .core.database import get_engine, Base
from .routers.auth import router as auth_router
from .routers.notes import router as notes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan handler to initialize database tables on startup.

    Ensures all tables are created before serving requests.
    """
    engine: AsyncEngine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown not needed for now; engine will be cleaned up by process exit.


settings = get_settings()

openapi_tags = [
    {"name": "Health", "description": "Health check endpoint"},
    {"name": "Authentication", "description": "User registration and login"},
    {"name": "Notes", "description": "CRUD operations for notes"},
]

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

# CORS
allow_origins = [o.strip() for o in settings.CORS_ALLOW_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins if allow_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Simple health check endpoint returning a status message."""
    return {"message": "Healthy"}


# Include routers
app.include_router(auth_router)
app.include_router(notes_router)
