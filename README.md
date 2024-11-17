# Workout-Playlist-Generator

# Spotify Audio Feature Extractor and Playlist Generator

This project leverages Spotify's API to extract detailed audio features for a given list of tracks and generates personalized playlists. It is designed to process large datasets of songs and provide insights or playlist recommendations based on audio characteristics such as tempo, energy, and danceability.

## Features

- **Batch Audio Feature Extraction**: Efficiently extracts audio features for up to 100 tracks at a time using Spotify's API.
- **Data Storage**: Saves extracted audio features into structured CSV files for further analysis.
- **Error Handling and Retry**: Robust error handling for API rate limits or other exceptions, ensuring uninterrupted data processing.
- **Playlist Recommendations**: Provides tools for clustering and filtering tracks based on user-defined preferences.

## File Overview

### 1. `gnod_final.ipynb`
- A Jupyter notebook that demonstrates the project pipeline, including data analysis, visualization, and playlist generation.

### 2. `gnod_functions.py`
- Contains core Python functions, including:
  - **`get_audio_features_batch()`**: Fetches audio features for a batch of track IDs.
  - **Retry Logic**: Ensures API compliance with rate limits by implementing pauses and retries.
  - **Data Formatting**: Outputs structured data for use in machine learning models or playlist generation.

### 3. `streamlit_metal.py`
- A Streamlit app for generating playlists based on extracted audio features. Allows users to interactively explore and filter tracks by their characteristics.

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/YourRepo.git
Navigate to the project directory:

bash
Code kopieren
cd YourRepo
Install dependencies:

bash
Code kopieren
pip install -r requirements.txt
Set up Spotify API credentials:

Sign up for a Spotify Developer account and create an app.
Save your client_id and client_secret in a .env file:
makefile
Code kopieren
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
Usage
Running the Jupyter Notebook
Open the Jupyter notebook:
bash
Code kopieren
jupyter notebook gnod_final.ipynb
Follow the steps in the notebook to:
Process a dataset of track IDs.
Analyze audio features.
Generate playlists.
Using the Streamlit App
Launch the Streamlit app:
bash
Code kopieren
streamlit run streamlit_metal.py
Interact with the app to explore tracks and generate playlists based on preferences.
Future Enhancements
Integration of advanced clustering algorithms for playlist personalization.
Addition of user login for saving and retrieving playlists.
Support for genre-based recommendations.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
Spotify API for providing access to audio features.
Contributors to open-source libraries like pandas and Spotipy.
