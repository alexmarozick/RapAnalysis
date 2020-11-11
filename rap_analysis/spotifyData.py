import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
from pprint import pprint as pp

genres = ['hip hop', 'pop rap', 'rap', 'chicago rap', 'melodic rap', 'canadian hip hop', 'canadian pop', 'toronto rap']

def spotify_data(spotify):
    '''
    We can analyze spotify data depending on user request.
    Some options which could be possible are the following: NOTE add more to this list if needed
    - Playlist of choice.
    - User listening habits.
    - Recent listen as hip hop genre.
    - Followed artists.
    '''
    # get_followed_artist(spotify)
    get_playlist(spotify)
    # get_recent_plays(spotify)


def get_followed_artist(spotify):
    '''
    Returns a dictionary of artists in the follwoing format:
        {"Artist1 name" : ['Spotify artist id', [genre list]],
        "Artist2 name" : ['Spotify artist id', [genre list]],
        ...
        }
    '''
    print("Followed artists")
    user_followed = spotify.current_user_followed_artists()
    pp(user_followed)
    if not user_followed:
        # display this to the user
        print("No followed artists.")
        return
    pp(user_followed["artists"])
    followed_artists = user_followed['artists']["items"] # a list the conatins info about the followed artists
    print('\n')
    artist_dict = {} # will contain all the extracted info from the artists
    for i in range (len(followed_artists)):
        if checkGenre(followed_artists[i]["genres"]):
            artist_dict.update({followed_artists[i]["name"] : [followed_artists[i]["id"], followed_artists[i]["genres"]]})
    print("Artist Dict")
    pp(artist_dict)
    print('\n')
    return artist_dict

def checkGenre(genre_list):
    for genre in genre_list:
        if genre in genres:
            return True
    return False

def get_playlist(spotify):
    '''
    Format of dict returned.
    {
        "playlist1-name" : 
            ["playlist id", [
                {"song1-name" : 
                    ["song-id", 
                        {"artist1-name" : "artist1-id", "artist2-name" : "artist2-id"},...,
                    ]
                },
                {"song2-name" : 
                    ["song-id", 
                        {"artist1-name" : "artist1-id", "artist2-name" : "artist2-id"},...,
                    ],
                },...
            ]
            ]
            "playlist2-name" : ...
    }
    '''
    print("Get playlists")
    playlists = spotify.current_user_playlists()
    pp(playlists)
    followed_playlists = playlists["items"]
    playlists_dict = {}
    for i in range (len(followed_playlists)):
        playlist_tracks = spotify.playlist_tracks(followed_playlists[i]["id"], fields="items")
        # error check here
        track_list = []
        for track in playlist_tracks["items"]:
            track_name = track["track"]["name"]
            track_id = track["track"]["id"]
            track_artists  = {}
            for artist in track["track"]["artists"]:
                track_artists.update({artist["id"] : artist["name"]})
            track_list.append({track_id : [track_name, track_artists]})
        playlists_dict.update({followed_playlists[i]["id"] : [followed_playlists[i]["name"], track_list]})
    
    print('\n')
    pp(playlists_dict)
    print("\ninfo on playlist")
    # playlist_tracks
    return playlists_dict


def get_recent_plays(spotify, num_songs=10):
    print("Get Recent plays")
    pp(spotify.current_user_recently_played(limit=num_songs))
    print('\n')

# current_user_recently_played(limit=50, after=None, before=None)
# Get the current user’s recently played tracks

#current_user_saved_albums(limit=20, offset=0)
# Gets a list of the albums saved in the current authorized user’s “Your Music” library 
# current_user_top_artists(limit=20, offset=0, time_range='medium_term')
# Get the current user’s top artists

# could create a playlist for the user
# user_playlist_create(user, name, public=True, collaborative=False, description='')
# Creates a playlist for a user

# user_playlists(user, limit=50, offset=0)
# Gets playlists of a user
# current_user_followed_artists(limit=20, after=None)
# Gets a list of the artists followed by the current authorized user




if __name__ == "__main__":
    main()