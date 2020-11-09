import lyricsgenius
import config
import json
import pymongo
import sys
import os
import spotipy
from pprint import pprint as pp
from spotipy.oauth2 import SpotifyClientCredentials
from requests.exceptions import HTTPError, Timeout
import time 
import analyzeSong

GENIUS_ACCESS_TOKEN = config.get('GENIUS_CLIENT_ACCESS_TOKEN','api')
# NOTE Make sure this is also the same in your Spotify app.
REDIRECT_URI = config.get('SPOTIPY_REDIRECT_URI','uri')

client_id = config.get('SPOTIPY_CLIENT_ID','api') # NOTE hey do this
client_secret = config.get('SPOTIPY_CLIENT_SECRET','api') # NOTE hey do this
token_url = 'https://accounts.spotify.com/api/token'


spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


cluster = pymongo.MongoClient("mongodb+srv://rapAnalysisUser:fPuQRGR3aRh81BB3@lyricsstorage.9tro8.mongodb.net/LyricsStorage?retryWrites=true&w=majority")
db = cluster["LyricsDB"]
col = db["testArtists"]

file_name = "artist_names.txt"

# Solution 1 using the song name it will find an artist
# There are a lot of similarties in cases 1 and 2 where 
# I feel like they could be combined together - Abduarraheem
def get_lyrics(song_name : str, artist_name : str):
    '''
    TODO Add some error handling for songs not found after searching in lyrics genius.
    Using the song name and the artist name, this function will add songs to their
    respective artist dictionary.

    TODO Review for accessing artist from the db properly.
    There are a few cases to conisder which are the following:
    Case 1 the given Artist already exist in the dictionary:
        - If the given song isn't in the artist dictionary then we use the lyricsgenius api
          and add that song to the artist dictionary.
        - If we already have the song then the results will be generated.
        - After not finding the song in the dict and then searching for it
          in using lyricsgeniius api we use that song name and check if it is in the dictionary

    Case 2 the user inputs case sesnstive or new artist name:
        - First the song will be searched using the given artist.
        - if after finding the song and the artist doesn't exist then we add it to the add that to
          the dict.
        - If they do exist then we simply check if the song provided exists in their dict,
          if it doesn't exist then it will be added if it doesn a result will be generated.

    Advantages:
        - Not 100% sure but I think we do less calls to the lyricgenius API here.

    Disadvantages:
        - A lot checks to the database to see if the song and artist exists before getting info
        from lyrcisgenius if not found  then we use lyric genius and some more checks happen.
    
    Late NOTE this might not be needed at all check this out: 
    https://lyricsgenius.readthedocs.io/en/master/reference/artist.html#lyricsgenius.artist.Artist.song
    '''
    # no song name given then return
    if not song_name:
        return

    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    
    
    # convert json file to dict
    with open("db.json") as json_file: 
        lyricsJSON = json.load(json_file)

    # Case 1
    if artist_name in lyricsJSON:
        print("here")
        # if the song isn't in the dict
        #TODO: Update the document for an artist using mongodb to add a song 
        if not song_name in lyricsJSON[artist_name]:
            song = genius.search_song(song_name, artist_name)
            song_name = song.title.lower()
            if not song_name in lyricsJSON[artist_name]:
                album_name = song.album
                lyrics = song.lyrics
                song_dict = {song_name : [lyrics, album_name]}
                # update artist song list
                lyricsJSON[artist_name].update(song_dict)
                print(lyricsJSON)
        # else it is already in the dict then just process
        else:
            print("Already have lyrics.")
            # print (lyricsJSON[artist_name][song_name])

    # Case 2
    else: # case of user input artist name not being in dict
        song = genius.search_song(song_name, artist_name)
        artist_name = song.artist.lower()
        song_name = song.title.lower()
       
        # check if the arist name gotten from the song not in the dict
        if not artist_name in lyricsJSON:
            album_name = song.album
            lyrics = song.lyrics
            song_dict = {song_name : [lyrics, album_name]}
            artist_dict = {artist_name : song_dict}
            lyricsJSON.update(artist_dict)
            print(lyricsJSON)
        # check if the arist name gotten from the song is in the dict
        else: 
            # if we don't have the song then we need to add it to the dict
            if not song_name in lyricsJSON[artist_name]:
                album_name = song.album
                lyrics = song.lyrics
                song_dict = {song.title : [lyrics, album_name]}
                lyricsJSON[artist_name].update(song_dict)

    # put the generated dict to the json
    with open("db.json", "w") as outfile:  
        json.dump(lyricsJSON, outfile)
    # buildArtist(artist_name) # NOTE for testing comment everything above and uncomment this line
    return


# Solution 2
def buildSongBySong(song_list : list, artist_name : str,builtdict : dict):
    '''
    Given song and artist name go use lyricsgenius api to get
    the song, then check if it exists in the dict, if not then add it
    else generate results 
    '''
    # with open("db.json") as json_file: 
    #     lyricsJSON = json.load(json_file)

    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    numadded = 0
    try: 
        genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
        genius.excluded_terms = ["(Remix)", "(Live)", "(Remastered)", "Cover", "Remaster", "Remix", "Listening Log", "Release Calendar"]
        for idx, song in enumerate(song_list):
            try:
                print(f"searching for {song}")
                genius_songs = genius.search_songs(song)
                pp(genius_songs)
                #for song in songs 
                    # if artits match 
                # add a check here to see if we found the exact song we are looking for
                # weve gotten wrong results before that are tracklists and release charts 
                # or just the wrong song
                if genius_songs is None:
                    #make sure we returned a result before extracting info from it
                    print("Not Found, Skipping...")
                    continue
                found = False
                for gsong in genius_songs['hits']:
                    print(f"Artist: {gsong['result']['primary_artist']['name']} Song: {gsong['result']['title']}")
                    song_name = gsong.title.lower().replace('.', "").replace("$",'s').strip(" ")
                    genius_artist_name = gsong.artist.lower()
                    #if song.lower().strip(" ") in song_name and artist_name.lower() in genius_artist_name:
                    if artist_name.lower() in genius_artist_name:
                        found = True
                         #genius has found the right song, analyze it and add it to the db                    
                        album_name = genius_song.album
                        numadded = idx
                    # col.update with $addToSet 
                        colors, marked = analyzeSong.parse_and_analyze_lyrics(cmd=False,args=genius_song.lyrics)
                    # analyze song now returns none if the parsing fails 
                        if colors is not None:
                            builtdict.update({song_name: [genius_song.lyrics,album_name,colors]})
                if not found: 
                    # print(f"'{song.lower()}' is not in  '{song_name}'")
                    # print("OR")
                    # print(f"'{artist_name.lower()}' is not in '{genius_artist_name}'")
                    print(f"{gsong} by {artist_name} was not found :( ")
                    continue

            except Timeout:
                print("Sleeping after a Timeout for 60sec")
                sleep(60)
                return buildSongBySong(song_list[numadded], artist_name,builtdict)


            # elif song.lower() not in song_name:
            #     print(f"'{song.lower()}' is not in  '{song_name}'")
            #     print("Skipping")
            # elif artist_name.lower() not in genius_artist_name:
            #     print(f"'{artist_name.lower()}' is not in '{genius_artist_name}'")
            #     print("Skipping")
            #     continue
            # else:
        #when we have gone through all the songs, add the whole artist dict to the collection

    except Timeout:
        # if we get timed out, pick up where we left off by recursively calling on the
        # songs that we have not yet processed, carry over the dict to the final call
        # i think this is tail recursion
        print("Sleeping after a Timeout for 60sec")
        sleep(60)
        return buildSongBySong(song_list[numadded], artist_name,builtdict)

    return builtdict
    
    # if not artist_name in lyricsJSON:
    #     song_dict = {song_name : [song.lyrics, album_name]}
    #     artist_dict = {artist_name : song_dict}
    #     lyricsJSON.update(artist_dict)
    # elif not song_name in lyricsJSON[artist_name]:
    #     song_dict = {song_name : [song.lyrics, album_name]}
    #     lyricsJSON.update(artist_dict)
    # generate result here.

# Solution 3
# def solution3(song_name : str, artist_name : str)

def artist_list(artist_list : list):
    for artist in artist_list:
        buildArtist(artist)

def buildArtist(artist_name : str):
    '''
    Get all songs from the given artist.
    Then from the result we can build our database.
    TODO should make all artist names lower case before putting them to the DB
    or check if DB keys aren't case sensitive.
    '''
    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    # Turn off status messages
    # genius.verbose = False

    # Remove section headers (e.g. [Chorus]) from lyrics when searching
    # genius.remove_section_headers = True

    # Include hits thought to be non-songs (e.g. track lists)
    # genius.skip_non_songs = False

    # Exclude songs with these words in their title
    

    

    # NOTE If you want to get all songs from an artist remove max_songs
    try: 
        artist = genius.search_artist(artist_name)
    except: TimeoutError
    songList = artist.songs
    song_dict = {}
    for song in songList:
        song_dict.update({song.title : [song.lyrics, song.album]})
    artist_name = artist.name.replace('.', "").replace("$","s") # TODO replace $ to S, also check for other cases that mongodb doesn't like
    print(artist_name)
    print(f'Song Dict{song_dict}\n\n')
    artist_dict = {artist_name : song_dict}
    print(f'Artist Dict{artist_dict}')
    col.insert_one(artist_dict)
    


def searchForSongs(artist : str) -> list:
    '''
    Takes an artist and returns all song names made by that artist using spotify API 
    '''
    offset = 0
    song_list = []
    while True:
        try:
            results = spotify.search(q='artist:' + artist,limit=50, offset=offset, type='track')
            #do search for 50 tracks
            # if len(result[tracknames] == 0)
            if len(results['tracks']['items']) == 0:
                #stop when no songs are returned with the given offset
                break
            else: 
                for item in results['tracks']['items']:
                    #take out everything in parethesese
                    trackname = item['name'].replace('.', "").replace("$",'s').strip(" ")
                    lparen = trackname.find('(')
                    if lparen != -1:
                        song_list.append(trackname[:lparen])
                    else: 
                        song_list.append(trackname)
                offset+= 50
        except spotipy.exceptions.SpotifyException:
            print("Reached End of Query")
            break

    return song_list

def main():
    '''
    Juno -- 
    Made a main so we can call artist list from a file that we open and read 
    '''
    song_list = []
    with open(sys.argv[1], 'r') as f:
        artist_list = f.read().split('\n')
        print(artist_list) 
        artist_list.remove('')
        for artist in artist_list:
            print(f"getting songs for {artist}")
            song_list = searchForSongs(artist)
            song_list = list(set(song_list))
            print(f"getting lrics for {len(song_list)} songs")
            song_dict = buildSongBySong(song_list, artist,{})
            print(song_dict)
            print("placing into mongodb")
            col[artist.lower().replace('.', "").replace("$",'s')].insert_one(song_dict)



    print(song_list)
        # for item in song_list:
        #     buildArtist(item)

                    #offset +50 
            # if len(artist) > 1:
            #     results = spotify.search(q='artist:' + artist, type='track',limit=50)
            #     restracks = [item for item in results['tracks']['items']]
            #     # resfiltered [item in for item in restracks if item['artists']
            #     for item in restracks:
            #         del item['available_markets']
            #         del item['album']['available_markets']
            #         pp(item)
            #         print(80 * '-')
            #pp(tracknames)
            #buildArtist(artist)


if __name__ == "__main__":
    main()