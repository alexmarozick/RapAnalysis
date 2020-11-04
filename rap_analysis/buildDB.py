import lyricsgenius
import config
import json
import pymongo
GENIUS_ACCESS_TOKEN = config.get('GENIUS_CLIENT_ACCESS_TOKEN','api')

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
def solution2(song_name : str, artist_name : str):
    '''
    Given song and artist name go use lyricsgenius api to get
    the song, then check if it exists in the dict, if not then add it
    else generate results 
    '''
    with open("db.json") as json_file: 
        lyricsJSON = json.load(json_file)

    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    song = genius.search_song(song_name, artist_name)
    # add a check here to see if we found a song
    artist_name = song.artist.lower()
    song_name = song.title.lower()
    album_name = song.albumn
    if not artist_name in lyricsJSON:
        song_dict = {song_name : [song.lyrics, album_name]}
        artist_dict = {artist_name : song_dict}
        lyricsJSON.update(artist_dict)
    elif not song_name in lyricsJSON[artist_name]:
        song_dict = {song_name : [song.lyrics, album_name]}
        lyricsJSON.update(artist_dict)
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
    # genius.excluded_terms = ["(Remix)", "(Live)"]

    # NOTE If you want to get all songs from an artist remove max_songs
    artist = genius.search_artist(artist_name, max_songs=5)
    songList = artist.songs
    song_dict = {}
    for song in songList:
        song_dict.update({song.title : [song.lyrics, song.album]})
    artist_name = artist.name.strip('$.') # TODO replace $ to S, also check for other cases that mongodb doesn't like
    print(artist_name)
    print(f'Song Dict{song_dict}\n\n')
    artist_dict = {artist_name : song_dict}
    print(f'Artist Dict{artist_dict}')
    col.insert_one(artist_dict)
    