from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from cache import make_cache_key, read_cache, write_cache
from config import DEFAULT_GEMINI_MODEL, MAX_SAMPLE_CHARS, MAX_SAMPLE_MESSAGES, load_stop_words
from gemini_service import GeminiInsight, GeminiInsightService
from prompt_builder import build_insight_prompt

NOISE_PATTERN = r"(?:<media omitted>|this message was deleted|deleted this message|message deleted|you deleted this message)"

STOP_WORDS = load_stop_words()

def _filter_by_user(df: pd.DataFrame, selected_user: str) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if df is not None else [])
    if selected_user != "Overall":
        return df[df["user"] == selected_user].copy()
    return df.copy()

def _text_only(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    msg = df["message"].fillna("").astype(str)

    mask = ~msg.str.contains(NOISE_PATTERN, case=False, na=False, regex=True)
    mask &= msg.str.strip().ne("")
    mask &= df["user"].fillna("").ne("group_notification")

    return df.loc[mask].copy()

def _top_keywords(messages: List[str], top_n: int = 12) -> List[str]:
    counter = Counter()
    for message in messages:
        for word in re.findall(r"[A-Za-z0-9_']+", str(message).lower()):
            if word not in STOP_WORDS and len(word) > 1:
                counter[word] += 1
    return [word for word, _ in counter.most_common(top_n)]

def _downsample_messages(messages: List[str], max_messages: int, max_chars: int) -> List[str]:
    cleaned = []
    for msg in messages:
        text = re.sub(r"\s+", " ", str(msg)).strip()
        if not text:
            continue
        if len(text) > 220:
            text = text[:220].rstrip() + "…"
        cleaned.append(text)

    if not cleaned:
        return []

    if len(cleaned) > max_messages:
        step = max(1, len(cleaned) // max_messages)
        cleaned = cleaned[::step][:max_messages]

    final = []
    total_chars = 0
    for msg in cleaned:
        if total_chars + len(msg) > max_chars:
            break
        final.append(msg)
        total_chars += len(msg) + 1

    return final

def build_user_profile(selected_user: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    df_user = _filter_by_user(df, selected_user)
    if df_user.empty:
        return None

    text_df = _text_only(df_user)

    total_messages = int(df_user.shape[0])
    text_messages = int(text_df.shape[0])

    media_messages = int(
        df_user["message"].fillna("").astype(str).str.contains(
            r"<media omitted>", case=False, na=False, regex=True
        ).sum()
    )

    link_messages = 0
    for message in text_df["message"].fillna("").astype(str):
        if "http" in message.lower() or "www." in message.lower():
            link_messages += 1

    active_hours = (
        text_df["hour"].value_counts().head(3).to_dict()
        if "hour" in text_df.columns and not text_df.empty else {}
    )

    active_days = (
        text_df["day_name"].value_counts().head(3).to_dict()
        if "day_name" in text_df.columns and not text_df.empty else {}
    )

    sample_messages = _downsample_messages(
        text_df["message"].fillna("").astype(str).tolist(),
        max_messages=MAX_SAMPLE_MESSAGES,
        max_chars=MAX_SAMPLE_CHARS,
    )

    top_keywords = _top_keywords(text_df["message"].fillna("").astype(str).tolist(), top_n=12)

    return {
        "user": selected_user,
        "total_messages": total_messages,
        "text_messages": text_messages,
        "media_messages": media_messages,
        "link_messages": link_messages,
        "top_active_hours": active_hours,
        "top_active_days": active_days,
        "top_keywords": top_keywords,
        "sample_messages": sample_messages,
    }

def analyze_user_behavior(
    selected_user: str,
    df: pd.DataFrame,
    api_key: str | None,
    model_name: str = DEFAULT_GEMINI_MODEL,
) -> Tuple[Optional[GeminiInsight], str]:
    profile = build_user_profile(selected_user, df)
    if profile is None:
        return None, "No data available."

    payload = json.dumps(profile, ensure_ascii=False, sort_keys=True)
    cache_key = make_cache_key(f"{selected_user}:{model_name}", payload)

    cached = read_cache(cache_key)
    if cached is not None:
        try:
            return GeminiInsight.model_validate(cached), "Loaded from cache."
        except Exception:
            pass

    prompt = build_insight_prompt(profile)
    service = GeminiInsightService(api_key=api_key, model_name=model_name)
    result = service.analyze(prompt)
    write_cache(cache_key, result.model_dump())

    return result, "Fresh Gemini analysis generated."