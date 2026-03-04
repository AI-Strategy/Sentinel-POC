"""
sentinel/core/llm.py
--------------------
Unified LLM client backed by the modern Google Gemini SDK (google-genai).

Replaces legacy google-generativeai calls throughout Sentinel.
Exposes two interfaces:

  GeminiClient.complete(prompt)         â†’ str
  GeminiClient.complete_vision(prompt, images)  â†’ str   (base64 image list)

Both return raw text. JSON callers must parse themselves.

Model routing:
  Text tasks  â†’ gemini-1.5-flash          (fast, cheap)
  Vision tasks â†’ gemini-1.5-flash          (native multimodal)

Configuration (env vars or explicit):
  GEMINI_API_KEY   â€” required
  GEMINI_TEXT_MODEL  â€” default: gemini-1.5-flash
  GEMINI_VISION_MODEL â€” default: gemini-1.5-flash
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

# â”€â”€ Defaults â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

DEFAULT_TEXT_MODEL   = "gemini-2.5-flash"
DEFAULT_VISION_MODEL = "gemini-2.5-flash"


# â”€â”€ Client â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class GeminiClient:
    """
    Thin wrapper around the google-genai SDK.
    Eliminates reliance on deprecated google-generativeai.
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
            if not self.api_key:
                logger.warning("GEMINI_API_KEY not set â€” LLM features disabled.")
                return
            
            # Use the new Client constructor
            self._client    = genai.Client(api_key=self.api_key)
            self._genai_pkg = genai
            self._available = True
            logger.info("Gemini (google-genai) client initialised (text=%s, vision=%s)",
                        self.text_model, self.vision_model)
        except ImportError:
            logger.warning(
                "google-genai not installed. "
                "Run: pip install google-genai"
            )

    @property
    def available(self) -> bool:
        return self._available

    # â”€â”€ Text completion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def complete(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Send a text prompt, return raw response string."""
        if not self._available:
            raise RuntimeError("Gemini client not available (check GEMINI_API_KEY and install google-genai)")
        
        from google.genai import types
        try:
            response = self._client.models.generate_content(
                model=self.text_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text.strip()
        except Exception as exc:
            logger.error("Gemini complete() failed: %s", exc)
            raise

    # â”€â”€ Vision completion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def complete_vision(
        self,
        prompt: str,
        images: list[dict],           # [{"data": base64str, "mime_type": "image/png"}, ...]
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Send a multimodal prompt with images, return raw response string."""
        if not self._available:
            raise RuntimeError("Gemini client not available")
            
        from google.genai import types
        try:
            import PIL.Image
            import io as _io

            # Construct multimodal parts
            contents: list[Any] = []
            for img in images:
                raw_bytes = base64.b64decode(img["data"])
                pil_img   = PIL.Image.open(_io.BytesIO(raw_bytes))
                contents.append(pil_img)
            
            # The prompt is also part of the contents
            contents.append(prompt)

            response = self._client.models.generate_content(
                model=self.vision_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return response.text.strip()
        except ImportError:
            raise RuntimeError("Pillow not installed: pip install Pillow")
        except Exception as exc:
            logger.error("Gemini complete_vision() failed: %s", exc)
            raise

    # â”€â”€ JSON helper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def complete_json(
        self,
        prompt: str,
        max_tokens: int = 4096,
        images: list[dict] | None = None,
    ) -> dict | list:
        """
        Send a prompt that expects a JSON response.
        Strips markdown fences and parses automatically.
        Raises ValueError if parsing fails.
        """
        raw = (
            self.complete_vision(prompt, images, max_tokens=max_tokens)
            if images
            else self.complete(prompt, max_tokens=max_tokens)
        )
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error("Gemini JSON parse failed.\nRaw:\n%s\nError: %s", raw[:500], exc)
            raise ValueError(f"Gemini returned non-JSON: {exc}") from exc


# â”€â”€ Module-level singleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_DEFAULT_CLIENT: GeminiClient | None = None


def get_client(
    api_key: str | None = None,
    text_model: str = DEFAULT_TEXT_MODEL,
    vision_model: str = DEFAULT_VISION_MODEL,
) -> GeminiClient:
    """Return (or create) the module-level default Gemini client."""
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None or api_key:
        _DEFAULT_CLIENT = GeminiClient(
            api_key=api_key,
            text_model=text_model,
            vision_model=vision_model,
        )
    return _DEFAULT_CLIENT
