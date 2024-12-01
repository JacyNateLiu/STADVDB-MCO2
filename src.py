import streamlit as st
import pandas as pd

# Hardcoded data for demonstration
games_data = [
    {
        "app_id": 1,
        "name": "Game One",
        "release_date": "2023-01-15",
        "price": 29.99,
        "about_the_game": "An exciting first-person adventure game.",
        "windows": True,
        "mac": True,
        "linux": False,
    },
    {
        "app_id": 2,
        "name": "Game Two",
        "release_date": "2022-10-05",
        "price": 19.99,
        "about_the_game": "A classic strategy game for thinkers.",
        "windows": True,
        "mac": False,
        "linux": True,
    },
    {
        "app_id": 3,
        "name": "Game Three",
        "release_date": "2021-05-21",
        "price": 9.99,
        "about_the_game": "A fun and challenging puzzle game.",
        "windows": False,
        "mac": True,
        "linux": True,
    },
]

# Convert hardcoded data to a DataFrame
df = pd.DataFrame(games_data)

# Streamlit app
st.title("Distributed Game Store Platform")

st.sidebar.header("Filters")
platform_filter = st.sidebar.multiselect(
    "Platforms", options=["Windows", "Mac", "Linux"], default=["Windows", "Mac", "Linux"]
)

# Filter data based on platform selection
filtered_data = df[
    (df["windows"] if "Windows" in platform_filter else False)
    | (df["mac"] if "Mac" in platform_filter else False)
    | (df["linux"] if "Linux" in platform_filter else False)
]

st.subheader("Available Games")
for _, game in filtered_data.iterrows():
    st.markdown(f"### {game['name']}")
    st.write(f"**Release Date:** {game['release_date']}")
    st.write(f"**Price:** ${game['price']}")
    st.write(f"**About the Game:** {game['about_the_game']}")
    st.write(f"**Platforms:** {'Windows ' if game['windows'] else ''}{'Mac ' if game['mac'] else ''}{'Linux' if game['linux'] else ''}")
    st.markdown("---")
