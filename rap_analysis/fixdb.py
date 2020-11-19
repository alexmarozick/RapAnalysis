#%%
import config
import json
import functools
import pymongo
from bson.objectid import ObjectId
from pprint import pprint as pp
import analyzeSong

mongoconnect = config.get("DBNAME", "MONGODB")
cluster = pymongo.mongo_client(mongoconnect)
db = cluster["Lyrics_Actual"]

colnames = db.list_collection_names()
print(colnames)
print(db[col].find())
for col in colnames:
    collection = db[col]
    docscursor = collection.find()
    docs = [doc for doc in docscursor]
    keys = [(doc.keys(),idx) for idx, doc in enumerate(docs) if "song" not in doc.keys()]
    print(keys)

    # check if artist has proper formatting, if first entry isnt formatted, whole artist wont be 
    i = 0
    # loop through docs, reformat, replace with reformatted
    print(f"WORKING WITH {col}")
    for key, idx in keys:
        _id =  docs[idx]["_id"]
        song = list(key)[1]
        lyrics = docs[idx][song][0]
        album = docs[idx][song][1]
        colors = docs[idx][song][2]
        if lyrics is None or colors is None:
            print(f"{song} is not valid lyrics, skipping")
            continue
        else: 
            # song_list.append( {"song" : song.title.replace('.', "").replace("$","s"), "lyrics" : song.lyrics, "album" : album, "colors" : colors})
            newdoc = {'song' : song, "lyrics" : lyrics, "album" : album, "colors" : colors}
            collection.delete_one({"_id" : ObjectId(_id)})
            collection.insert_one(newdoc)
            print(f".", end="")
    print(f"processed {i} songs ")


# %%
for col in colnames:
    collection = db[col]
    collection.create_index([('song', pymongo.TEXT)], name='search_index', default_language='english')
    print("creatd index for {col}")


# %%
import config
import pymongo
import analyzeSong
from bson.objectid import ObjectId
mongoconnect = config.get("DBNAME", "MONGODB")
cluster = pymongo.MongoClient("mongodb+srv://rapAnalysisUser:fPuQRGR3aRh81BB3@lyricsstorage.9tro8.mongodb.net/LyricsStorage?retryWrites=true&w=majority")
db = cluster["Lyrics_Actual"]

#MADE IT FROM NAS TO THE GAME 

colnames = db.list_collection_names()

for col in colnames:
    collection = db[col]
    print(f"Fixing {col}")
    for doc in collection.find():
        try:
            lyrics = doc['lyrics']
            colors, marked = analyzeSong.parse_and_analyze_lyrics(cmd=False,args=lyrics)
            collection.update_one({"song" : doc['song']},{"$set" : {"colors" : colors}} )
            print(r".", end=r"")
        except KeyError:
            collection.delete_one({"_id" : ObjectId(doc['_id'])})
            print("Invalid song deleted")
        print("")

# %%
