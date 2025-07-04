#!/usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from typing import Dict, List
import math

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

# Returns a dictionary mapping artist URI to artist info for all artists of a list of tracks.
def get_artist_info_for_tracks(spotify_client : spotipy.Spotify, tracks : List[Dict]) -> Dict[str, Dict]:
    referenced_artists_uris = set()
    for track in tracks:
        if not track['track']['is_local']:
            for artist in track['track']['artists']:
                referenced_artists_uris.add(artist['uri'])
    referenced_artists_uris = list(referenced_artists_uris)

    all_artists_info = {}
    batch_size = 50
    for slice_index in range(math.ceil(len(referenced_artists_uris) / batch_size)):
        artist_uris_batch = referenced_artists_uris[(slice_index * batch_size) : ((slice_index + 1) * batch_size)]
        batch_artist_info = spotify_client.artists(artist_uris_batch)
        for artist_info in batch_artist_info['artists']:
            all_artists_info[artist_info['uri']] = artist_info
    return all_artists_info

def create_playlist_with_tracks(spotify_client : spotipy.Spotify, playlist_name : str, tracks : List[Dict]) -> None:
    new_playlist_info = spotify_client.user_playlist_create(spotify_client.current_user()['id'], playlist_name)

    batch_size = 100
    for slice_index in range(math.ceil(len(tracks) / batch_size)):
        track_batch = tracks[(slice_index * batch_size) : ((slice_index + 1) * batch_size)]
        
        track_batch_uris = []
        for track in track_batch:
            track_batch_uris.append(track['track']['uri'])
        
        spotify_client.playlist_add_items(new_playlist_info['id'], track_batch_uris)

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
