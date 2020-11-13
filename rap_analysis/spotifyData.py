import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
from pprint import pprint as pp

# genres = ['hip hop', 'pop rap', 'rap', 'chicago rap', 'melodic rap', 'canadian hip hop', 'canadian pop', 'toronto rap']
genres = ['hip hop', 'rap', 'pop']

def spotify_data(spotify):
    '''
    We can analyze spotify data depending on user request.
    Some options which could be possible are the following: NOTE add more to this list if needed
    - Playlist of choice.
    - User listening habits.
    - Recent listen as hip hop genre.
    - Followed artists.
    '''
    artists_data = get_followed_artist(spotify)
    playlist_data = get_playlists(spotify)
    recent_plays_data = get_recent_plays(spotify)
    return {"artists" : artists_data, "playlists" : playlist_data, "recent_plays" : recent_plays_data}


def get_followed_artist(spotify):
    '''
    Returns a dictionary of artists in the follwoing format:
        {" Spotify artist id" : ['Artist1 name', [genre list]],
        "Spotify artist id" : ['Artist2 name', [genre list]],
        ...
        }
    '''
    print("Get followed artists")
    artist_dict = {} # will contain all the extracted info from the artists
    all_artists = {}
    user_followed = spotify.current_user_followed_artists()
    while user_followed:
        followed_artists = user_followed['artists']["items"] # a list the conatins info about the followed artists
        for artist in followed_artists:
            if checkGenre(artist["genres"]):
                artist_dict.update({artist["id"] : [artist["name"], artist["genres"]]})
            all_artists.update(({artist["id"] : [artist["name"], artist["genres"]]}))
        # pp(artist_dict)
        if user_followed['artists']['next']:
            user_followed = spotify.next(user_followed['artists'])
        else:
            user_followed = None

    # NOTE for debugging   
    # print("Gotten Artists")
    # print(f'{len(artist_dict)}')
    # pp(artist_dict)
    # diff = {}
    # print(f'{len(all_artists)}')
    # print("All artists")
    # pp(all_artists)
    # for key in all_artists:
    #     if key not in artist_dict:
    #         diff.update({key : all_artists[key]})
    # print("Difference")
    # print(f'{len(diff)}')
    # print(diff)

    return artist_dict

def checkGenre(genre_list):
    for genre in genre_list:
        if genres[0] in genre or genres[1] in genre or genres[2] in genre:
            return True
    return False


def get_playlists(spotify):
    '''
    Returns user playlist.
    Format of dict returned.
    {
        "playlist1-id" : "playlist1-name", "playlist2-id" : "playlist2-name",... 
    }
    '''
    print("Get playlists")
    playlists = spotify.current_user_playlists() # spotify api call that gives at max 50 playlists
    playlists_dict = {}    
    while playlists:
        followed_playlists = playlists["items"]
        for playlist in followed_playlists: # looping through all playlists got from the spotify api call
            # inserts playlist id and playlist name to dicitonary.
            playlists_dict.update({playlist["id"] : playlist["name"]})
        if playlists['next']: # check if there is another playlist next
            playlists = spotify.next(playlists)
        else:
            playlists = None
    return playlists_dict

def get_songs_from_playlist(spotify, playlist_id):
    '''
    Takes in a play list id and returns info on the songs of the playlist
    Format of dict returned.
    {"song1-id" : 
            ["song2-name", 
                {"artist1-id" : "artist1-name", "artist2-id" : "artist2-name"},...,
            ]
        },
    '''

    playlist_tracks = spotify.playlist_tracks(playlist_id)
    track_list = []
    while playlist_tracks:
        for track in playlist_tracks["items"]:
            if track["track"]:
                track_name = track["track"]["name"]
                track_id = track["track"]["id"]
                track_artists  = {}
                for artist in track["track"]["artists"]:
                    track_artists.update({artist["id"] : artist["name"]})
                track_list.append({track_id : [track_name, track_artists]})
        
        if playlist_tracks['next']:
            playlist_tracks = spotify.next(playlist_tracks)
        else:
            playlist_tracks = None
    return track_list


def get_recent_plays(spotify, num_songs=1):
    '''
    TODO make more test cases and do more error handling,
    also don't forget to change some stuff with the num_songs.
    Dict returned format:
    {song-id : [song-name, {
        artist-id : artist-name,...}
        ]
    , ...}
    '''

    recent_dict = {}
    print("Get Recent plays")
    recent_plays = spotify.current_user_recently_played(limit=num_songs)
    recents = recent_plays["items"]
    
    for song in recents:
        artists_dict = {}
        artist_list = song["track"]["artists"]
        for artist in artist_list:
            artists_dict.update({artist["id"] : artist["name"]})
        recent_dict.update({song["track"]["id"] : [song["track"]["name"], artists_dict]})
    return recent_dict




if __name__ == "__main__":
    main()