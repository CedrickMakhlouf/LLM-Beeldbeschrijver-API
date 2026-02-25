import base64
import logging
import time
from typing import Any

import httpx
from openai import AzureOpenAI, InternalServerError

from app.core.settings import Settings

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 60
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


class VLMGenerator:
    """Genereert schermbeschrijvingen via een vision language model."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client, self._model = self._build_client(settings)

    @staticmethod
    def _build_client(settings: Settings) -> tuple[Any, str]:
        # Voorkeur: Azure AI Foundry inference endpoint (Llama etc.)
        if (
            settings.azure_inference_endpoint
            and settings.azure_inference_api_key
            and settings.azure_inference_deployment
        ):
            client = AzureOpenAI(
                api_key=settings.azure_inference_api_key,
                azure_endpoint=settings.azure_inference_endpoint,
                api_version=settings.azure_inference_api_version,
            )
            return client, settings.azure_inference_deployment
        # Fallback: Azure OpenAI (gpt-4o)
        if (
            settings.azure_openai_endpoint
            and settings.azure_openai_api_key
            and settings.azure_openai_deployment
        ):
            client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                azure_endpoint=settings.azure_openai_endpoint,
                api_version=settings.azure_openai_api_version,
            )
            return client, settings.azure_openai_deployment
        raise ValueError("Geen Azure-configuratie gevonden. Stel AZURE_INFERENCE_* of AZURE_OPENAI_* in.")

    def generate(
        self,
        image_base64: str | None = None,
        image_url: str | None = None,
        image_id: str | None = None,
    ) -> dict[str, Any]:
        if image_url and not image_base64:
            logger.info("Fetching image from URL: %s", image_url)
            try:
                resp = httpx.get(image_url, timeout=15, follow_redirects=True)
                resp.raise_for_status()
                img_bytes = resp.content
            except Exception as exc:
                logger.exception("Kon afbeelding niet ophalen van URL %s: %s", image_url, exc)
                raise
            image_base64 = base64.b64encode(img_bytes).decode()
        data_url = f"data:image/png;base64,{image_base64}"

        start = time.time()
        logger.info("Calling VLM model: %s", self._model)
        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": self._settings.default_vlm_prompt},
                                {"type": "image_url", "image_url": {"url": data_url}},
                            ],
                        }
                    ],
                    timeout=TIMEOUT_SECONDS,
                )
                break  # success
            except InternalServerError as exc:
                last_exc = exc
                logger.warning("VLM poging %d/%d mislukt (InternalServerError): %s", attempt, MAX_RETRIES, exc)
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)
        else:
            raise last_exc  # type: ignore[misc]
        description = response.choices[0].message.content.strip()
        logger.info("VLM responded in %dms", int((time.time() - start) * 1000))

        return {
            "image_id": image_id,
            "description": description,
            "processing_ms": int((time.time() - start) * 1000),
        }
