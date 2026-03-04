"""
sentinel/core/llm.py (v1.5)
--------------------
Unified LLM client backed by the modern Google Gemini SDK (google-genai).
Supports Native PDF/Vision processing and Structured Outputs (JSON Schema).

Replaces legacy google-generativeai calls throughout Sentinel.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
from typing import Any, Optional, Type, Union
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_TEXT_MODEL   = "gemini-2.0-flash"
DEFAULT_VISION_MODEL = "gemini-2.0-flash"


# ── Client ───────────────────────────────────────────────────────────────────

class GeminiClient:
    """
    Thin wrapper around the google-genai SDK.
    Supports native bytes (PDF/Images) and Structured Response schemas.
    """

    def __init__(
        self,
        api_key: str | None = None,
        text_model: str = DEFAULT_TEXT_MODEL,
        vision_model: str = DEFAULT_VISION_MODEL,
    ):
        self.api_key      = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.text_model   = text_model
        self.vision_model = vision_model
        self._client      = None
        self._available   = False
        self._init()

    def _init(self):
        try:
            from google import genai
            # Check for Vertex AI environment variables
            use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
            
            if use_vertex:
                project = os.environ.get("GOOGLE_CLOUD_PROJECT")
                location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
                self._client = genai.Client(vertexai=True, project=project, location=location)
                logger.info("Gemini initialized via Vertex AI (project=%s, location=%s)", project, location)
            else:
                if not self.api_key:
                    logger.warning("GEMINI_API_KEY not set — LLM features disabled.")
                    return
                self._client = genai.Client(api_key=self.api_key)
            
            self._genai_pkg = genai
            self._available = True
        except ImportError:
            logger.warning("google-genai not installed. Run: pip install google-genai")

    @property
    def available(self) -> bool:
        return self._available

    def complete(
        self,
        prompt: Union[str, list[Any]],
        max_tokens: int = 4096,
        temperature: float = 0.1,
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Any:
        """
        Generates content. Supports multimodal 'contents' list and structured output.
        If response_schema is provided, returns the parsed model instance/dict.
        """
        if not self._available:
            raise RuntimeError("Gemini client not available.")
        
        from google.genai import types
        
        config_kwargs = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if response_schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = response_schema

        try:
            response = self._client.models.generate_content(
                model=self.text_model,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )
            
            if response_schema:
                # If it's structured output, google-genai returns the parsed data in response.parsed
                # or we can manually parse response.text if using older SDK versions
                if hasattr(response, "parsed") and response.parsed:
                    return response.parsed
                return json.loads(response.text)
            
            return response.text.strip()
        except Exception as exc:
            logger.error("Gemini model.generate_content failed: %s", exc)
            raise

    def complete_json(
        self,
        prompt: str,
        images: list[dict] | None = None,
        max_tokens: int = 4096,
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> Any:
        """
        Legacy-compatible wrapper for JSON tasks. 
        Now supports direct structured output via Pydantic.
        """
        contents = [prompt]
        if images:
            from google.genai import types
            for img in images:
                # Transform legacy internal format to google-genai types.Part
                if "data" in img:
                    contents.append(
                        types.Part.from_bytes(
                            data=base64.b64decode(img["data"]),
                            mime_type=img.get("mime_type", "image/png")
                        )
                    )
        
        return self.complete(contents, max_tokens=max_tokens, response_schema=response_schema)


# ── Module-level singleton ────────────────────────────────────────────────────

_DEFAULT_CLIENT: GeminiClient | None = None

def get_client(
    api_key: str | None = None,
    text_model: str = DEFAULT_TEXT_MODEL,
    vision_model: str = DEFAULT_VISION_MODEL,
) -> GeminiClient:
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None or api_key:
        _DEFAULT_CLIENT = GeminiClient(
            api_key=api_key,
            text_model=text_model,
            vision_model=vision_model,
        )
    return _DEFAULT_CLIENT
