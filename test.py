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

# Function to fetch total records count
def get_total_records(connection, platform_filter):
    try:
        query = "SELECT COUNT(*) FROM games_data WHERE "
        conditions = []
        if "Windows" in platform_filter:
            conditions.append("windows = 1")
        if "Mac" in platform_filter:
            conditions.append("mac = 1")
        if "Linux" in platform_filter:
            conditions.append("linux = 1")
        query += " OR ".join(conditions) if conditions else "1"
        cursor = connection.cursor()
        cursor.execute(query)
        total_records = cursor.fetchone()[0]
        return total_records
    except mysql.connector.Error as e:
        st.error(f"Error calculating total records: {e}")
        return 0

# Function to fetch paginated game data
def fetch_paginated_data(connection, platform_filter, offset, records_per_page):
    try:
        query = "SELECT * FROM games_data WHERE "
        conditions = []
        if "Windows" in platform_filter:
            conditions.append("windows = 1")
        if "Mac" in platform_filter:
            conditions.append("mac = 1")
        if "Linux" in platform_filter:
            conditions.append("linux = 1")
        query += " OR ".join(conditions) if conditions else "1"
        query += f" LIMIT {records_per_page} OFFSET {offset};"
        df = pd.read_sql(query, con=connection)
        return df
    except mysql.connector.Error as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Function to generate styled platform labels
def platform_box(platform):
    platform_colors = {
        "Windows": "#1e90ff",  # Blue for Windows
        "Mac": "#eb6434",      # Red-Orange for Mac
        "Linux": "#32cd32"     # Green for Linux
    }
    color = platform_colors.get(platform, "#ffffff")  # Default to white if no color defined
    html = f"""
    <div style="
        display: inline-block;
        background-color: {color};
        padding: 10px 20px;
        margin-right: 5px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: bold;
        color: white;
        text-align: center;
    ">
        {platform}
    </div>
    """
    return html

# Initialize session state
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Read View"

# Sidebar for navigation
st.sidebar.header("Navigation")
if st.sidebar.button("Switch View"):
    # Toggle between views
    st.session_state.view_mode = (
        "Write View" if st.session_state.view_mode == "Read View" else "Read View"
    )
st.sidebar.write(f"Current View: **{st.session_state.view_mode}**")

# Load the selected view
if st.session_state.view_mode == "Read View":
    st.title("Read View: STEAM Games")

    # Sidebar filters
    st.sidebar.header("Filters")
    platform_filter = st.sidebar.multiselect(
        "Platforms", options=["Windows", "Mac", "Linux"], default=["Windows", "Mac", "Linux"]
    )

    # Define records per page
    records_per_page = 10

    # Add sorting options in the sidebar
    sort_by = st.sidebar.selectbox("Sort by", options=["Price", "Release Date", "Name"], index=0)
    sort_order = st.sidebar.radio("Sort order", options=["Ascending", "Descending"], index=0)

    # Create database connection
    connection = create_connection()

    if connection:
        total_records = get_total_records(connection, platform_filter)
        if total_records > 0:
            total_pages = (total_records // records_per_page) + (1 if total_records % records_per_page > 0 else 0)
            current_page = st.number_input("Page number", min_value=1, max_value=total_pages, value=1)
            offset = (current_page - 1) * records_per_page
            games_df = fetch_paginated_data(connection, platform_filter, offset, records_per_page)

            # Sort data
            if sort_by == "Price":
                games_df = games_df.sort_values(by="price", ascending=(sort_order == "Ascending"))
            elif sort_by == "Release Date":
                games_df = games_df.sort_values(by="release_date", ascending=(sort_order == "Ascending"))
            elif sort_by == "Name":
                games_df = games_df.sort_values(by="name", ascending=(sort_order == "Ascending"))

            st.subheader(f"Page {current_page} of {total_pages}")
            if not games_df.empty:
                for _, game in games_df.iterrows():
                    st.markdown(f"### {game['name']}")
                    st.write(f"**Release Date:** {game['release_date']}")
                    st.write(f"**Price:** ${game['price']}")
                    st.write(f"**About the Game:** {game['about_the_game']}")
                    platforms = []
                    if game['windows']:
                        platforms.append("Windows")
                    if game['mac']:
                        platforms.append("Mac")
                    if game['linux']:
                        platforms.append("Linux")
                    platform_html = "".join([platform_box(platform) for platform in platforms])
                    st.markdown(platform_html, unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.write("No games available for the selected filters.")
        else:
            st.write("No games found.")
        connection.close()
    else:
        st.warning("Failed to connect to the database.")

else:
    st.title("Write View: STEAM Games")
    tabs = st.tabs(["View Games", "Update Game Details", "Delete Game"])

    # View Games Tab
    with tabs[0]:
        st.header("View Games")
        st.write("Add your logic for viewing games here.")

    # Update Game Details Tab
    with tabs[1]:
        st.header("Update Game Details")
        st.write("Add your logic for updating game details here.")

    # Delete Game Tab
    with tabs[2]:
        st.header("Delete Game")
        st.write("Add your logic for deleting games here.")