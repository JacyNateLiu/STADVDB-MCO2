import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error  # Corrected import

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

@st.cache_data
def fetch_games_from_db():
    connection = create_connection()
    if connection:
        query = "SELECT * FROM games_data;"  # Update "games" to your actual table name
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if connection fails

def update_game_price(app_id, new_price):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "UPDATE games SET price = %s WHERE app_id = %s;"  # Update table name and column if different
            cursor.execute(query, (new_price, app_id))
            connection.commit()
            st.sidebar.success("Price updated successfully!")
        except Error as e:
            st.sidebar.error(f"Failed to update price: {e}")
        finally:
            cursor.close()
            connection.close()

st.title("Distributed Game Store Platform (SQL Connected)")

if st.button("Refresh Game Data"):
    st.experimental_rerun()

st.header("Games List")
games_df = fetch_games_from_db()
if not games_df.empty:
    st.write(games_df)
else:
    st.error("Failed to load game data from the database.")

st.sidebar.header("Admin Section")
if not games_df.empty:
    app_id = st.sidebar.selectbox("Select Game ID to Update", options=games_df["app_id"])
    new_price = st.sidebar.number_input("New Price", min_value=0.0, value=29.99, step=0.01)
    if st.sidebar.button("Update Price"):
        update_game_price(app_id, new_price)