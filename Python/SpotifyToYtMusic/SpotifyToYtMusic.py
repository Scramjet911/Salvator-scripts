import json
import logging
import time
from typing import List, Dict
import os

from spotipy import Spotify, SpotifyOAuth
from ytmusicapi import YTMusic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Export spotify and youtube music keys
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Import the keys for spotify from another file

# YouTube Music setup
YT_HEADERS_PATH = "browser.json"  # Path to YouTube Music headers JSON file

# Initialize APIs
spotify = Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-library-read"))

yt_music = YTMusic(YT_HEADERS_PATH)

def fetch_liked_songs_from_spotify() -> List[Dict[str, str]]:
    """Fetch liked songs from Spotify."""
    logging.info("Fetching liked songs from Spotify...")
    liked_songs = []
    offset = 0
    limit = 50

    while True:
        try:
            results = spotify.current_user_saved_tracks(limit=limit, offset=offset)
            if not results['items']:
                break

            for item in results['items']:
                track = item['track']
                liked_songs.append({
                    'title': track['name'],
                    'artist': ", ".join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name']
                })

            offset += limit

        except Exception as e:
            logging.error(f"Error fetching Spotify songs: {e}")
            break

    logging.info(f"Fetched {len(liked_songs)} liked songs from Spotify.")
    return liked_songs

def search_and_create_playlist_on_youtube(playlist_name: str, songs: List[Dict[str, str]]) -> None:
    """Search for songs on YouTube Music and create a playlist."""
    logging.info(f"Creating playlist '{playlist_name}' on YouTube Music...")
    playlist_id = yt_music.create_playlist(playlist_name, "Replicated from Spotify Liked Songs")
    logging.info(f"Playlist created with ID: {playlist_id}")

    for song in songs:
        try:
            query = f"{song['title']} {song['artist']}"
            search_results = yt_music.search(query, filter="songs")

            if search_results:
                video_id = search_results[0]['videoId']
                yt_music.add_playlist_items(playlist_id, [video_id])
                logging.info(f"Added '{song['title']}' by {song['artist']} to playlist.")
            else:
                logging.warning(f"No match found for '{song['title']}' by {song['artist']}. Skipping.")

        except Exception as e:
            logging.error(f"Error processing song '{song['title']}': {e}")

if __name__ == "__main__":
    # Fetch liked songs from Spotify
    spotify_songs = fetch_liked_songs_from_spotify()

    # Create a YouTube Music playlist and add songs
    search_and_create_playlist_on_youtube("Spotify Liked Songs", spotify_songs)

    logging.info("Task completed.")
