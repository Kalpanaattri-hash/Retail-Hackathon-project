import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import SessionLocal
from app.routers.chat_router import router as chat_router
from app.routers.dashboard_router import router as dashboard_router
from app.services.analytics_service import AnalyticsService, ConversationMemory
from app.services.bedrock_service import BedrockService
from app.services.sql_generator import SQLGenerator


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    bedrock_service = BedrockService()
    sql_generator = SQLGenerator(bedrock_service)
    memory = ConversationMemory(max_size=settings.memory_size)

    app.state.analytics_service = AnalyticsService(
        db_session_factory=SessionLocal,
        sql_generator=sql_generator,
        bedrock_service=bedrock_service,
        memory=memory,
    )
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(dashboard_router)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": settings.app_name, "environment": settings.app_env}


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": "HTTP_ERROR", "detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled server error: %s", exc)
    return JSONResponse(status_code=500, content={"error": "INTERNAL_SERVER_ERROR", "detail": "Something went wrong"})
