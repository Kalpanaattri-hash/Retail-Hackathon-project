import json
import logging
from collections import deque
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Callable

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.services.bedrock_service import BedrockService, BedrockServiceError
from app.services.sql_generator import SQLGenerationError, SQLGenerator
from app.utils.prompt_templates import business_summary_prompt, follow_up_questions_prompt

logger = logging.getLogger(__name__)


class AnalyticsServiceError(Exception):
    pass


class ConversationMemory:
    def __init__(self, max_size: int) -> None:
        self._history: deque[dict[str, str]] = deque(maxlen=max_size)

    def add(self, question: str, sql: str) -> None:
        self._history.append({"question": question, "sql": sql})

    def get_recent(self) -> list[dict[str, str]]:
        return list(self._history)


class AnalyticsService:
    def __init__(
        self,
        db_session_factory: Callable,
        sql_generator: SQLGenerator,
        bedrock_service: BedrockService,
        memory: ConversationMemory,
    ) -> None:
        self.db_session_factory = db_session_factory
        self.sql_generator = sql_generator
        self.bedrock_service = bedrock_service
        self.memory = memory

    def process_question(self, question: str) -> dict:
        try:
            generated = self.sql_generator.generate_sql(question, self.memory.get_recent())
            rows = self._execute_query(generated.sql)
            answer = self._summarize(question, generated.sql, rows)
            follow_up_questions = self._generate_follow_up_questions(question, answer, rows)
            self.memory.add(question, generated.sql)

            return {
                "answer": answer,
                "generated_sql": generated.sql,
                "data_preview": rows[:20],
                "follow_up_questions": follow_up_questions,
            }

        except (SQLGenerationError, BedrockServiceError) as exc:
            logger.warning("Model processing failed: %s", exc)
            raise AnalyticsServiceError(str(exc)) from exc

    @contextmanager
    def _db_session(self):
        db = self.db_session_factory()
        try:
            yield db
        finally:
            db.close()

    def _execute_query(self, sql: str) -> list[dict]:
        try:
            with self._db_session() as db:
                result = db.execute(text(sql))
                return [self._serialize_row(dict(row._mapping)) for row in result.fetchall()]
        except SQLAlchemyError as exc:
            logger.exception("Database query execution failed")
            raise AnalyticsServiceError("Database query failed") from exc

    def _summarize(self, question: str, sql: str, rows: list[dict]) -> str:
        if not rows:
            return "No matching sales records were found for this question."

        system_prompt, user_prompt = business_summary_prompt(question, sql, rows[:20])

        try:
            return self.bedrock_service.generate_text(
                system_prompt,
                user_prompt,
                temperature=0.2,
                max_tokens=400,
            )
        except BedrockServiceError:
            logger.warning("Falling back to deterministic summary")
            return f"Found {len(rows)} matching records. Here is a preview of the top results based on your query."

    def _serialize_row(self, row: dict) -> dict:
        serialized = {}
        for key, value in row.items():
            if isinstance(value, (datetime, date)):
                serialized[key] = value.isoformat()
            elif isinstance(value, Decimal):
                serialized[key] = float(value)
            else:
                serialized[key] = value
        return serialized

    def _generate_follow_up_questions(self, question: str, answer: str, rows: list[dict]) -> list[str]:
        system_prompt, user_prompt = follow_up_questions_prompt(question, answer, rows)

        try:
            raw_output = self.bedrock_service.generate_text(
                system_prompt,
                user_prompt,
                temperature=0.3,
                max_tokens=180,
            )
            parsed = json.loads(raw_output)

            if isinstance(parsed, dict):
                candidates = parsed.get("questions", [])
            elif isinstance(parsed, list):
                candidates = parsed
            else:
                candidates = []

            cleaned: list[str] = []
            for item in candidates:
                if isinstance(item, str):
                    text = item.strip()
                    if text and text not in cleaned:
                        cleaned.append(text)
                if len(cleaned) == 3:
                    break

            if len(cleaned) >= 2:
                return cleaned
        except (BedrockServiceError, json.JSONDecodeError, TypeError, ValueError):
            logger.debug("Using fallback follow-up questions", exc_info=True)

        return self._fallback_follow_up_questions(question)

    def _fallback_follow_up_questions(self, question: str) -> list[str]:
        question_lower = question.lower()

        if "region" in question_lower:
            return [
                "Can you show this trend month by month for each region?",
                "Which region had the highest growth versus last quarter?",
                "What is the contribution percentage of each region?",
            ]

        if "product" in question_lower or "category" in question_lower:
            return [
                "Which products contributed most to this result?",
                "How did each product category perform in the previous quarter?",
                "Can you show the top 5 products by revenue with quantity sold?",
            ]

        return [
            "Can you break this down by product category?",
            "How does this compare with the previous quarter?",
            "Can you show the monthly trend for this metric?",
        ]
