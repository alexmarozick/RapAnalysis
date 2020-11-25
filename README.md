# RapAnalysis

A Rhyme Detection analysis Framework and Webservice for Hip-Hop/Rap Lyrics 

## Installation and Usage Documentation
Want to contribute to the project? [Check out our Wiki for installation and usage instructions](https://github.com/alexmarozick/RapAnalysis/wiki)

Example Playlist for Testing our Spotify Integration:

    https://open.spotify.com/playlist/5SiGw4acTtJWGeAEZjsZHY?si=xr3wHmaSQnKhLPCF-CDRJQ
    https://open.spotify.com/playlist/5TZkls9cEOzWDR6qCxwDot?si=TT1T9favTGynYp0w7qUvIg

## About
Rap Analyzer visualizes the way that a rapper rhymes in a given song by color coding groups of words that rhyme. Simply search a song on the homepage or log in with Spotify to analyze your favorite Hip-Hop playlist and recently listened songs. Your searches query our custom database of analyzed lyrics of over 100 artists. 
   
## Approach 

### Obtaining Lyrics
We used the [LyricsGenius](https://github.com/johnwmillr/LyricsGenius) python library to collect lyrics for over 100 artists. This library runs on a combination of the official Genius API and web-scraping tools. Due to Intellectual Property law and licensing, we cannot provide this database for other developers looking to contribute to this project, however, we have provided the scripts which we used to build our database. More information on using these tools is available in [our wiki](https://github.com/alexmarozick/RapAnalysis/wiki)

### Rhyme Detection    
English is a fickle language. For Example: through, rough, and trough share the same '-ough' ending despite being pronounced differently (/THro͞o/, /rəf/, /trôf/). This presents an interesting problem as rhymes cannot be detected via spelling alone. Moreover, rappers frequently coerce pronunciations to force rhymes where they would not normally occur. 

To account for these problems, we break words down into a list of phonemes (phonetic syllables which describe how a word is pronounced) using the Python Natual Language Toolkit and the CMU Pronouncing Dictionary (CMUDict) which contains 39 phonemes and three levels of syllabic stress. For example, `Cheese` -> `CH IY Z`. We compare the ending phonemes of words to look for rhymes and address pronunciation coercion in two ways: 

1. Multiple Word Pronunciations

    CMUDict contains multiple pronunciations for many words. For Example, we catch a rhyme between `"Business"` and `"Witness"` by comparing two pronunciations of `"Business"` ( `B IH1 Z N AH0 S` and `B IH1 Z N IH0 S`) with the single pronunciations of `"Witness"` (`W IH1 T N AH0 S`) 

2. Rebuilding Truncated Suffixes

    Many rappers use a truncated suffix, ending present participle `-ing` words with `in'`

            Dodgin' bullets, reapin' what you sow
            And stackin' up the footage, livin' on the go
            
    `Dodgin` and `Reapin` are not official words listed in the CMUDict, so we rebuild these suffixes to `Dodging` and `Reaping` to catch rhymes between words of this form and words with a complete `ing` ending

    Note: For words that are not in the CMUDict, direct string equality is used. 
  
Our algorithm considers one verse or chorus at a time to mitigate false positives derived from rhymes detected across sections. In a given section, our algorithm operates as follows:
    
    rhymeNumberList = [-1] * Length of section
    rhymeNumber = 0
    for A in section: 
        for B in section[index of A onward]:
            if A rhymes with B: 
                Mark A with rhymeNumber
                Mark All instances of B with RhymeNumber
                rhymeNumbers[IndexOf(A)] = rhymeNumber
                RhymeNumber++

A section's rhyme information is stored as a list of rhyme numbers: word A and word B rhyme if `RhymeList[IndexOf(A)] == RhymeList[IndexOf(B)]`, We use rhyme numbers to determine which color to ascribe to a set of words on the Rap Analyzer Web service.


### Spotify Integration
In addition to viewing one song at a time by searching on the Rap Analyzer Homepage, users can log in with their Spotify account to grant Rap Analyzer access to their playlists and recently listened songs. Users can then select a playlist or number of recently listened songs they wish to analyze. Highlighted Lyrics are presented to the user with a dropdown menu to switch between songs.  


### Highlighting Lyrics:
A word's Rhyme Number is used to determine the color of its highlight: Words with the same rhyme number rhyme with each other and are given the same highlight color. A word's rhyme number is mapped to an HSL hue value from 0 to 360. To obtain a set of diverse highlighting colors. Rhyme Numbers and are mapped to hue values as follows: 
    
    Rhyme Number                             Hue
        [0,17]                [n * 10 for n in range(0,360) if n % 2 == 0]   (20,40,60,...360)         
        [18,36]               [n * 10 for n in range(0,360) if n % 2 != 0]   (10,30,50,...350)

The brightness value of a color alternates between a light and dark highlight to further differentiate sets of rhymes 

A rhyme number of -1 corresponds to no highlighting.  

### Hosting Lyrics and rhyming information
Web-scraping lyrics using LyricsGenius proved too inefficient to rely on for realtime analysis of more than one song at a time. We opted to build a MongDB database of over 100 artists (most of which had 100-300 songs), their lyrics, and their rhyme information in the following format: 

    {Database: 
        {'artist1' : [
                    {'song': "songName1" , 'lyrics' : "lyrics go here", 'rhyme' [[List of Rhyme Numbers]]}
                    {'song': "songName2" , 'lyrics' : "lyrics go here", 'rhyme' [[List of Rhyme Numbers]]}
                    ]
        }
        {'artist2' : [
                    {'song': "songName1" , 'lyrics' : "lyrics go here", 'rhyme' [[List of Rhyme Numbers]]}
                    {'song': "songName2" , 'lyrics' : "lyrics go here", 'rhyme' [[List of Rhyme Numbers]]}
                    ]
        }
    }

Artist and song names were made lowercase and stripped of any special characters. ('.' replaced with '' and '$' replaced with 's' to conform to MongoDB restrictions)
MongoDB's Text indexing to allows users to search our database in a case-insensitive manner.


### Next Steps 
1. Using Rhyme Information to generate Statistics: <br>
    We intend to calculate statistics for artists based on rhyming such as their average amount of unique rhymes per song. This information will be merged with the present Spotify page to allow a user to compare artists on their favorites list

2. Improving Rhyme Detection <br>
    There are many ways to improve our algorithm, including ignoring tense and plural word endings as rappers often coerce rhymes between present and past tense, or single and plural words. Furthermore, we could implement an algorithm that searches for common strings of vowels in words to detect multi-word rhyme schemes. Eventually, we want to apply Machine Learning models to rhyme detection to allow for the coverage of areas where our algorithm falls short. 
