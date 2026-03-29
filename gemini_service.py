from __future__ import annotations

import os
from typing import List, Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class GeminiInsight(BaseModel):
    communication_style: str = Field(default="")
    tone: str = Field(default="")
    conversation_behavior: str = Field(default="")
    dominant_topics: List[str] = Field(default_factory=list)
    social_style: str = Field(default="")
    strengths: List[str] = Field(default_factory=list)
    watchouts: List[str] = Field(default_factory=list)
    summary: str = Field(default="")
    confidence: Literal["low", "medium", "high"] = "medium"

def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)
        if len(text) >= 2:
            text = text[1]
    return text.strip()

class GeminiInsightService:
    def __init__(self, api_key: str | None = None, model_name: str = "gemini-2.5-flash"):
        key = (api_key or os.getenv("GEMINI_API_KEY") or "").strip()
        if not key:
            raise ValueError("GEMINI_API_KEY is missing.")

        os.environ["GEMINI_API_KEY"] = key
        self.client = genai.Client()
        self.model_name = model_name

    def analyze(self, prompt: str) -> GeminiInsight:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": GeminiInsight.model_json_schema(),
            },
        )

        raw = _strip_code_fences(response.text or "")
        if not raw:
            raise RuntimeError("Gemini returned an empty response.")

        try:
            return GeminiInsight.model_validate_json(raw)
        except Exception:
            return GeminiInsight(
                communication_style="",
                tone="",
                conversation_behavior="",
                dominant_topics=[],
                social_style="",
                strengths=[],
                watchouts=[],
                summary=raw,
                confidence="low",
            )