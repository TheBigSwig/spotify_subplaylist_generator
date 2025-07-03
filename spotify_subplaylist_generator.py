#!/usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from typing import Dict, List

def get_user_playlists(spotify_client : spotipy.Spotify) -> List[Dict]:
    user_playlists = []
    num_playlists_per_request = 50

    api_response = spotify_client.current_user_playlists(limit=num_playlists_per_request)
    while len(api_response['items']) > 0:
        for playlist in api_response['items']:
            user_playlists.append(playlist)
        api_response = spotify_client.current_user_playlists(limit=num_playlists_per_request,
                                                             offset=len(user_playlists))
    return user_playlists

def get_playlist_tracks(spotify_client : spotipy.Spotify, playlist_uri : str) -> List[Dict]:
    playlist_tracks = []
    num_tracks_per_request = 100

    api_response = spotify_client.playlist_items(playlist_uri,
                                                 limit=num_tracks_per_request,
                                                 additional_types=('track',))
    while len(api_response['items']) > 0:
        for track in api_response['items']:
            playlist_tracks.append(track)
        api_response = spotify_client.playlist_items(playlist_uri,
                                                     limit=num_tracks_per_request,
                                                     offset=len(playlist_tracks),
                                                     additional_types=('track',))
    return playlist_tracks

def main():
    print("Welcome to the Spotify Subplaylist Generator!")
    
    print("\nRetrieving Spotify access token...")
    spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-public"))

    print("\nRetrieving user playlist information...")
    user_playlists = get_user_playlists(spotify_client)
    
    if len(user_playlists) == 0:
        print("User does not have any public playlists, so subplaylists cannot be generated")
        print("Exiting...")
        return
    
    print("\nUser playlists:")
    for playlist in user_playlists:
        print(f"> {playlist['name']}")

if __name__ == "__main__":
    main()
