import json
import logging
import re
from dataclasses import dataclass

from app.config import get_settings
from app.services.bedrock_service import BedrockService
from app.utils.prompt_templates import sql_generation_prompt

logger = logging.getLogger(__name__)

BLOCKED_KEYWORDS = {
    "DELETE",
    "DROP",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "MERGE",
}


class SQLGenerationError(Exception):
    pass


class SQLValidationError(Exception):
    pass


@dataclass
class SQLGenerationResult:
    sql: str
    rationale: str


class SQLGenerator:
    def __init__(self, bedrock_service: BedrockService) -> None:
        self.bedrock_service = bedrock_service
        self.settings = get_settings()

    def generate_sql(self, question: str, recent_history: list[dict[str, str]]) -> SQLGenerationResult:
        system_prompt, user_prompt = sql_generation_prompt(
            question=question,
            allowed_tables=self.settings.allowed_tables_set,
            recent_history=recent_history,
        )

        raw_output = self.bedrock_service.generate_text(system_prompt, user_prompt)
        parsed = self._parse_bedrock_json(raw_output)
        sql = self.validate_and_normalize_sql(parsed.get("sql", ""))

        return SQLGenerationResult(
            sql=sql,
            rationale=parsed.get("rationale", "Generated from business intent"),
        )

    def _parse_bedrock_json(self, response_text: str) -> dict:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if not match:
                logger.error("Unable to parse Bedrock JSON response: %s", response_text)
                raise SQLGenerationError("Model returned invalid SQL payload")
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                logger.error("Unable to parse extracted JSON: %s", response_text)
                raise SQLGenerationError("Model returned unparsable SQL payload") from exc

    def validate_and_normalize_sql(self, sql: str) -> str:
        if not sql or not sql.strip():
            raise SQLValidationError("Generated SQL is empty")

        clean_sql = self._strip_sql_comments(sql).strip().rstrip(";")
        if ";" in clean_sql:
            raise SQLValidationError("Multiple SQL statements are not allowed")

        if not re.match(r"^SELECT\b", clean_sql, re.IGNORECASE):
            raise SQLValidationError("Only SELECT statements are allowed")

        for keyword in BLOCKED_KEYWORDS:
            if re.search(rf"\b{keyword}\b", clean_sql, re.IGNORECASE):
                raise SQLValidationError(f"Blocked SQL keyword detected: {keyword}")

        self._validate_table_access(clean_sql)
        clean_sql = self._enforce_limit(clean_sql)

        return clean_sql

    def _validate_table_access(self, sql: str) -> None:
        table_pattern = re.compile(r"\b(?:FROM|JOIN)\s+([a-zA-Z_][\w\.]*)", re.IGNORECASE)
        found_tables = table_pattern.findall(sql)
        if not found_tables:
            raise SQLValidationError("Query must reference at least one allowed table")

        allowed = self.settings.allowed_tables_set
        for table in found_tables:
            base_name = table.split(".")[-1].strip('"').lower()
            if base_name not in allowed:
                raise SQLValidationError(f"Table '{base_name}' is not allowed")

    def _enforce_limit(self, sql: str) -> str:
        max_rows = self.settings.max_result_rows
        limit_match = re.search(r"\bLIMIT\s+(\d+)\b", sql, re.IGNORECASE)

        if not limit_match:
            return f"{sql} LIMIT {max_rows}"

        current_limit = int(limit_match.group(1))
        if current_limit <= max_rows:
            return sql

        return re.sub(r"\bLIMIT\s+\d+\b", f"LIMIT {max_rows}", sql, count=1, flags=re.IGNORECASE)

    @staticmethod
    def _strip_sql_comments(sql: str) -> str:
        sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
        sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
        return sql
