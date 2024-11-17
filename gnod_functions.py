import time
import pandas as pd
from spotipy.exceptions import SpotifyException

def get_audio_features_batch(sp, track_ids, track_names, artist_names, artist_ids, wait_time=2, filename="track_features.csv"):
    all_features = []
    for i in range(0, len(track_ids), 100):
        batch_track_ids = track_ids[i:i + 100]
        batch_track_names = track_names[i:i + 100]
        batch_artist_names = artist_names[i:i + 100]
        batch_artist_ids = artist_ids[i:i + 100]
        
        try:
            features = sp.audio_features(batch_track_ids)
            all_features.extend(features)
            
            # Prepare the data to save after each batch
            data_to_save = []
            for j in range(len(features)):
                if features[j] is not None:  # Only include valid features
                    data = {
                        "track_name": batch_track_names[j],
                        "artist_name": batch_artist_names[j],
                        "artist_id": batch_artist_ids[j],
                        **features[j]  # Add all audio features
                    }
                    data_to_save.append(data)
            
            # Save batch to CSV
            save_to_csv(data_to_save, filename)
            time.sleep(wait_time)  # Wait between each batch to avoid rate limit
            
        except SpotifyException as e:
            if e.http_status == 429:  # Rate limit exceeded
                retry_after = int(e.headers.get("Retry-After", 10))  # Default wait time of 10 seconds
                print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
                return get_audio_features_batch(sp, track_ids[i:], track_names[i:], artist_names[i:], artist_ids[i:], wait_time, filename)  # Retry the current batch
            else:
                raise e
    return all_features

def get_playlist_tracks(sp, playlist_id, wait_time=2):
    track_uris = []
    artist_ids = []
    track_names = []
    artist_names = []
    
    # Pagination for large playlists
    offset = 0
    while True:
        try:
            response = sp.playlist_items(playlist_id, offset=offset, limit=100)
            items = response['items']
            if not items:
                break  # Exit loop if no more items
            
            for item in items:
                track = item["track"]
                track_uris.append(track["uri"])
                track_names.append(track["name"])
                
                # Primary artist data
                artist = track["artists"][0]
                artist_ids.append(artist["id"])
                artist_names.append(artist["name"])
                
            offset += 100  # Increment offset to get the next batch of 100 items
            time.sleep(wait_time)
            
        except SpotifyException as e:
            if e.http_status == 429:  # Rate limit exceeded
                retry_after = int(e.headers.get("Retry-After", 10))
                print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                raise e
    
    return track_uris, track_names, artist_ids, artist_names

def save_to_csv(data_batch, filename):
    # Convert the batch of data to a DataFrame
    df = pd.DataFrame(data_batch)
    
    # Append to CSV without writing the header if the file already exists
    df.to_csv(filename, mode='a', index=False, header=not pd.io.common.file_exists(filename))

def get_features_from_playlist(sp, playlist_id, filename="track_features.csv"):
    # Fetch all track URIs, names, artist IDs, and artist names from the playlist in batches
    track_uris, track_names, artist_ids, artist_names = get_playlist_tracks(sp, playlist_id, wait_time=2)
    
    # Fetch audio features in batches with rate-limit handling and save each batch
    get_audio_features_batch(sp, track_uris, track_names, artist_names, artist_ids, wait_time=2, filename=filename)
    
    # Load the saved CSV to ensure all data is captured
    final_df = pd.read_csv(filename)
    return final_df


def find_related_artists_for_df(sp, artist_df):
    # Initialize a list to hold the data for the new DataFrame
    related_data = []

    # Loop over each artist ID in the input DataFrame
    for artist_id in artist_df["artist_id"]:
        try:
            # Fetch related artists for the current artist
            related_info = sp.artist_related_artists(artist_id)
            
            # Get the top 5 related artists
            for related_artist in related_info["artists"][:5]:
                related_data.append({
                    "original_artist_id": artist_id,
                    "related_artist_id": related_artist["id"],
                    "related_artist_name": related_artist["name"]
                })

        except Exception as e:
            print(f"An error occurred for artist {artist_id}: {e}")
            continue

    # Convert the list to a DataFrame
    related_artists_df = pd.DataFrame(related_data)
    return related_artists_df


def get_top_tracks_for_artists_in_batches(sp, artist_df, batch_size=100, wait_time=1):
    # Initialize a list to store top tracks data
    top_tracks_data = []
    
    # Process artists in batches of `batch_size`
    for i in range(0, len(artist_df), batch_size):
        batch = artist_df.iloc[i:i + batch_size]
        
        for _, row in batch.iterrows():
            artist_id = row["artist_id"]
            artist_name = row["artist_name"]

            try:
                # Fetch the artist's top tracks
                results = sp.artist_top_tracks(artist_id)

                # Extract the top 5 tracks with their popularity scores and URIs
                for j, track in enumerate(results["tracks"][:5]):
                    top_tracks_data.append({
                        "artist_id": artist_id,
                        "artist_name": artist_name,
                        "track_name": track["name"],
                        "track_popularity": track["popularity"],
                        "track_uri": track["uri"],
                        "track_number": j + 1
                    })

            except SpotifyException as e:
                if e.http_status == 429:  # Rate limit exceeded
                    retry_after = int(e.headers.get("Retry-After", wait_time))
                    print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                else:
                    print(f"An error occurred for artist {artist_name} (ID: {artist_id}): {e}")
                    continue

            time.sleep(wait_time)  # Wait between requests within the batch

        # Wait before moving on to the next batch
        time.sleep(wait_time)

    # Convert the collected data into a DataFrame
    top_tracks_df = pd.DataFrame(top_tracks_data)
    return top_tracks_df


def get_audio_features_for_tracks(sp, tracks_df, batch_size=100, wait_time=1, filename="enhanced_tracks.csv"):
    # Initialize a list to store audio features data
    audio_features_data = []

    # Process tracks in batches of `batch_size`
    for i in range(0, len(tracks_df), batch_size):
        # Get a batch of track URIs
        batch_uris = tracks_df["track_uri"].iloc[i:i + batch_size].tolist()
        
        try:
            # Fetch audio features for the current batch
            features = sp.audio_features(batch_uris)
            
            # Append each track's audio features to the list
            for feature in features:
                if feature is not None:  # Ensure valid data
                    audio_features_data.append(feature)

            # Convert current batch of audio features to a DataFrame
            batch_features_df = pd.DataFrame(audio_features_data)

            # Merge the batch of audio features with the corresponding tracks in `tracks_df`
            batch_tracks_df = tracks_df.iloc[i:i + batch_size].merge(
                batch_features_df, left_on="track_uri", right_on="uri", how="left"
            )

            # Append to CSV incrementally
            mode = 'a' if i > 0 else 'w'  # Append ('a') if not the first batch, otherwise write ('w')
            header = (i == 0)  # Write header only for the first batch
            batch_tracks_df.to_csv(filename, mode=mode, header=header, index=False)

            # Clear audio_features_data to avoid duplicating data
            audio_features_data.clear()

            # Wait to avoid exceeding the rate limit
            time.sleep(wait_time)

        except SpotifyException as e:
            if e.http_status == 429:  # Rate limit exceeded
                retry_after = int(e.headers.get("Retry-After", wait_time))
                print(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            else:
                print(f"An error occurred: {e}")
                continue

    # Reload the full CSV to return a complete DataFrame
    enhanced_tracks_df = pd.read_csv(filename)
    return enhanced_tracks_df