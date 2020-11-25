import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
from pprint import pprint as pp

# genres = ['hip hop', 'pop rap', 'rap', 'chicago rap', 'melodic rap', 'canadian hip hop', 'canadian pop', 'toronto rap']
genres = ['hiphop', 'hip hop', 'rap', 'pop']

def spotify_data(spotify):
    '''
    We can analyze spotify data depending on user request.
    Some options which could be possible are the following: NOTE add more to this list if needed
    - Playlist of choice.
    - User listening habits.
    - Recent listen as hip hop genre.
    - Followed artists.
    '''
    playlist_data = get_playlists(spotify)
    # artists_data = get_followed_artist(spotify)
    # recent_plays_data = get_recent_plays(spotify)
    return {'playlists' : playlist_data}


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
            if checkGenre(artist['genres']):
                artist_dict.update({artist['id'] : [artist['name'], artist['genres']]})
            all_artists.update(({artist['id'] : [artist['name'], artist['genres']]}))
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

def checkGenre(genre_list : list) -> bool:
    for genre in genre_list:
        if genres[0] in genre or genres[1] in genre or genres[2] in genre:
            return True
    return False


def get_playlists(spotify) -> dict:
    '''
    Input:
    spotify: Spotipy object.
    Returns user playlist.
    Output
    Format of dict returned.
    {
        "playlist1-id" : "playlist1-name", "playlist2-id" : "playlist2-name",... 
    }
    '''
    # print("Get playlists")
    playlists = spotify.current_user_playlists() # spotify api call that gives at max 50 playlists
    playlists_dict = {}    
    while playlists:
        followed_playlists = playlists['items']
        for playlist in followed_playlists: # looping through all playlists got from the spotify api call
            # inserts playlist id and playlist name to dicitonary.
            playlists_dict.update({playlist['id'] : playlist['name']})
        if playlists['next']: # check if there is another playlist next
            playlists = spotify.next(playlists)
        else:
            playlists = None
    # get_songs_from_playlist(spotify, list(playlists_dict.keys())[0] ) # for testing purposes 
    return playlists_dict

def get_songs_from_playlist(spotify, playlist_id) -> list:
    '''
    Input:
    spotify: Spotipy object
    playlist_id: Playlist id could be in any of the following formats
                Spotify URI: spotify:track:6rqhFgbbKwnb9MLmUQDhG6
                Spotify URL: http://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6
                Spotify ID:  6rqhFgbbKwnb9MLmUQDhG6
    Output:
    Note that if there is multiple artits for one song the artist value will contain
    a list of artists if there is only one artist then the value will be a string containing
    the name of the artist.
    Format of list dicts returned:
    [{song : "song-name1", artist : "artist-name"}, {song : "song-name2", artist : ["artist1-name", "artist2-name"]}, ...]
    
    Other info:
    Additionally some commented out code could get more information on songs for potenial future features
    The format of dict that contains the info will be as follows:
    If multiple artists from one song it would look like this
    [{"song1-id" : 
            ["song2-name", 
                {"artist1-id" : "artist1-name", "artist2-id" : "artist2-name"},...,
            ]
        },]
    if one artist per song then it would look like the following:
        [{"song1-id" : 
            ["song2-name", 
                {"artist1-id" : "artist1-name"},...,
            ]
        },]
    '''

    playlist_tracks = spotify.playlist_tracks(playlist_id)
    track_list = []
    # all_tracksInfo = [] # same trakc_list expect that it will contail all the track extracted info including info from artists that aren't in the hiphop/rap genre
    songs_artists = [] # will contain a dicts taht contain song name and the artists.
    while playlist_tracks:
        for track in playlist_tracks['items']:
            if track['track']:
                # pp(track["track"])
                # track_artist = {} # dict that contains artist id as the key and the value is the artist name
                # same as track_artist execpt that this will also contain artists that don't fall in the hiphop/artist genre 
                # all_artist = {} # NOTE used for debugging

                track_id = track['track']['id']                                 # get song id
                track_name = track['track']['name']                             # get song name
                result = includeSong(spotify, songs_artists, track['track']['artists'],track_name)
                if result:
                    songs_artists.append(result)
                # artist = track["track"]["artists"][0]                           # get the first artist from the list of artist which is most likely the primary artist.
                # artist_id = artist["id"]
                # artist_name = artist["name"]
                # sp_artist = spotify.artist(artist_id)                           # get  artist info given the id
                # # pp(sp_artist)                                                 # for debugging
                # genre_list = sp_artist["genres"]                                # list of genres that the artist has
                # if checkGenre(genre_list):                                      # check if the artist is a hiphop, rap or pop artist
                #     track_artist.update({artist_id : artist_name})              # if so add the artist to the list of 
                #     track_list.append({track_id : [track_name, track_artist]})  
                #     songs_artists.append({'song' : track_name, 'artist' :  artist_name}) #
                
                # all_artist.update({artist_id : artist_name})
                # all_tracksInfo.append({track_id : [track_name, all_artist]})
                # below gets all artists of a songs with their id and names
                # track_artists  = {}
                # for artist in track["track"]["artists"]:
                #     track_artists.update({artist["id"] : artist["name"]})
                # track_list.append({track_id : [track_name, track_artists]})
        
        if playlist_tracks['next']:
            playlist_tracks = spotify.next(playlist_tracks)
        else:
            playlist_tracks = None
    # pp(track_list)
    # print(len(song_artist))
    # print(len(track_list))
    #pp(songs_artists)
    return songs_artists


def repetitionCheck(song_artist : list, song_name : str, artists) -> bool:
    '''
    Checks if the a list of dictionaries
    in the format of [{song : "songname", artist : "artist name"}, ...]
    '''
    for song in song_artist:
        songname = song['song']
        checkSong = song_name == songname
        if type(artists) == list:
            for artist in artists:
                if checkSong and artist in song['artist']:
                    return True
        elif checkSong and artists in song['artist']:
            return True
    return False

def includeSong(spotify, songs_artists : list, artists_info : list, song_name : str):
    '''
    Function that deteremines if the song should be included to be analyzed.
    For the song to be included it must have one of the genres 
    listed and it is a song that isn't included already.

    NOTE could make a few tweaks to remove some stuff if needed - Abduarraheem
    '''
    artists_list = [artist['name'] for artist in artists_info] # put all artist names in a list
    for artist in artists_info:
        artist_id = artist['id']
        sp_artist = spotify.artist(artist_id) 
        genre_list = sp_artist['genres'] # NOTE an idea popped up to mind is that we get all genres of artist and put them all in one list then do a check on that instead
        if checkGenre(genre_list):
            if not repetitionCheck(songs_artists, song_name, artists_list):
                if len(artists_list) == 1: # if we got one artist then insert as a string 
                    return {'song' : song_name, 'artist' : artists_list[0]}
                else: # if not insert as a list of artists
                    return {'song' : song_name, 'artist' : artists_list}
            break
    return None


def get_recent_plays(spotify, num_songs=10):
    '''
    Input: 
    spotify: Spotipy object
    num_songs: Number of songs to get based on user input, default 10 for now.
    
    Output:
    Note that if there is multiple artits for one song the artist value will contain
    a list of artists if there is only one artist then the value will be a string containing
    the name of the artist.
    Format of list dicts returned:
    [{song : "song-name1", artist : "artist-name"}, {song : "song-name2", artist : ["artist1-name", "artist2-name"]}, ...]

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
    recent_plays = spotify.current_user_recently_played()
    
    # pp(recents)
    songCounter = 0 # counter of hiphop/rap songs 
    songs_artists = []
    while recent_plays:
        # print(songCounter)
        recents = recent_plays["items"]
        for song in recents:
            # main_artist = song["track"]["artists"][0]
            # artist_id = main_artist['id']
            # sp_artist = spotify.artist(artist_id)   
            # genre_list = sp_artist["genres"]
            artists_info = song["track"]["artists"]
            result = includeSong(spotify, songs_artists, artists_info, song['track']['name'])
            if result:
                songs_artists.append(result)
                songCounter += 1
           
            if songCounter >= num_songs:
                break
            # artists_dict = {}
            # artist_list = song["track"]["artists"]
            # artists = []
            # for artist in artist_list:
            #     artists.append(artist["name"])
            #     artists_dict.update({artist["id"] : artist["name"]})
            # recent_dict.update({song["track"]["id"] : [song["track"]["name"], artists_dict]})
        # print(songs_artists)

        if recent_plays['next'] and songCounter < num_songs:
            recent_plays = spotify.next(recent_plays)
        else:
            recent_plays = None
    # print(songCounter)
    #pp(songs_artists)
    # pp(list(set(songs_artists)))
    # print('in recent')
    return songs_artists



if __name__ == "__main__":
    main()