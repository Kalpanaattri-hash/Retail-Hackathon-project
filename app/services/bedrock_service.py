import json
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings

logger = logging.getLogger(__name__)


class BedrockServiceError(Exception):
    pass


class BedrockService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_id = settings.bedrock_model_id
        self.client = boto3.client("bedrock-runtime", region_name=settings.aws_region)

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ) -> str:
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "system": system_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user_prompt}],
                }
            ],
        }

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json",
            )
            body = json.loads(response["body"].read())
            content = body.get("content", [])
            text_output = "".join(
                item.get("text", "") for item in content if item.get("type") == "text"
            )
            if not text_output.strip():
                raise BedrockServiceError("Bedrock returned empty response")
            return text_output.strip()

        except (BotoCoreError, ClientError) as exc:
            logger.exception("Bedrock invocation failed")
            raise BedrockServiceError("Bedrock request failed") from exc
        except (KeyError, json.JSONDecodeError) as exc:
            logger.exception("Invalid Bedrock response format")
            raise BedrockServiceError("Invalid Bedrock response") from exc
