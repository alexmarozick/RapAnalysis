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

mongo_client = config.get("CLIENT",'MONGODB')

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# cluster = pymongo.MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_clusters}")
cluster = pymongo.MongoClient(mongo_client)
# pymongo.MongoClient("mongodb+srv://rapAnalysisUser:fPuQRGR3aRh81BB3@lyricsstorage.9tro8.mongodb.net/<dbname>?retryWrites=true&w=majority")

db = cluster["Lyrics_Actual"]
# col = db["testArtists"]

file_name = "toprappers.txt"

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
def buildSongBySong(song_list : "list[(song,album)]", artist_name : str,builtlist : list):
    '''
    Given song and artist name go use lyricsgenius api to get
    the song, then check if it exists in the dict, if not then add it
    else generate results 
    '''
    # with open("db.json") as json_file: 
    #     lyricsJSON = json.load(json_file)

    #create a collection for the artist 
    log = open('log.txt', 'a')
    added_songs = []
    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    numadded = 0
    try: 
        genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
        genius.excluded_terms = ["(Remix)", "(Live)", "(Remastered)", "Cover", "Remaster", "Remix", "Listening Log", "Release Calendar"]
        genius.skip_non_songs = True
        for idx, entry in enumerate(song_list):
            try:
                song = entry[0]
                album = entry[1]
                print(f"searching for {song} by {artist_name}")
                if song in added_songs:
                    print("Duplicate, already in list, Skipping ...")
                    continue

                genius_songs = genius.search_songs(f"{song} {artist_name}")
                lyrics = ""

                # pp(genius_songs)
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
                    song_name = gsong['result']['title']
                    genius_artist_name = gsong['result']['primary_artist']['name']
                    gid = gsong['result']['id']
                    
                    print(f"is {artist_name} in {genius_artist_name}?")
                    if artist_name in genius_artist_name and song in song_name:
                        lyrics = genius.lyrics(gid)
                        found = True
                        break
                         #genius has found the right song, analyze it and add it to the db                    
                        # album_name = genius_song.album
                if not found: 
                    # print(f"'{song.lower()}' is not in  '{song_name}'")
                    # print("OR")
                    # print(f"'{artist_name.lower()}' is not in '{genius_artist_name}'")
                    print(f"{song} by {artist_name} was not found, trying again with artist")
                    try: 
                        genius_song = genius.search_song(song,artist_name)
                    except TypeError:
                        print("Sleeping after a Timeout for 60sec")
                        time.sleep(5*60)
                        print("DONE SLEEPING")
                        log.close()
                        return buildSongBySong(song_list[numadded], artist_name,builtlist)

                    if genius_song is None:
                        print(f"Search_Song returned no results for {song} by {artist_name}")
                    else:
                        song_name = genius_song.title
                        genius_artist_name = genius_song.artist
                        print(f"Search_Song Got {song_name} {artist_name}")
                        if song in song_name:
                            found = True
                            lyrics = genius_song.lyrics

                if found:
                    numadded += 1 
                    print(f"{numadded} SONG ADDED")
                    # col.update with $addToSet 
                    colors, marked = analyzeSong.parse_and_analyze_lyrics(cmd=False,args=lyrics)
                    # analyze song now returns none if the parsing fails 
                    if colors is not None:
                        builtlist.append({song: [lyrics,album,colors]})
                        added_songs.append(song)
                    log.write(f"{song} by {artist_name}:  {numadded} / {len(song_list)} \n")
                                      

                else: 
                    print("Both Methods failed, moving on :( ...")



            except TypeError:
                print("Sleeping after a Timeout for 5 min")
                time.sleep(5*60)
                print("DONE SLEEPING")
                log.close()
                return buildSongBySong(song_list[numadded], artist_name,builtlist)

            except IndexError: 
                print("recursive Call Failed After timeout")
                print(f"Song list {song_list}, built list {builtlist}")
                return builtlist

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
        return buildSongBySong(song_list[numadded], artist_name,builtlist)

    return builtlist
    
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
    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN, retries=1000, skip_non_songs=True,excluded_terms=["Remix", "Live", "Remastered", "Cover", "Remaster", "Remix", "Listening Log", "Release Calendar"])
    # Turn off status messages
    # genius.verbose = False

    # Remove section headers (e.g. [Chorus]) from lyrics when searching
    # genius.remove_section_headers = True

    # Include hits thought to be non-songs (e.g. track lists)
    # genius.skip_non_songs = False

    # Exclude songs with these words in their title

    # NOTE If you want to get all songs from an artist remove max_songs
    try:
        artist = genius.search_artist(artist_name, max_songs=500)
    except: 
        print(f"Oops something happened getting {artist_name}... moving on...")
        return None

    artist_name = artist.name.replace('.', "").replace("$","s").lower()

    print(f"Saving Lyrics for {artist_name}")
    artist.save_lyrics(filename=f"{artist_name}_Lyricsjson",overwrite=True)

    print(f"creating collection for {artist_name}")
    if artist_name not in db.list_collection_names():
        db.create_collection(artist_name)

    songList = artist.songs
    song_list = []
    print(f"Analyzing lyrics for {artist_name}")
    for song in songList:
        results = {}
        album = ""
        try:  
            results = spotify.search(q='track:' + song.title,limit=50, offset=0, type='track')
            album = results['tracks']['items'][0]['album']['name'].replace('.', "").replace("$","s")
        except: 
            print(f"song {song} not found on spotify.. putting blank album")
        # pp(results)
        colors, marked = analyzeSong.parse_and_analyze_lyrics(cmd=False,args=song.lyrics)
        song_list.append( {"song" : song.title.replace('.', "").replace("$","s"), "lyrics" : song.lyrics, "album" : album, "colors" : colors})

    db[artist_name].insert_many(song_list)
    db[artist_name].create_index([('song', pymongo.TEXT)], name='search_index', default_language='english')
    # db[artist.lower().replace('.', "").replace("$",'s')].insert_many(entry_list)
    



def searchForSongs(artist : str) -> list:
    '''
    Takes an artist and returns all song names made by that artist using spotify API 
    '''
    offset = 0
    song_list = []
    albumresults = spotify.search(q='artist:' + artist,limit=50, offset=offset, type='album')
    artist_albums = [item['name'] for item in albumresults['albums']['items']]
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
                    album = item['album']['name']
                    if album not in artist_albums:
                        continue
                    #take out everything in parethesese
                    trackname = item['name']
                    track = ""
                    
                    lparen = trackname.find('(')
                    if lparen != -1:
                        track = trackname[:lparen].strip(" ")
                        song_list.append((trackname[:lparen].strip(" "),album))
                    else: 
                        track = trackname
                    if track not in [e[0] for e in song_list]:
                        song_list.append((track,album))
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
        #artist_list.remove('')
        for artist in artist_list:

            print(f"getting songs for {artist}")
            buildArtist(artist)

            # song_list = searchForSongs(artist)
            # song_list = list(set(song_list))

            # print(f"getting lrics for {len(song_list)} songs")
            # entry_list = buildSongBySong(song_list, artist,[])

            # print(f"{len(entry_list)} song by {artist} found")
            # try:
            #     with open(f"{artist}_songlyrics.txt", 'w') as f: 
            #         f.write(str(entry_list))
            # except: 
            #     print("Could not write file")

            
            # print("placing into mongodb")
            # # .replace('.', "").replace("$",'s').strip(" ")
            # # {song: [lyrics,album,colors]}
        
            # # format the artists to remove special chars ($, .) and strip trailing whitespace
            # # by updating the names of the keys in the list of dicts 
            # songs = [list(d.keys())[0] for d in entry_list]
            # for i,d in enumerate(entry_list): 
            #     d[songs[i].replace('.', "").replace("$",'s').strip(" ")] = d.pop(songs[i]) 

            # # add the new entries to the db
            # db[artist.lower().replace('.', "").replace("$",'s')].insert_many(entry_list)
    



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


