#!/usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyOAuth

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read"))
    
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])

if __name__ == "__main__":
    main()
