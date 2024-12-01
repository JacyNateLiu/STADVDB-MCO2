import streamlit as st
import pandas as pd
import time

# Simulating database updates (hardcoded)
def get_game_data():
    return [
        {"app_id": 1, "name": "Game One", "price": 29.99, "about_the_game": "Exciting game!"},
        {"app_id": 2, "name": "Game Two", "price": 19.99, "about_the_game": "Strategic fun!"},
    ]

@st.cache_data
def fetch_games():
    # Simulate database fetch
    time.sleep(1)  # Simulate latency
    return pd.DataFrame(get_game_data())

def admin_update_game_price(app_id, new_price):
    # Simulate a database update
    for game in get_game_data():
        if game["app_id"] == app_id:
            game["price"] = new_price

# Streamlit app
st.title("Distributed Game Store Platform")

# Show data to users
if st.button("Refresh Game Data"):
    st.experimental_rerun()

st.header("Games List")
df = fetch_games()
st.write(df)

# Admin Interface
st.sidebar.header("Admin Section")
app_id = st.sidebar.selectbox("Select Game ID to Update", options=df["app_id"])
new_price = st.sidebar.number_input("New Price", min_value=0.0, value=29.99, step=0.01)
if st.sidebar.button("Update Price"):
    admin_update_game_price(app_id, new_price)
    st.sidebar.write("Price updated successfully!")
