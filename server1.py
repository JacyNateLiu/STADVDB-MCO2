import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="ccscloud.dlsu.edu.ph",
            port=21302,
            user="your_username",
            password="your_password",
            database="games"
        )
        return connection
    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

def get_total_records(connection):
    try:
        # Modified query to include specific conditions
        query = "SELECT COUNT(*) FROM games_data WHERE windows = 1 AND linux = 0 AND mac = 0;"
        cursor = connection.cursor()
        cursor.execute(query)
        total_records = cursor.fetchone()[0]
        return total_records
    except mysql.connector.Error as e:
        st.error(f"Error calculating total records: {e}")
        return 0

def fetch_paginated_data(connection, offset, records_per_page, sort_by, sort_order):
    try:
        # Build the base query with specific filters
        query = "SELECT * FROM games_data WHERE windows = 1 AND linux = 0 AND mac = 0"

        # Add sorting logic
        sort_column_mapping = {
            "App ID": "app_id",
            "Name": "name",
            "Release Date": "release_date",
            "Price": "price"
        }
        sort_column = sort_column_mapping.get(sort_by, "app_id")  # Default to "app_id" if no match
        order = "ASC" if sort_order == "Ascending" else "DESC"
        query += f" ORDER BY {sort_column} {order}"

        # Add pagination logic
        query += f" LIMIT {records_per_page} OFFSET {offset};"

        # Execute the query and fetch data
        df = pd.read_sql(query, con=connection)
        return df
    except mysql.connector.Error as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def platform_box(platform):
    platform_colors = {
        "Windows": "#1e90ff",# Blue for Windows
        "Mac": "#eb6434",    # Red-Orange for Mac
        "Linux": "#32cd32"   # Green for Linux
    }
    color = platform_colors.get(platform, "#ffffff")
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

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Read View"

st.sidebar.header("Navigation")
if st.sidebar.button("Switch View"):

    st.session_state.view_mode = (
        "Write View" if st.session_state.view_mode == "Read View" else "Read View"
    )
st.sidebar.write(f"Current View: **{st.session_state.view_mode}**")

if st.session_state.view_mode == "Read View":
    st.title("Read View: STEAM Games")

    st.sidebar.header("Filters")
    platform_filter = st.sidebar.multiselect(
        "Platforms", options=["Windows", "Mac", "Linux"], default=["Windows", "Mac", "Linux"]
    )

    records_per_page = 10

    sort_by = st.sidebar.selectbox("Sort by", options=["App ID", "Name", "Release Date", "Price"], index=0)
    sort_order = st.sidebar.radio("Sort order", options=["Ascending", "Descending"], index=0)

    connection = create_connection()

    if connection:
        total_records = get_total_records(connection)
        if total_records > 0:
            total_pages = (total_records // records_per_page) + (1 if total_records % records_per_page > 0 else 0)
            current_page = st.number_input("Page number", min_value=1, max_value=total_pages, value=1)
            offset = (current_page - 1) * records_per_page
            games_df = fetch_paginated_data(connection, offset, records_per_page, sort_by, sort_order)
                
            st.subheader(f"Page {current_page} of {total_pages}")
            if not games_df.empty:
                for _, game in games_df.iterrows():
                    # Display game name and app_id
                    st.markdown(f"### {game['name']} (ID: {game['app_id']})")
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
    tabs = st.tabs(["Add Game", "Update Game Details", "Delete Game"])

    connection = create_connection()
    
    if connection:
        cursor = connection.cursor()

        with tabs[0]:
            st.header("Add New Game")
            try:
                # Fetch the next available app_id
                cursor.execute("SELECT MAX(app_id) FROM games_data;")
                max_app_id = cursor.fetchone()[0]
                new_app_id = (max_app_id + 1) if max_app_id else 1

                st.write(f"Assigned Game ID: {new_app_id}")

                new_name = st.text_input("Game Name")
                new_price = st.number_input("Price", min_value=0.0, step=0.01)
                new_release_date = st.date_input("Release Date")
                new_about = st.text_area("About the Game")
                new_platforms = st.multiselect(
                    "Platforms",
                    options=["Windows", "Mac", "Linux"],
                    key="add_game_platforms" 
                )

                if st.button("Add Game"):
                    # Validation: Ensure that required fields are not empty
                    if not new_name or not new_price or not new_release_date or not new_about:
                        st.error("Please fill in all the fields: Name, Price, Release Date, and About the Game.")
                    elif not new_platforms:  # Validation: Ensure that at least one platform is selected
                        st.error("Please select at least one platform (Windows, Mac, or Linux).")
                    else:
                        insert_query = """
                        INSERT INTO games_data (app_id, name, price, release_date, about_the_game, windows, mac, linux)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        """
                        values = (
                            new_app_id,
                            new_name,
                            new_price,
                            new_release_date,
                            new_about,
                            1 if "Windows" in new_platforms else 0,
                            1 if "Mac" in new_platforms else 0,
                            1 if "Linux" in new_platforms else 0,
                        )
                        cursor.execute(insert_query, values)
                        connection.commit()
                        st.success(f"Game '{new_name}' added successfully with ID {new_app_id}.")

            except mysql.connector.Error as e:
                connection.rollback()
                st.error(f"Error adding game: {e}")

        with tabs[1]:
            st.header("Update Game Details")
            try:
                app_id = st.number_input("Enter Game ID to update", min_value=1, step=1)

                if "game_details" not in st.session_state:
                    st.session_state["game_details"] = None

                if st.button("Fetch Game Details"):
                    fetch_query = """
                    SELECT name, price, release_date, about_the_game, windows, mac, linux 
                    FROM games_data 
                    WHERE app_id = %s
                    """
                    cursor.execute(fetch_query, (app_id,))
                    game = cursor.fetchone()

                    if game:
                        st.session_state["game_details"] = {
                            "name": game[0],
                            "price": game[1],
                            "release_date": game[2],
                            "about": game[3],
                            "windows": game[4],
                            "mac": game[5],
                            "linux": game[6],
                        }
                        st.success("Game details fetched successfully.")
                    else:
                        st.session_state["game_details"] = None
                        st.error(f"No game found with ID {app_id}")

                if st.session_state["game_details"]:
                    current_name = st.session_state["game_details"]["name"]
                    current_price = st.session_state["game_details"]["price"]
                    current_release_date = st.session_state["game_details"]["release_date"]
                    current_about = st.session_state["game_details"]["about"]
                    current_windows = st.session_state["game_details"]["windows"]
                    current_mac = st.session_state["game_details"]["mac"]
                    current_linux = st.session_state["game_details"]["linux"]
                else:
                    current_name = ""
                    current_price = 0.0
                    current_release_date = None
                    current_about = ""
                    current_windows = 0
                    current_mac = 0
                    current_linux = 0

                new_name = st.text_input("New Name", value=current_name)
                new_price = st.number_input("New Price", min_value=0.0, step=0.01, value=float(current_price))
                new_release_date = st.date_input("New Release Date", value=current_release_date)
                new_about = st.text_area("New About the Game", value=current_about)
                new_platforms = st.multiselect(
                    "Platforms",
                    options=["Windows", "Mac", "Linux"],
                    default=[
                        platform
                        for platform, flag in zip(
                            ["Windows", "Mac", "Linux"],
                            [current_windows, current_mac, current_linux]
                        )
                        if flag
                    ],
                    key="update_game_platforms"
                )

                if st.button("Update Game"):
                    # Validation: Ensure that required fields are not empty
                    if not new_name or not new_price or not new_release_date or not new_about:
                        st.error("Please fill in all the fields: Name, Price, Release Date, and About the Game.")
                    elif not new_platforms:  # Validation: Ensure that at least one platform is selected
                        st.error("Please select at least one platform (Windows, Mac, or Linux).")
                    else:
                        update_query = """
                        UPDATE games_data
                        SET name = %s, price = %s, release_date = %s, about_the_game = %s, windows = %s, mac = %s, linux = %s
                        WHERE app_id = %s;
                        """
                        values = (
                            new_name,
                            new_price,
                            new_release_date,
                            new_about,
                            1 if "Windows" in new_platforms else 0,
                            1 if "Mac" in new_platforms else 0,
                            1 if "Linux" in new_platforms else 0,
                            app_id,
                        )
                        cursor.execute(update_query, values)
                        connection.commit()
                        st.success(f"Game ID {app_id} updated successfully.")

            except mysql.connector.Error as e:
                connection.rollback()
                st.error(f"Error: {e}")

        with tabs[2]:
            st.header("Delete Game")
            try:
                app_id_to_delete = st.number_input("Enter Game ID to delete", min_value=1, step=1)

                if st.button("Delete Game"):
                    # Check if the game exists before trying to delete
                    check_query = "SELECT 1 FROM games_data WHERE app_id = %s;"
                    cursor.execute(check_query, (app_id_to_delete,))
                    game_exists = cursor.fetchone()

                    if not game_exists:
                        st.error(f"No game found with ID {app_id_to_delete}.")
                    else:
                        # Proceed with deletion if the game exists
                        delete_query = "DELETE FROM games_data WHERE app_id = %s;"
                        cursor.execute(delete_query, (app_id_to_delete,))
                        connection.commit()
                        st.success(f"Game ID {app_id_to_delete} deleted successfully.")
            except mysql.connector.Error as e:
                connection.rollback()
                st.error(f"Error deleting game: {e}")

        connection.close()
    else:
        st.warning("Failed to connect to the database.")