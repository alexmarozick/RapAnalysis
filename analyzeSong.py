"""
Juno Mayer
A test of kevin brown's rhyme detection  
takes lyrics, tokenizes them, prints them out to console with marks to deliminate rhymes

"""
import os 
import sys
from pprint import pprint as pp
from copy import deepcopy
import nltk
import logging
import json
import random


logging.basicConfig(level=logging.INFO)

#TODO: Look at checking by syllable, if its not possible 
# Then check last TWO phonemes for rhyme 
phone_dictionary = nltk.corpus.cmudict.dict()

def possible_phones(word):

    if word not in phone_dictionary:
        return []
    return phone_dictionary[word]


def phon_match(first_phon : list, second_phon : list,start : int, end: int,debug=False) -> int:
    logging.debug(f"FIRST: {first_phon} SECOND: {second_phon}")
    first_range = first_phon[start:end]
    second_range = second_phon[start:end]

    first_range = first_range[::-1]
    second_range = second_range[::-1]

    if debug:
        logging.debug(f"FIRST RANGE: {first_range}, SECOND RANGE: {second_range}")

    # we only want to loop through the smallest range
    if len(first_range) > len(second_range):
        first_range, second_range = second_range, first_range

    hits = 0
    total = len(first_range)
    #TODO: check if there is only one phoneneme in first_range, 
    # if so we can take out the loop here
    for idx, phone in enumerate(first_range):
        other_phone = second_range[idx]

        if phone == other_phone:
            hits += 1

            # Phones with emphasis are better matches, weight them more
            if phone[-1].isdigit():
                hits += 1
                total += 1

    return hits/total

def word_similarity(first_word, second_word, start_phone=None, end_phone=None,debug=False):
    # print(f"looking up Phonemes for {first_word} and {second_word}")
    first_word = first_word.strip(".!?-()").replace("in'", "ing")
    second_word = second_word.strip(".!?-()").replace("in'", "ing")
    
    first_phones = possible_phones(first_word)
    second_phones = possible_phones(second_word)
    logging.debug(f"SIMILARITY BETWEEN: {first_word} {first_phones} {second_word} {second_phones}")

    if not first_phones or not second_phones:
        return 0

    # If there is only one pronouciation of both words
    if len(first_phones) + len(second_phones) == 2:
        first_phones = first_phones[0]
        second_phones = second_phones[0] 
        return phon_match(first_phones, second_phones,start_phone,end_phone,debug=True)
    
    else:
    # multiple pronouciations for one or both words
    #we want to find if any pronouciations result in a rhyme
    # append all rhyme scores to list, if any of them > 0 its a rhyme
        scorelist = []
        for f_p in first_phones:
            for s_p in second_phones: 
                scorelist.append(phon_match(f_p,s_p,start_phone,end_phone,debug=True))
            
        if 1 in scorelist:
            return 1
        else: 
            return 0

def mark_with_rhymes(lyrics : str) -> str: 
    """
    marks the lyrics with delims around words based on rhymes 
    """

    #make copy unique to remove repeated lines 
    logging.debug(lyrics)
    mark_copy = deepcopy(lyrics)

    found_rhymes = 0 
    prev_found = 0
    numremoved = 0
    colorlist = [-1] * len(mark_copy)
    # logging.info(f"{colorlist},{mark_copy}")
    rhymecolor = random.randint(0,0xFFFFFF)

    #"dead in the middle of little italy"
    # middle == rhymer, little == rhymee
    for idx, rhymer in enumerate(lyrics):
        if '[' in rhymer or ']' in rhymer:
            print(rhymer)
        found = False
        # iter_seg = iter_copy[split_lyrics.index(word)-20:split_lyrics.index(word)+20]
        for rhymee in mark_copy[idx + 1:]:
    #       if word similarity(word, copyword) > 0 then its a rhyme
            if rhymee in lyrics:
                they_rhyme = False
                # we are concerned with end rhymes for now, only want to check if the last phoneme in the word matches
                # so start at the last phoneme of the shortest word (length of shortest - 1 OR 1 if its a 1 phoneme word)
                rhymer_phon = possible_phones(rhymer.strip(".!?-()").replace("in'", "ing"))
                rhymee_phon = possible_phones(rhymee.strip(".!?-()").replace("in'", "ing"))

                #criteria for rhyming depends on if the word is in the phoneme dictionary or not
                # if one of the words are not, the best we can do is check for exact equaliy (for now)
                if rhymer_phon == [] or rhymee_phon == []: 
                    they_rhyme = rhymer == rhymee
                    logging.debug(f"{rhymer} or {rhymee} was not found in CMUDict")
                else:
                    #shortest pronounciation of each word 
                    shortest_rhymer_phon = min(rhymer_phon, key=len)
                    shortest_rhymee_phon = min(rhymee_phon, key=len)
                    shortest_phon = min([shortest_rhymee_phon,shortest_rhymer_phon], key=len)
                    # rhymer_phon if len(rhymer_phon[0]) <= len(rhymee_phon[0]) else rhymee_phon

                    logging.debug(f"RHYMER: {rhymer} {rhymer_phon}, RHYMEE: {rhymee} {rhymee_phon}, SHORTEST: {shortest_phon}")
                    logging.debug(f"{len(shortest_phon)} phonemes in {shortest_phon}")
                    # if we have a 1 phoneneme word, we dont subtract off the end (last phoneme is the only phoneme)
                    nphones_in_shortest = 0 if (len(shortest_phon) - 1) == 0 else len(shortest_phon) - 1
                    #also do string literal comparison  
                    they_rhyme = word_similarity(rhymer,rhymee, start_phone=(nphones_in_shortest -1), debug=True) == 1


                if they_rhyme:
                    found = True
                    #print(f"{rhymer} rhymes with {rhymee}")
                    #rhyme is between WORD in splitlyrics (original) and some other word (rhymee) in the iter_copy
                    #mark both words in rhyme pair with the same number 
                    delimnated_rhymer = str(found_rhymes) + rhymer.replace("in'", "ING") + str(found_rhymes)
                    delimnated_rhymee = str(found_rhymes) + rhymee.replace("in'", "ING") + str(found_rhymes)
                    # replace ALL INSTANCES of the rhymee with a delimnated version of it
                    rhymee_indicies = [i for i, x in enumerate(mark_copy) if x == rhymee]
                    logging.debug(f"matching {rhymer}, {rhymee} is in {rhymee_indicies}")
                    for i in rhymee_indicies:
                        mark_copy[i] = delimnated_rhymee
                        colorlist[i] = found_rhymes

                    if mark_copy[idx] == rhymer:
                        mark_copy[idx] = delimnated_rhymer
                        colorlist[idx] = found_rhymes

                    else:
                        logging.debug(f"{rhymer, idx} alerady marked by another rhyme, rhymee: {rhymee}")
                        logging.debug(f"{rhymee_indicies}   indicies")
    
                        # if we dont find the word, its because its already been marked 
            
                    logging.debug(f"word {delimnated_rhymer} rhymes with {delimnated_rhymee}")
                    #delete it so we save time
                    # iter_copy.remove(rhymee)
        if found: 
            # this word did not rhyme and has not been delimnated / appended
            found_rhymes += 1
            rhymecolor = random.randint(0,0xFFFFFF)

    # retroactively remove cases where the rhymer is delimnated without a rhymee 
    # i.e. only one instance of that num in colorlist
    for num in range(found_rhymes):
        indicies_of_rhymenum = [i for i, x in enumerate(colorlist) if num == x]
        if len(indicies_of_rhymenum) == 1: 
            # marking as 0 means no highlight 
            colorlist[indicies_of_rhymenum[0]] = 0
    return colorlist, mark_copy


def parse_lyrics(lyrics) -> list:
    '''
    returns a parsed lyrics list for a given lyrics string
    Genius separates song sections (Verse, Chorus, Intro, Outro, etc) by newlines and square brackets:
    [Verse 1]
    ...
    ...
    ...

    [Chorus]
    .......
    .......

    We split lyrics into lists based on these sections and remove section headers

    '''
    # split lyrics by "[]" to seperate verses and choruses
    # pprint.pprint(lyrics.split('\n'))
    split_newl = lyrics.lower().split('\n')
    size = len(split_newl)
    parsed_lyrics = []
    #get indicies of all instances of empty string (these are blank lines inbetween sections)
    idx_list = [idx + 1 for idx, val in enumerate(split_newl) if val == ''] 
    #generate new list seperated by sections 
    try:
        sections = [split_newl[i: j] for i, j in zip([0] + idx_list, idx_list + ([size] if idx_list[-1] != size else []))] 
    except IndexError:
        print("Invalid Lyrics")
        return None, None
    # pprint.pprint(sections)        
        # print("THIS MANY SECTIONS IN THE SONG")
        # print(len(sections))
        #remove troublesome characters from lyrics
    for section in sections:
        words = []
        for l in section[1:]:
            for word in l.split():
                words.append(word.strip(",?\".()—")) 
        parsed_lyrics.append(words)

    return parsed_lyrics

def analyze_lyrics(lyrics: list) -> list:
    """
    Takes in lyrics, and analyzes them for rhymes, returning a list[list] of Rhyme Numbers by section
    lyrics: [[list of words in section] for each section]
    
    returns:
    rhyme_numbers: [[list of rhyme numbers] for each section]
    rhyme_numbers and lyrics are one-to-one
    marked_lyrics: A String of lyrics where rhyming words are delimnated by their rhyme number
    used for debugging and development
    """
    rhyme_num_list = []
    marked_lyrics = []
    for section in lyrics:
        if section != []:
            rhyme_numbers, marked = mark_with_rhymes(section)
            logging.debug(f"RhymeNumbers: {len(rhyme_numbers)}MARKED {len(section)} ")
            rhyme_num_list.append(rhyme_numbers)
            marked_lyrics.append(marked)
            logging.debug(marked)
        else:
            logging.debug("Found an empty section")
    logging.debug(rhyme_num_list)

    return rhyme_num_list, marked_lyrics

def parse_and_analyze_lyrics(lyrics=None,cmd=False,args=None,genius=True) -> dict:
    """
    Parses and analyzes song lyrics for rhymes
    Command Line:
        -t Accepts a text file with the lyrics of a single song, copied from Genius.com
        (Used for Debugging and Development)
        -j Accepts Artist JSON Object created by the LyricsGenius library, obtained by 
        using buildDB.py
        Use to build a local database of song lyrics for personal data analysis or project contribution

    Function Call:
        Accepts a lyrics string using the 'lyrics' argument, returns rhyme numbers and marked lyrics
        Used by buildDB.py to create our MongoDB database 
    """
    colors_for_html = []
    marked_lyrics = []
    json_out = {}
    if cmd:
        #this function was run from command line 
        #-t for .txt of lyrics copied from Genius.com
        #-j for json generated from lyricsGenius
        file = ""
        if args[1] == '-j':
            fp = open(args[2],'r')
            jp = json.load(fp)
            db = jp['Database']
            for artist in db:
                print(f"Loaded {len(artist['songs'])} songs by {artist['name']}")
                print('Parsing...')
                json_out['artist'] = artist['name']
                json_out['songs'] = []
                for song in artist['songs']:
                    parsed = parse_lyrics(song['lyrics'])
                    rhyme_num_list, marked_lyrics = analyze_lyrics(parse)

                    db[artist] = {
                        "song" : song['song'], 
                        "album" : song['album'],
                        "lyrics" : song['lyrics'], 
                        "rhyme" : rhyme_num_list,
                        "marked" : marked_lyrics 
                        }
                
                fp.close()
                out = open(f"{artist['name']}_analyzed.json",'w')
                json.dump(json_out,out)
                out.close()
            return json_out
        elif args[1] == '-t':
            lyrics = open(args[2],'r').read()
            print("Loaded Lyrics from Text File")
            parsed = parse_lyrics(lyrics)
            rhyme_num_list, marked_lyrics = analyze_lyrics(parse)
            with open(f'{args[2][:4]}_analyzed.txt') as fp:
                json.dump(
                    {"filename" : args[2], 
                    "lyrics": lyrics, 
                    "marked" : marked_lyrics, 
                    "rhymenum" : rhyme_num_list}
                )

        else:
            print("USAGE: python3 analyzeSong.py [-t][-j] FILENAME \n\n \
    -t : .txt file of lyrics copied from Genius.com \n \
    OR \n \
    -j : .json generated from BuildDB.py")
            return -1
    else:
        songlyrics = parse_lyrics(lyrics)
        rhyme_num, marked = analyze_lyrics(songlyrics)
        
    
   
    # print(marked)
    return rhyme_num,marked


if __name__ == "__main__":
    parse_and_analyze_lyrics(cmd=True,args=sys.argv)

