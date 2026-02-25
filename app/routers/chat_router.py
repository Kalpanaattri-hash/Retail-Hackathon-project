import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas import ChatRequest, ChatResponse
from app.services.analytics_service import AnalyticsService, AnalyticsServiceError
from app.services.sql_generator import SQLValidationError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


def get_analytics_service(request: Request) -> AnalyticsService:
    return request.app.state.analytics_service


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, service: AnalyticsService = Depends(get_analytics_service)) -> ChatResponse:
    try:
        result = service.process_question(payload.question)
        return ChatResponse(**result)
    except SQLValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid generated SQL: {exc}",
        ) from exc
    except AnalyticsServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in /chat")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error",
        ) from exc
