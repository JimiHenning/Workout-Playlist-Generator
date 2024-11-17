import streamlit as st
import pandas as pd


df = pd.read_csv("enhanced_tracks_cluster10_further_reduced.csv") 


def get_playlist(song_name, duration, data, popularity_preference="Doesn't Matter"):
    # Locate song in the DataFrame
    song_row = data[data['track_name'].str.contains(song_name, case=False, na=False)]
    if song_row.empty:
        return None, "Song not found in database."

    # Get cluster of the input song
    cluster_number = song_row.iloc[0]['Cluster']
    artist_name = song_row.iloc[0]['artist_name']  # Extract the artist name

    # Filter songs in the same cluster, excluding the entered song
    similar_songs = data[(data['Cluster'] == cluster_number) &
                         (~data['track_name'].str.contains(song_name, case=False, na=False))]

    # Sort songs based on popularity preference
    if popularity_preference == "Popular":
        similar_songs = similar_songs.sort_values(by="track_popularity", ascending=False)  # Most popular first
    elif popularity_preference == "Underground":
        similar_songs = similar_songs.sort_values(by="track_popularity", ascending=True)   # Least popular first
    elif popularity_preference == "Doesn't Matter":
        # Prefer songs by the same artist
        similar_songs['same_artist'] = similar_songs['artist_name'] == artist_name
        similar_songs = similar_songs.sort_values(by=['same_artist'], ascending=False)
    
    # Calculate cumulative duration
    total_duration = 0
    playlist = []

    for _, row in similar_songs.iterrows():
        if total_duration + row['duration_ms'] <= duration * 60000: 
            playlist.append(f"{row['artist_name']} - {row['track_name']} (Popularity: {row['track_popularity']})")
            total_duration += row['duration_ms']
        if total_duration >= duration * 60000:
            break

    if not playlist:
        return None, "Not enough songs to fill the specified duration."

    return playlist, None



st.title("Workout Playlist Generator")

song_name = st.text_input("Enter a song you like:")
workout_duration = st.number_input("Enter workout duration in minutes:", min_value=1, max_value=300, step=5)

# Slider for Popularity Preference
popularity_preference = st.select_slider(
    "Select popularity preference for recommendations:",
    options=["Popular", "Doesn't Matter", "Underground"],
    value="Doesn't Matter"
)

# Generate playlist when user clicks the button 
if st.button("Generate Playlist"):
    if not song_name:
        st.warning("Please enter a song name.")
    elif workout_duration <= 0:
        st.warning("Please enter a positive workout duration.")
    else:
        
        playlist, error_message = get_playlist(song_name, workout_duration, df, popularity_preference)
        
        if error_message:
            st.error(error_message)
        else:
            st.success("Here's your recommended playlist:")
            for song in playlist:
                st.write(song)  # Displays "Artist Name - Song Name (Popularity: X)" for each song
