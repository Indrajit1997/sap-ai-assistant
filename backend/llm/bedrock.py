from __future__ import annotations

import json
from collections.abc import AsyncIterator

import structlog

from backend.config import get_settings
from backend.llm.base import LLMBase, LLMResponse

log = structlog.get_logger()


class BedrockLLM(LLMBase):
    """AWS Bedrock Claude adapter."""

    def __init__(self):
        import boto3
        settings = get_settings()
        self._client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
        self._model_id = settings.bedrock_model_id

    async def generate(self, prompt: str, system: str = "", max_tokens: int = 2048) -> LLMResponse:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system

        response = self._client.invoke_model(
            modelId=self._model_id,
            body=json.dumps(body),
        )
        result = json.loads(response["body"].read())

        return LLMResponse(
            content=result["content"][0]["text"],
            model=self._model_id,
            usage=result.get("usage"),
        )

    async def generate_stream(self, prompt: str, system: str = "", max_tokens: int = 2048) -> AsyncIterator[str]:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system

        response = self._client.invoke_model_with_response_stream(
            modelId=self._model_id,
            body=json.dumps(body),
        )

        for event in response["body"]:
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                yield chunk["delta"].get("text", "")
