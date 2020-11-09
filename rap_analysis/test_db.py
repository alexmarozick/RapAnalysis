import unittest
import lyricsgenius
from pprint import pprint as pp
import config
GENIUS_ACCESS_TOKEN = config.get('GENIUS_CLIENT_ACCESS_TOKEN','api')
genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN,skip_non_songs=True)
genius.excluded_terms = ["(Remix)", "(Live)", "(Remastered)", "Cover", "Remaster", "Remix", "Listening Log"]
class TestDatabase(unittest.TestCase):
    # def test_songsearch(self):
    #     for song in ["LA Hex"]:
    #         genius_song = genius.search_song(song, "Beast Coast")
    #         pp(genius_song)
    #         pp(genius_song.artist)
    #         pp(genius_song.album)
    #         pp(genius_song.lyrics)

    def test_paren_eleminiation(self):
        a = "test (shit in parens)"
        print(a.find('('))
        b = a[:a.find("(")]
        print(a.find(b))

    def test_paren2(self): 
        a = "kush & corinthians (his pain)" 
        b = "kush & corinthians"
        assert b in a