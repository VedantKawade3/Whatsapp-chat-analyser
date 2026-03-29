from __future__ import annotations

import re
from typing import List, Dict

import pandas as pd

MESSAGE_START_RE = re.compile(
    r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s'
    r'(?P<time>\d{1,2}:\d{2}(?:\s?[ap]m)?)\s-\s'
    r'(?P<body>.*)$',
    flags=re.IGNORECASE
)

def _normalize_text(text: str) -> str:
    if text is None:
        return ""
    return (
        text.replace("\u202f", " ")
            .replace("\u200e", "")
            .replace("\ufeff", "")
    )

def _get_period(hour: int) -> str:
    if pd.isna(hour):
        return ""
    hour = int(hour)
    if hour == 23:
        return "23-00"
    if hour == 0:
        return "00-01"
    return f"{hour:02d}-{hour + 1:02d}"

def preprocess(data: str) -> pd.DataFrame:
    data = _normalize_text(data)

    base_columns = [
        "date", "user", "message", "only_date", "year", "month_num",
        "month", "day", "day_name", "hour", "minute", "period"
    ]

    if not data.strip():
        return pd.DataFrame(columns=base_columns)

    lines = data.splitlines()
    records: List[Dict[str, str]] = []
    current = None

    for raw_line in lines:
        line = raw_line.strip("\r")
        match = MESSAGE_START_RE.match(line)

        if match:
            if current is not None:
                records.append(current)

            current = {
                "date_str": match.group("date").strip(),
                "time_str": match.group("time").strip(),
                "body": match.group("body").strip()
            }
        else:
            if current is not None:
                current["body"] += "\n" + line.strip()

    if current is not None:
        records.append(current)

    if not records:
        return pd.DataFrame(columns=base_columns)

    parsed_rows = []

    for rec in records:
        body = rec["body"].strip()

        if ": " in body:
            user, message = body.split(": ", 1)
            user = user.strip() or "group_notification"
            message = message.strip()
        else:
            user = "group_notification"
            message = body

        dt_text = f"{rec['date_str']} {rec['time_str']}"
        dt = pd.to_datetime(dt_text, dayfirst=True, errors="coerce")

        parsed_rows.append(
            {
                "date": dt,
                "user": user,
                "message": message,
            }
        )

    df = pd.DataFrame(parsed_rows)
    df = df.dropna(subset=["date"]).reset_index(drop=True)

    if df.empty:
        return pd.DataFrame(columns=base_columns)

    df["only_date"] = df["date"].dt.date
    df["year"] = df["date"].dt.year
    df["month_num"] = df["date"].dt.month
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["day_name"] = df["date"].dt.day_name()
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute
    df["period"] = df["hour"].apply(_get_period)

    return df