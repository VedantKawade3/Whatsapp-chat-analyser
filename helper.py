from __future__ import annotations

import re
from collections import Counter
from typing import Optional

import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
import emoji

from config import load_stop_words

extract = URLExtract()
STOP_WORDS = load_stop_words()

NOISE_PATTERN = r"(?:<media omitted>|this message was deleted|deleted this message|message deleted|you deleted this message)"

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

def fetch_stats(selected_user, df):
    df = _filter_by_user(df, selected_user)

    num_messages = int(df.shape[0])

    text_df = _text_only(df)

    words = []
    for message in text_df["message"].fillna("").astype(str):
        words.extend(message.split())

    media_mask = df["message"].fillna("").astype(str).str.contains(
        r"<media omitted>", case=False, na=False, regex=True
    )
    num_media_messages = int(media_mask.sum())

    links = []
    for message in text_df["message"].fillna("").astype(str):
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def most_active_users(df):
    if df is None or df.empty:
        return pd.Series(dtype=int), pd.DataFrame(columns=["name", "percent"])

    df = df[df["user"] != "group_notification"].copy()

    if df.empty:
        return pd.Series(dtype=int), pd.DataFrame(columns=["name", "percent"])

    x = df["user"].value_counts().head(10)
    percent_df = ((df["user"].value_counts() / df.shape[0]) * 100).round(2).reset_index()
    percent_df.columns = ["name", "percent"]
    return x, percent_df

def create_wordcloud(selected_user, df):
    df = _filter_by_user(df, selected_user)
    text_df = _text_only(df)

    if text_df.empty:
        return None

    def remove_stop_words(message: str) -> str:
        return " ".join(
            word for word in message.lower().split()
            if word not in STOP_WORDS
        )

    temp = text_df.copy()
    temp["message"] = temp["message"].fillna("").astype(str).apply(remove_stop_words)

    text = temp["message"].str.cat(sep=" ").strip()
    if not text:
        return None

    try:
        wc = WordCloud(
            width=500,
            height=500,
            min_font_size=10,
            background_color="white"
        )
        return wc.generate(text)
    except ValueError:
        return None

def most_common_words(selected_user, df):
    df = _filter_by_user(df, selected_user)
    text_df = _text_only(df)

    if text_df.empty:
        return None

    words = []

    for message in text_df["message"].fillna("").astype(str):
        for word in message.lower().split():
            word = word.strip()
            if word and word not in STOP_WORDS:
                words.append(word)

    if not words:
        return None

    out = pd.DataFrame(Counter(words).most_common(20), columns=["word", "count"])
    out = out.sort_values(by="count", ascending=True).reset_index(drop=True)
    return out

def emoji_helper(selected_user, df):
    df = _filter_by_user(df, selected_user)
    text_df = _text_only(df)

    if text_df.empty:
        return None

    emojis = []

    try:
        emoji_set = set(emoji.EMOJI_DATA.keys())
    except Exception:
        try:
            emoji_set = set(emoji.UNICODE_EMOJI["en"])
        except Exception:
            emoji_set = set()

    for message in text_df["message"].fillna("").astype(str):
        emojis.extend([c for c in message if c in emoji_set])

    if not emojis:
        return None

    out = pd.DataFrame(Counter(emojis).most_common(), columns=["emoji", "count"])
    return out

def monthly_timeline(selected_user, df):
    df = _filter_by_user(df, selected_user)

    if df.empty:
        return pd.DataFrame(columns=["year", "month_num", "month", "message", "time"])

    timeline = df.groupby(["year", "month_num", "month"]).count()["message"].reset_index()
    timeline["time"] = timeline["month"] + "-" + timeline["year"].astype(str)
    return timeline

def daily_timeline(selected_user, df):
    df = _filter_by_user(df, selected_user)

    if df.empty:
        return pd.DataFrame(columns=["only_date", "message"])

    daily = df.groupby("only_date").count()["message"].reset_index()
    return daily

def week_activity_map(selected_user, df):
    df = _filter_by_user(df, selected_user)

    if df.empty:
        return pd.Series(dtype=int)

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    out = df["day_name"].value_counts().reindex(order, fill_value=0)
    return out

def month_activity_map(selected_user, df):
    df = _filter_by_user(df, selected_user)

    if df.empty:
        return pd.Series(dtype=int)

    order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    out = df["month"].value_counts().reindex(order, fill_value=0)
    return out

def activity_heatmap(selected_user, df):
    df = _filter_by_user(df, selected_user)

    if df.empty:
        return pd.DataFrame()

    heatmap = df.pivot_table(
        index="day_name",
        columns="period",
        values="message",
        aggfunc="count"
    ).fillna(0)

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap = heatmap.reindex(order)

    return heatmap