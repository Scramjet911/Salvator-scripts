# Spotify to YouTube Music Playlist Replicator

## Overview

This Python script replicates your Spotify "Liked Songs" playlist to YouTube Music.

## Features

- Fetch "Liked Songs" from Spotify.
- Search for equivalent songs on YouTube Music.
- Create a new playlist on YouTube Music and add matched songs.
- Robust error handling for API failures.

## Prerequisites

- Python 3.9+
- Install required Python libraries:
  ```sh
  pip install spotipy ytmusicapi python-dotenv
  ```
- Spotify API credentials:
  - Create an app at the Spotify Developer Dashboard.
  - Set up a redirect URI and note down the Client ID and Client Secret.
- YouTube Music API setup:
  - Open Youtube Music on your browser and copy the headers of any one authenticated request (Right click -> Copy value -> Copy headers)
  - Run `ytmusicapi browser` on the terminal and paste the headers in it. This will generate the `browser.json` file required

## Setup

- Create a new `.env` file in the same location as the script with the following keys:
```sh
SPOTIFY_CLIENT_ID=xxx
SPOTIFY_CLIENT_SECRET=xx
SPOTIFY_REDIRECT_URI=xx
```
- Ensure `browser.json` is placed in the working directory.

## Usage

- Run the script:
  ```sh
  python SpotifyToYtMusic.py
  ```
  The script will:
  - Authenticate with Spotify using OAuth 2.0.
  - Retrieve liked songs from Spotify.
  - Authenticate with YouTube Music using the headers file.
  - Create a new playlist and replicate songs on YouTube Music.
