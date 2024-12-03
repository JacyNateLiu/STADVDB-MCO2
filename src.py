import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Function to create a database connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="ccscloud.dlsu.edu.ph",
            port=21292,
            user="your_username",
            password="your_password",
            database="games"
        )
        return connection
    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# Function to fetch games data using a manual connection
@st.cache_data
def fetch_games_data():
    connection = create_connection()
    if connection:
        try:
            query = "SELECT * FROM games_data;"  # Adjust if needed
            df = pd.read_sql(query, con=connection)
            return df
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error
        finally:
            connection.close()
    else:
        return pd.DataFrame()

# Streamlit app
st.title("Distributed Game Store Platform")

# Fetch data dynamically
games_df = fetch_games_data()

if games_df.empty:
    st.warning("No data available to display. Please check the database connection.")
else:
    # Sidebar filters
    st.sidebar.header("Filters")
    platform_filter = st.sidebar.multiselect(
        "Platforms", options=["Windows", "Mac", "Linux"], default=["Windows", "Mac", "Linux"]
    )

    # Apply platform filters
    def filter_by_platform(df, platforms):
        conditions = []
        if "Windows" in platforms:
            conditions.append(df["windows"])
        if "Mac" in platforms:
            conditions.append(df["mac"])
        if "Linux" in platforms:
            conditions.append(df["linux"])
        return df[pd.concat(conditions, axis=1).any(axis=1)] if conditions else df

    filtered_data = filter_by_platform(games_df, platform_filter)

    st.subheader("Available Games")
    for _, game in filtered_data.iterrows():
        st.markdown(f"### {game['name']}")
        st.write(f"**Release Date:** {game['release_date']}")
        st.write(f"**Price:** ${game['price']}")
        st.write(f"**About the Game:** {game['about_the_game']}")
        st.write(
            f"**Platforms:** "
            f"{'Windows ' if game['windows'] else ''}"
            f"{'Mac ' if game['mac'] else ''}"
            f"{'Linux' if game['linux'] else ''}"
        )
        st.markdown("---")