import analyzeSong
import pymongo

cluster = pymongo.MongoClient("mongodb+srv://rapAnalysisUser:fPuQRGR3aRh81BB3@lyricsstorage.9tro8.mongodb.net/LyricsStorage?retryWrites=true&w=majority")
db = cluster["LyricsDB"]
col = db["LyricsCollection"]
def add_song(col : "Collection",colors : list, lyrics : str, songname : str):
    col.insert_one({'song' : songname, "lyrics" : lyrics, "colors" : colors })
         




    return None

def get_lyrics():


    return None 


def main():
    print(db.list_collection_names())
    # add to mongodb
    file = "Test_Lyrics/somethings_underneath.txt"
    songname = "Something Underneath"
    with open(file,'r') as l:
        colors, marked = analyzeSong.parse_and_analyze_lyrics(cmd=False,args=l.read())
        add_song(col, colors,l.read(),songname)

    print(col.inserted_id)

if __name__ == "__main__":
    main()

