# app.py
import streamlit as st
from preprocessor import preprocess
import helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocess(data)

    # fetch unique users
    
    user_list = df['user'].unique().tolist()
    # user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='green')
        ax.set_xlabel("Timeline (Month-Year)")
        ax.set_ylabel("Monthly Message Volume")
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of Messages")
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most Active day")
            Active_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(Active_day.index,Active_day.values,color='purple')
            ax.set_xlabel("Day of Week")
            ax.set_ylabel("Number of Messages") 
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most Active month")
            Active_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(Active_month.index, Active_month.values,color='orange')
            ax.set_xlabel("Month")
            ax.set_ylabel("Number of Messages")  
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        if user_heatmap.empty or (user_heatmap.values == 0).all():
            st.warning("No activity data available for heatmap")
        else:
            fig, ax = plt.subplots()
            sns.heatmap(user_heatmap, ax=ax)
            st.pyplot(fig)

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Active Users')
            x,new_df = helper.most_active_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='red')
                ax.set_xlabel("Users")
                ax.set_ylabel("Number of Messages") 
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)

        if df_wc is None:
            st.warning("Not enough textual data to generate wordcloud")
        else:
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis("off")
            st.pyplot(fig)

        # most common words
        most_common_df = helper.most_common_words(selected_user,df)
        st.title('Most common words')

        if most_common_df is None:
            st.warning("Not enough meaningful words for analysis")
        else:
            fig, ax = plt.subplots()
            ax.barh(most_common_df['word'], most_common_df['count'])
            st.pyplot(fig)

        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")
        
        col1, col2 = st.columns(2)
        
        if emoji_df is None:
            st.warning("No emojis found for this user")
        else:
            with col1:
                st.dataframe(emoji_df)
        
            with col2:
                fig, ax = plt.subplots()
                ax.pie(
                    emoji_df['count'].head(),
                    labels=emoji_df['emoji'].head(),
                    autopct="%0.2f"
                )
                st.pyplot(fig)