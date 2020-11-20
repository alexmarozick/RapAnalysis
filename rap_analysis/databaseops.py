import config
import json
import pymongo
from pprint import pprint as pp

mongo_user = config.get("USER",'MONGODB')
mongo_password = config.get("PASS",'MONGODB')
mongo_clusters = config.get("DBNAME",'MONGODB')


cluster = pymongo.MongoClient("mongodb+srv://rapAnalysisUser:fPuQRGR3aRh81BB3@lyricsstorage.9tro8.mongodb.net/LyricsStorage?retryWrites=true&w=majority")
# cluster = pymongo.MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_clusters}")
db = cluster["Lyrics_Actual"]




def searchfor():
    pass


def getsongdata(songdict :list) -> list:
    '''
    Gets the lyrics of a dict of artists and their songs  
    songdict : {"song" : SONGNAME, "artist"}
    returns [{object_id: ObjectID, "album": ALBUM, "colors" : COLORS, 'lyrics' : LYRICS}]
    COLORS is a list of lists. Each sublist corresponds to a section of the song (deliminated by something like [Intro] or [Chorus])
    '''
    db = cluster['Lyrics_Actual']
    dbArtists = db.list_collection_names()
    res = []
    for item in songdict:
        if type(item['artist']) == list: # NOTE the way I am doing these checks could probably be done better also something else to consider is what if no artist is given - Abduarraheem
            for a in item['artist']:
                artist = a.lower().replace("$","s").replace(".", "")
                # query_result = db[artist].find({ "song": item['song']  })
                if artist in dbArtists:
                    query_result = db[artist].find({"$text" :{"$search" : item['song'], "$caseSensitive" : False}})
                   
                    # print(item['song'])
                    # break because one of the artists was in the data base, 
                    # NOTE then since we can't be 100% sure that this artist 
                    # has the song we are looking for we would need to go 
                    # to the next artist in the list to check if the artist has the song given.
                    break  
                else:
                    print(f"Error Artist {artist} not in the Data Base")

        else:
            artist = item['artist'].lower().replace("$","s").replace(".", "")
            if artist in dbArtists:
                query_result = db[artist].find({"$text" :{"$search" : item['song'], "$caseSensitive" : False}}) 
            else:
                print(f"Error Artist {artist} not in the Data Base")
        try:
            docs = [doc for doc in query_result]
            res.append(docs)
        except (UnboundLocalError, TypeError): # if the artist wasn't in the db, go the next song.
            continue
    # pp(res)
    return res



def getcolors():
    '''
    getcolors of a list of songs 
    '''
    pass

def songs_in_db():
    """
    Given a list of songs, returns a subset of all which are contained in the db 
    """
    pass


def main():
    getsongdata([{'artist': 'RZA', 'song': 'tragedy'}])

if __name__ == "__main__":
    main()



