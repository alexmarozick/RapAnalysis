"""
Juno Mayer
Test of Datamuse API on a song 
"""
import os 
import sys
import requests 
from copy import deepcopy
import logging
import json

logging.basicConfig(level=logging.INFO)

def get_rhymes(word : str) -> dict:
    """ 
    Calls Datamuse API to find the rhymes of a word
    exact, approximate, and homophone 
    """

    url = "https://api.datamuse.com/words?"
    perfect = json.loads(requests.get(url,params={'rel_rhy' : word}).text)
    logging.debug(f"perfect rhymes {perfect}")
    near = json.loads(requests.get(url,params={'rel_nry' : word}).text)
    logging.debug(f"near rhymes{near} ")
    homophone = json.loads(requests.get(url,params={'rel_hom' : word}).text)
    logging.debug(f"homophones {homophone}")

    return perfect,near,homophone

def mark_with_rhymes(lyrics : str) -> str: 
    """
    marks the lyrics with delims around words based on rhymes 
    """
    #split lyrics string by newline to create a list by line 
    #split each line by space to get a list of lists 
    #create copy to iterate through and remove already processed 
    split_lyrics = lyrics.split()

    # for line in lines: 
    #     split_lyrics.append(line.split())
    print(split_lyrics)
    #make copy unique to remove repeated lines 
    iter_copy = deepcopy(split_lyrics)
    # iter_copy = list(set(iter_copy))
    # mark_copy = deepcopy(split_lyrics)

    found_rhymes = 0 
    prev_found = 0
    for word in split_lyrics:
        # if word is not marked already as rhyming
        if '!@*' not in word:
            perflist = []
            nearlist = []
            homlist = []
            #call datamuse api to get possible rhyming words with found word
            print("calling api")
            perfect, near, homophone = get_rhymes(word)
            if perfect is not [] or None:
                perflist = [d['word'] for d in perfect]
            if near is not [] or None: 
                nearlist = [d['word'] for d in near]
            if homophone is not [] or None: 
                homlist = [d['word'] for d in homophone]

            #loop through list of possible words 
            # if one of those words are in the lyrics, mark all occurances of it in the lyrics based on number and type
            # delete all occurances of the found rhyme words 
            
            for p in nearlist:
                indices = [i for i, x in enumerate([word for word in split_lyrics]) if x == p]
                for i in indices:
                    logging.info(f"{word} rhymes with {split_lyrics[i]}")
                    split_lyrics[i] = f"!{found_rhymes}{split_lyrics[i]}!"
                    found_rhymes += 1

            # for n in nearlist:
            #     print(n)
            # for h in homlist:
            #     print(h)
        #call datamuse api to get possible rhyming words with found word
        #loop through list of possible words 
            # if one of those words are in the lyrics, mark all occurances of it in the lyrics based on number and type
            # delete all occurances of the found rhyme words 


    #     found = False
    #     for cpyword in iter_copy:
    # #       if word similarity(word, copyword) > 0 then its a rhyme
    #         if word_similarity(word,cpyword) > .3:
    #             found = True
    #             delimnated = str(found_rhymes) + cpyword + str(found_rhymes)
    #             # replace the word that rhymes with a delimnated version of it
    #             mark_copy[mark_copy.index(cpyword)] = delimnated
    #             print(f"word {delimnated} rhymes with {cpyword}")
    #             #delete it so we save time
    #             iter_copy.remove(cpyword)
        
    #     if found: 
    #         # this word did not rhyme and has not been delimnated / appended
    #         found_rhymes += 1 
        
    return split_lyrics

def main():
    lyrics = "rap snitches, telling all their business \
Sit in the court and be their own star witness \
\
Do you see the perpetrator? Yeah, I'm right here \
Fuck around, get the whole label sent up for years \
\
Type profile low, like A in 'Paid in Full' \
Attract heavy cash cause the game's centrifugal\
\
Mr. Fantastik, long dough like elastic\
Guard my life with twin Glocks that's made out of plastic\
\
Can't stand a brown nosing nigga, fake ass bastard\
Admiring my style, tour bus through Manhattan\
\
Plotting, plan the quickest, my flow's the sickest\
My hoes be the thickest, my dro the stickiest\
\
Street nigga, stamped and bonafide\
When beef jump niggas come get me cause they know I ride\
\
True to the ski mask, New York's my origin\
Play a fake gangsta like a old accordion\
According to him, when the D's rushed in\
Complication from the wire testimony was thin\
Caused his man to go up north, the ball hit 'em again\
Lame rap snitch nigga even told on the Mexican"

lshort = "rap snitches, telling all their business \
Sit in the court and be their own star witness \
\
Do you see the perpetrator? Yeah, I'm right here \
Fuck around, get the whole label sent up for years"

# marked = mark_with_rhymes(lyrics)

# print(get_rhymes("test"))
# print(get_rhymes("snitches"))
print(mark_with_rhymes(lshort))

if __name__ == "__main__":
    main()