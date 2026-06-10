import asyncio
import json
import random
from typing import Any

import httpx
from azure.core.exceptions import ClientAuthenticationError
from azure.identity.aio import DefaultAzureCredential

from .config import Settings


RETRYABLE_STATUS_CODES = {429, 502, 503, 504}


class FoundryError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class FoundryClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.credential = DefaultAzureCredential()
        self.http = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.foundry_timeout_seconds, connect=10),
            limits=httpx.Limits(
                max_connections=settings.max_concurrent_foundry_calls,
                max_keepalive_connections=settings.max_concurrent_foundry_calls,
            ),
        )
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_foundry_calls)

    async def close(self) -> None:
        await self.http.aclose()
        await self.credential.close()

    async def validate_invoice(self, invoice_number: str) -> tuple[Any, str | None]:
        if not self.settings.foundry_agent_endpoint:
            raise FoundryError("Foundry Agent Application endpoint is not configured", 503)

        payload = {
            "input": (
                "Validate this invoice using the configured invoice-risk workflow. "
                f"Invoice number: {invoice_number}. Return the final structured decision."
            )
        }

        try:
            await asyncio.wait_for(self.semaphore.acquire(), timeout=self.settings.queue_timeout_seconds)
        except TimeoutError as exc:
            raise FoundryError("Validation capacity is busy; retry shortly", 503) from exc
        try:
            response = await self._post_with_retry(payload)
        finally:
            self.semaphore.release()

        try:
            body = response.json()
        except json.JSONDecodeError as exc:
            raise FoundryError("Foundry returned a malformed response") from exc
        return self._extract_result(body), body.get("id")

    async def _post_with_retry(self, payload: dict[str, Any]) -> httpx.Response:
        url = f"{self.settings.foundry_agent_endpoint}/responses"
        for attempt in range(self.settings.foundry_max_retries + 1):
            try:
                token = await self.credential.get_token("https://ai.azure.com/.default")
            except ClientAuthenticationError as exc:
                raise FoundryError("Managed identity could not authenticate to Foundry", 503) from exc
            try:
                response = await self.http.post(
                    url,
                    params={"api-version": self.settings.foundry_api_version},
                    headers={
                        "Authorization": f"Bearer {token.token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            except httpx.TransportError as exc:
                if attempt >= self.settings.foundry_max_retries:
                    raise FoundryError("Foundry endpoint is unavailable", 503) from exc
                await self._backoff(attempt)
                continue

            if response.status_code in RETRYABLE_STATUS_CODES and attempt < self.settings.foundry_max_retries:
                retry_after = response.headers.get("retry-after")
                await self._backoff(attempt, float(retry_after) if retry_after and retry_after.isdigit() else None)
                continue

            if response.is_error:
                status = 503 if response.status_code in RETRYABLE_STATUS_CODES else 502
                raise FoundryError(f"Foundry request failed with status {response.status_code}", status)
            return response

        raise FoundryError("Foundry request failed after retries", 503)

    @staticmethod
    async def _backoff(attempt: int, retry_after: float | None = None) -> None:
        delay = retry_after if retry_after is not None else min(8, 0.5 * (2**attempt)) + random.random() * 0.25
        await asyncio.sleep(delay)

    @staticmethod
    def _extract_result(body: dict[str, Any]) -> Any:
        text_parts: list[str] = []
        for output in body.get("output", []):
            for content in output.get("content", []):
                text = content.get("text")
                if text:
                    text_parts.append(text)
        text = "\n".join(text_parts).strip()
        if not text:
            return body
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"summary": text}
