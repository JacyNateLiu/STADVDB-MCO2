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
        # Construct query based on the platform filter
        query = "SELECT COUNT(*) FROM games_data WHERE "
        conditions = []
        if "Windows" in platform_filter:
            conditions.append("windows = 1")
        if "Mac" in platform_filter:
            conditions.append("mac = 1")
        if "Linux" in platform_filter:
            conditions.append("linux = 1")
        query += " OR ".join(conditions) if conditions else "1"  # Default query if no filter
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
        query += " OR ".join(conditions) if conditions else "1"  # Default query if no filter
        query += f" LIMIT {records_per_page} OFFSET {offset};"
        df = pd.read_sql(query, con=connection)
        return df
    except mysql.connector.Error as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Function to generate styled platform labels with a rectangular box and rounded borders
def platform_box(platform):
    platform_colors = {
        "Windows": "#1e90ff",  # Blue for Windows
        "Mac": "#eb6434",      # Light grey for Mac
        "Linux": "#32cd32"      # Green for Linux
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

# Streamlit app
st.title("Distributed Game Store Platform")

# Sidebar filters
st.sidebar.header("Filters")
platform_filter = st.sidebar.multiselect(
    "Platforms", options=["Windows", "Mac", "Linux"], default=["Windows", "Mac", "Linux"]
)

# Define records per page
records_per_page = 10

# Add sorting options in the sidebar
sort_by = st.sidebar.selectbox(
    "Sort by", options=["Price", "Release Date", "Name"], index=0
)
sort_order = st.sidebar.radio(
    "Sort order", options=["Ascending", "Descending"], index=0
)

# Create database connection
connection = create_connection()

if connection:
    # Get total records based on filters
    total_records = get_total_records(connection, platform_filter)
    
    if total_records > 0:
        # Calculate total pages
        total_pages = (total_records // records_per_page) + (1 if total_records % records_per_page > 0 else 0)
        
        # Allow user to select the page number
        current_page = st.number_input("Page number", min_value=1, max_value=total_pages, value=1)
        
        # Calculate offset based on the selected page number
        offset = (current_page - 1) * records_per_page
        
        # Fetch paginated data
        games_df = fetch_paginated_data(connection, platform_filter, offset, records_per_page)

        # Sort the data based on the selected sort criteria
        if sort_by == "Price":
            games_df = games_df.sort_values(by="price", ascending=(sort_order == "Ascending"))
        elif sort_by == "Release Date":
            games_df = games_df.sort_values(by="release_date", ascending=(sort_order == "Ascending"))
        elif sort_by == "Name":
            games_df = games_df.sort_values(by="name", ascending=(sort_order == "Ascending"))

        # Display the filtered and paginated data
        st.subheader(f"Page {current_page} of {total_pages}")
        if not games_df.empty:
            for _, game in games_df.iterrows():
                st.markdown(f"### {game['name']}")
                st.write(f"**Release Date:** {game['release_date']}")
                st.write(f"**Price:** ${game['price']}")
                st.write(f"**About the Game:** {game['about_the_game']}")
                
                # Display platforms in styled boxes
                platforms = []
                if game['windows']:
                    platforms.append("Windows")
                if game['mac']:
                    platforms.append("Mac")
                if game['linux']:
                    platforms.append("Linux")
                
                # Display platform boxes
                platform_html = "".join([platform_box(platform) for platform in platforms])
                st.markdown(platform_html, unsafe_allow_html=True)

                st.markdown("---")
    else:
        st.write("No games available for the selected filters.")
    
    # Close the connection
    connection.close()
else:
    st.warning("Failed to connect to the database.")