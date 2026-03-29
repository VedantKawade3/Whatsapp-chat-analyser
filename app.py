import streamlit as st
from preprocessor import preprocess
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Whatsapp Chat Analyzer", layout="wide")

st.sidebar.title("Whatsapp Chat Analyzer")
st.sidebar.caption("Upload an exported WhatsApp .txt file")

uploaded_file = st.sidebar.file_uploader("Choose a file", type=["txt"])

if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8", errors="ignore")
        df = preprocess(data)

        if df.empty:
            st.error("No messages could be parsed from this file.")
            st.stop()

        user_list = [u for u in df["user"].dropna().unique().tolist() if u != "group_notification"]
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("Show analysis wrt", user_list, index=0)

        if st.sidebar.button("Show Analysis"):
            st.title("Top Statistics")

            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

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
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            if not timeline.empty:
                ax.plot(timeline["time"], timeline["message"], color="green")
            ax.set_xlabel("Timeline (Month-Year)")
            ax.set_ylabel("Monthly Message Volume")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

            st.subheader("Daily Timeline")
            daily = helper.daily_timeline(selected_user, df)
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
                active_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                if not active_day.empty:
                    ax.bar(active_day.index, active_day.values, color="purple")
                ax.set_xlabel("Day of Week")
                ax.set_ylabel("Number of Messages")
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

            with col2:
                st.write("Most Active Month")
                active_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                if not active_month.empty:
                    ax.bar(active_month.index, active_month.values, color="orange")
                ax.set_xlabel("Month")
                ax.set_ylabel("Number of Messages")
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

            st.subheader("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            if user_heatmap.empty or user_heatmap.fillna(0).values.sum() == 0:
                st.warning("No activity data available for heatmap")
            else:
                fig, ax = plt.subplots()
                sns.heatmap(user_heatmap, ax=ax)
                st.pyplot(fig)

            if selected_user == "Overall":
                st.subheader("Most Active Users")
                x, new_df = helper.most_active_users(df)

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
            df_wc = helper.create_wordcloud(selected_user, df)

            if df_wc is None:
                st.warning("Not enough textual data to generate wordcloud")
            else:
                fig, ax = plt.subplots()
                ax.imshow(df_wc)
                ax.axis("off")
                st.pyplot(fig)

            st.subheader("Most Common Words")
            most_common_df = helper.most_common_words(selected_user, df)

            if most_common_df is None or most_common_df.empty:
                st.warning("Not enough meaningful words for analysis")
            else:
                fig, ax = plt.subplots()
                ax.barh(most_common_df["word"], most_common_df["count"])
                st.pyplot(fig)

            st.subheader("Emoji Analysis")
            emoji_df = helper.emoji_helper(selected_user, df)

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

    except Exception as e:
        st.error(f"Something went wrong: {e}")