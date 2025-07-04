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
    for index, playlist in enumerate(user_playlists):
        print(f"{index}) {playlist['name']}")

    desired_playlist_index = None
    while desired_playlist_index is None:
        try:
            user_input = int(input("\nEnter the index of the playlist you wish to generate subplaylists from: "))
            if user_input < 0 or user_input >= len(user_playlists):
                print("Invalid selection!")
            else:
                desired_playlist_index = user_input
        except ValueError:
            print("Invalid selection!")
    
    print("\nCurrently supported filters for generating a subset playlist:")
    print("0) Genre")

    filter_index = None
    while filter_index is None:
        try:
            user_input = int(input("\nEnter the index of the filter you wish to use: "))
            if user_input != 0:
                print("Invalid selection!")
            else:
                filter_index = user_input
        except ValueError:
            print("Invalid selection!")
    
    print("\nYou can find a list of some of the main Spotify genres here: https://open.spotify.com/genre/0JQ5DArNBzkmxXHCqFLx3c")
    selected_genre = input("Enter the (lowercase) name of the genre you wish to filter by: ")

    print(f"\nRetrieving songs from '{user_playlists[desired_playlist_index]['name']}'...")
    playlist_tracks = get_playlist_tracks(spotify_client, user_playlists[desired_playlist_index]['uri'])

    print(f"\nRetrieving artist info for all artists referenced in '{user_playlists[desired_playlist_index]['name']}'...")
    artist_info_dictionary = get_artist_info_for_tracks(spotify_client, playlist_tracks)

    print(f"\nFiltering all '{selected_genre}' songs from '{user_playlists[desired_playlist_index]['name']}'...")
    filtered_tracks = []
    for index, playlist_track in enumerate(playlist_tracks):
        if not playlist_track['track']['is_local']:
            for artist in playlist_track['track']['artists']:
                artist_info = artist_info_dictionary[artist['uri']]
                if selected_genre in artist_info['genres']:
                    filtered_tracks.append(playlist_track)
                    break

    if len(filtered_tracks) == 0:
        print(f"\nNo '{selected_genre}' songs were found in '{user_playlists[desired_playlist_index]['name']}'")
    else:
        subplaylist_name = input("\nEnter the desired name for the new subplaylist: ")
        print(f"\nCreating '{subplaylist_name}' subplaylist from filtered songs...")
        create_playlist_with_tracks(spotify_client, subplaylist_name, filtered_tracks)
        print("\nSubplaylist was successfully created!")

if __name__ == "__main__":
    main()
