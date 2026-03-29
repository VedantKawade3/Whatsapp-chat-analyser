from __future__ import annotations

import os

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from config import DEFAULT_GEMINI_MODEL
from helper import (
    activity_heatmap,
    create_wordcloud,
    daily_timeline,
    emoji_helper,
    fetch_stats,
    month_activity_map,
    monthly_timeline,
    most_active_users,
    most_common_words,
    week_activity_map,
)
from insights import analyze_user_behavior
from preprocessor import preprocess


st.set_page_config(
    page_title="Whatsapp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Whatsapp Chat Analyzer")
st.sidebar.caption("Upload an exported WhatsApp .txt file")

uploaded_file = st.sidebar.file_uploader("Choose a file", type=["txt"])


def get_api_key() -> str | None:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY")


def render_normal_analysis(df, selected_user):
    num_messages, words, num_media_messages, num_links = fetch_stats(selected_user, df)

    st.title("Top Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Messages", num_messages)
    with col2:
        st.metric("Total Words", words)
    with col3:
        st.metric("Media Shared", num_media_messages)
    with col4:
        st.metric("Links Shared", num_links)

    st.divider()

    st.subheader("Monthly Timeline")
    timeline = monthly_timeline(selected_user, df)
    fig, ax = plt.subplots()
    if not timeline.empty:
        ax.plot(timeline["time"], timeline["message"], color="green")
    ax.set_xlabel("Timeline (Month-Year)")
    ax.set_ylabel("Monthly Message Volume")
    plt.xticks(rotation="vertical")
    st.pyplot(fig)

    st.subheader("Daily Timeline")
    daily = daily_timeline(selected_user, df)
    fig, ax = plt.subplots()
    if not daily.empty:
        ax.plot(daily["only_date"], daily["message"], color="black")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Messages")
    plt.xticks(rotation="vertical")
    st.pyplot(fig)

    st.subheader("Activity Map")
    col1, col2 = st.columns(2)

    with col1:
        st.write("Most Active Day")
        active_day = week_activity_map(selected_user, df)
        fig, ax = plt.subplots()
        if not active_day.empty:
            ax.bar(active_day.index, active_day.values, color="purple")
        ax.set_xlabel("Day of Week")
        ax.set_ylabel("Number of Messages")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

    with col2:
        st.write("Most Active Month")
        active_month = month_activity_map(selected_user, df)
        fig, ax = plt.subplots()
        if not active_month.empty:
            ax.bar(active_month.index, active_month.values, color="orange")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Messages")
        plt.xticks(rotation="vertical")
        st.pyplot(fig)

    st.subheader("Weekly Activity Map")
    user_heatmap = activity_heatmap(selected_user, df)
    if user_heatmap.empty or user_heatmap.fillna(0).values.sum() == 0:
        st.warning("No activity data available for heatmap")
    else:
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

    if selected_user == "Overall":
        st.subheader("Most Active Users")
        x, new_df = most_active_users(df)

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            if not x.empty:
                ax.bar(x.index, x.values, color="red")
            ax.set_xlabel("Users")
            ax.set_ylabel("Number of Messages")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        with col2:
            st.dataframe(new_df, use_container_width=True)

    st.subheader("Wordcloud")
    df_wc = create_wordcloud(selected_user, df)

    if df_wc is None:
        st.warning("Not enough textual data to generate wordcloud")
    else:
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

    st.subheader("Most Common Words")
    most_common_df = most_common_words(selected_user, df)

    if most_common_df is None or most_common_df.empty:
        st.warning("Not enough meaningful words for analysis")
    else:
        fig, ax = plt.subplots()
        ax.barh(most_common_df["word"], most_common_df["count"])
        ax.set_xlabel("Count")
        ax.set_ylabel("Word")
        st.pyplot(fig)

    st.subheader("Emoji Analysis")
    emoji_df = emoji_helper(selected_user, df)

    if emoji_df is None or emoji_df.empty:
        st.warning("No emojis found for this user")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df, use_container_width=True)

        with col2:
            fig, ax = plt.subplots()
            ax.pie(
                emoji_df["count"].head(),
                labels=emoji_df["emoji"].head(),
                autopct="%0.2f"
            )
            st.pyplot(fig)


def render_gemini_analysis(df, selected_user, model_name):
    st.divider()
    st.subheader("Gemini Communication Insights")
    st.caption("This analyzes communication style and behavior, not medical or psychological diagnoses.")

    if selected_user == "Overall":
        st.info("Select a specific user to generate an individual communication profile.")
        return

    api_key = get_api_key()
    if not api_key:
        st.error("GEMINI_API_KEY is missing.")
        return

    with st.spinner("Generating Gemini insights..."):
        try:
            insight, status = analyze_user_behavior(
                selected_user=selected_user,
                df=df,
                api_key=api_key,
                model_name=model_name.strip() or DEFAULT_GEMINI_MODEL,
            )

            if insight is None:
                st.warning("Not enough data for AI analysis.")
                return

            st.success(status)

            left, right = st.columns(2)

            with left:
                st.markdown("### Communication Style")
                st.write(insight.communication_style)

                st.markdown("### Tone")
                st.write(insight.tone)

                st.markdown("### Conversation Behavior")
                st.write(insight.conversation_behavior)

                st.markdown("### Social Style")
                st.write(insight.social_style)

            with right:
                st.markdown("### Dominant Topics")
                st.write(insight.dominant_topics)

                st.markdown("### Strengths")
                st.write(insight.strengths)

                st.markdown("### Watchouts")
                st.write(insight.watchouts)

                st.markdown("### Confidence")
                st.write(insight.confidence)

            st.markdown("### Summary")
            st.write(insight.summary)

            with st.expander("Raw JSON"):
                st.json(insight.model_dump())

        except Exception as e:
            st.error(f"Gemini analysis failed: {e}")


if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8", errors="ignore")
    df = preprocess(data)

    if df.empty:
        st.error("No usable messages were parsed from this file.")
        st.stop()

    user_list = [u for u in df["user"].dropna().unique().tolist() if u != "group_notification"]
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    model_name = st.sidebar.text_input("Gemini model", value=DEFAULT_GEMINI_MODEL)

    col1, col2 = st.sidebar.columns(2)

    with col1:
        normal_btn = st.button("📊 Show Analysis", use_container_width=True)

    with col2:
        gemini_btn = st.button("🧠 AI Analysis", use_container_width=True)

    if normal_btn:
        render_normal_analysis(df, selected_user)

    if gemini_btn:
        render_gemini_analysis(df, selected_user, model_name)