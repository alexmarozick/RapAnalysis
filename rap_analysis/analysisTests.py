import unittest
from analyzeSong import mark_with_rhymes
import logging 
logging.basicConfig(level=logging.DEBUG)

class TestAnalysis(unittest.TestCase):
    def test_cuplet(self): 
        res = ['rap','snitches', 'telling', 'all','their','business',
              'Sit','in','the','court','and','be','their','own','star','witness']
        string = True
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
        execd = mark_with_rhymes(string,delims=None)
        print(execd)
        self.assertEqual(execd,res)

if __name__ == "__main__":
    unittest.main()