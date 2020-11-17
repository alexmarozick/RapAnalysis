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


def getsongdata(songdict :dict ) -> dict:
    '''
    Gets the lyrics of a dict of artists and their songs  
    songdict : {"song" : SONGNAME, "artist"}
    returns [{object_id: ObjectID, "album": ALBUM, "colors" : COLORS, 'lyrics' : LYRICS}]
    COLORS is a list of lists. Each sublist corresponds to a section of the song (deliminated by something like [Intro] or [Chorus])
    '''
    db = cluster['Lyrics_Actual']
    res = []
    for item in songdict:
        artist = item['artist'].lower().replace("$","s").replace(".", "")
        query_result = db[artist].find({ "song": item['song']  })
        docs = [doc for doc in query_result]
        res.append(docs)
    pp(res)
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
    getlyrics([{'artist': 'Future', 'song': 'Mask Off'}])

if __name__ == "__main__":
    main()



