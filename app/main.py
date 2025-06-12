from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import sentry_sdk
from prometheus_client import Counter, Histogram
from opentelemetry import trace
from .core.config import settings
from .core.logging import logger
from .api.routes import router
from .db.database import db_manager

# Initialize monitoring
if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn)

# Initialize metrics
QUERY_PROCESSING_TIME = Histogram(
    'query_processing_seconds',
    'Time spent processing queries'
)

# Initialize tracing
if settings.tracing_enabled:
    tracer = trace.get_tracer(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Query Processor API")
    if not await db_manager.test_connection():
        logger.error("Failed to connect to database on startup")
    else:
        logger.info("Database connection successful")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Query Processor API")
    if db_manager.engine:
        await db_manager.engine.dispose()

app = FastAPI(
    title="Query Processor API",
    description="Production-ready API for processing SQL queries",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.allowed_hosts != ["*"]:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Include routers
app.include_router(router)
