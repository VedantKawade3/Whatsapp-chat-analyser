from __future__ import annotations

from typing import Any, Dict, List

def build_insight_prompt(profile: Dict[str, Any]) -> str:
    sample_messages = profile.get("sample_messages", [])
    topics = profile.get("top_keywords", [])
    hours = profile.get("top_active_hours", [])
    days = profile.get("top_active_days", [])

    messages_block = "\n".join(
        f"{i + 1}. {msg}" for i, msg in enumerate(sample_messages)
    ) or "No sample messages available."

    return f"""
You are an AI communication analyst for WhatsApp chats.

Task:
Analyze the user's communication behavior from the provided evidence and return ONLY valid JSON that matches the requested schema.

Hard rules:
- Do NOT diagnose medical, psychological, or psychiatric conditions.
- Do NOT infer protected traits such as religion, caste, ethnicity, nationality, sexuality, political views, age, or health.
- Base conclusions only on observable chat evidence.
- If evidence is weak, say so and lower confidence.
- Keep the output concise, specific, and practical.

Evidence:
User: {profile.get("user", "Unknown")}
Total messages: {profile.get("total_messages", 0)}
Text messages after cleanup: {profile.get("text_messages", 0)}
Media messages: {profile.get("media_messages", 0)}
Link messages: {profile.get("link_messages", 0)}
Top active hours: {hours}
Top active days: {days}
Top keywords: {topics}

Sample messages:
{messages_block}

Return JSON with this shape:
{{
  "communication_style": "string",
  "tone": "string",
  "conversation_behavior": "string",
  "dominant_topics": ["string"],
  "social_style": "string",
  "strengths": ["string"],
  "watchouts": ["string"],
  "summary": "string",
  "confidence": "low | medium | high"
}}
""".strip()