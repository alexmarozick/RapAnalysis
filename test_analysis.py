import unittest
from analyzeSong import mark_with_rhymes, word_similarity
import logging 
logging.basicConfig(level=logging.DEBUG)

class TestAnalysis(unittest.TestCase):
    def test_cuplet(self): 
        res = ['rap','snitches', 'telling', 'all','their','business',
              'Sit','in','the','court','and','be','their','own','star','witness']
        string = True
        for idx, item in enumerate(res):
            for i in range (idx, len(res)):
                word_similarity(item, res[i])
        self.assertEqual(True,string)

    def test_rhyme(self):
        string = ['hub', 'boo', 'sub', 'coo']
        print(mark_with_rhymes(string, delims=None))
        self.assertTrue(True)


    def test_rhyme2(self):
        string = ['hub', 'boo', 'sub', 'coo','coo','coo','boo','boo']
        print(mark_with_rhymes(string, delims=None))
        self.assertTrue(True)


    def test_repeats(self): 
        string = ['0down0', '0down0', '0down0', '0down0']
        res = ['0down0', '0down0', '0down0', '0down0']
        colorlist, mark_copy = mark_with_rhymes(string,delims=None)
        print(mark_copy)
        self.assertEqual(mark_copy,res)

    def test_numbers(self):
        string = ['one','two','three','four']
        colorlist, mark_copy = mark_with_rhymes(string,delims=None)
        print(mark_copy)
        

    def test_suffix(self):
        string = ["wearin'","stretchin'", "curvin'"]
        # print(word_similarity(string[0],string[1]))


        colorlist, mark_copy = mark_with_rhymes(string,delims=None)
        print(mark_copy)


    

if __name__ == "__main__":
    unittest.main()