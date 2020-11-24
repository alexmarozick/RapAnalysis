# RapAnalysis

## About
Rap Analysis website (RAW) visualizes the way that a rapper rhymes in a given song by color coding groups of words that rhyme. Simply search a song on the homepage or log in with Spotify to analyze your favorite Hip-Hop playlist and recently listened songs. Your searches query our custom database of analyzed lyrics of over ___ artists. Can't find your favorite song or artist? Check back soon! We will adding the ability to add new songs to our database on the fly in a coming update! 

Noteable examples: 
    Clout Cobain by Denzel Curry
    Sirens by Denzel Curry
    Tragedy by RZA
    DNA by Kendrik Lamar
    Stan by Eminem
    Gin and Juice by Snoop Dogg
    I Think by Tyler The Creator

Lyrics are captured one verse or chorus at a time, allowing RAW to consider both internal and end rhymes while eliminating false positives occurring throughout a verse no matter their position within a given line.


## Approach 

### Obtaining Lyrics
We used the [LyricsGenius](https://github.com/johnwmillr/LyricsGenius) python library to collect lyrics for over 100 artists. This library runs on a combination of the official Genius API and web-scraping tools. Due to Intellectual Property law and licensing, we cannot provide this database for other developers looking to contribute to this project, however, we have provided the scripts which we used to build our database. More information on using these tools is available in our wiki [LINK ME BRO]

### Rhyme Detection    
English is a fickle language. For Example: through, rough, and trough share the same '-ough' ending despite being pronouced differently (/THro͞o/, /rəf/, /trôf/). This presents an interesting problem as rhymes cannot be detected via spelling alone. Moreover, rappers frequently coerse pronounciations to force rhymes where they would not normally occur. 

To account for these problems, we break words down into a list of phonemes (phonetic syllables which describe how a word is prnounced) using the Python Natual Language Toolkit and the CMU Pronouncing Dictionary (CMUDict) which contains 39 phonemes and three levels of syllabic stress. For example, `Cheese` -> `CH IY Z`. We compare the ending phonemes of words to look for rhymes and address pronounciation coersion in two ways: 

1. Multiple Word Prounounciations

    CMUDict contains multiple pronounciations for many words. For Example, we catch a rhyme between `"Business"` and `"Witness"` by comparing two pronounciations of `"Business"` ( `B IH1 Z N AH0 S` and `B IH1 Z N IH0 S`) with the single pronounciation of `"Witness"` (`W IH1 T N AH0 S`) 

2. Rebuilding Truncated Stuffixes

    Many rappers use a truncated suffix, ending present participle `-ing` words with `in'`

            Dodgin' bullets, reapin' what you sow
            And stackin' up the footage, livin' on the go
    `Dodgin` and `Reapin` are not official words listed in the CMUDict, so we rebuild these suffixes to `Dodging` and `Reaping` to catch rhymes between words of this form and words with a complete `ing` ending

    Note: For words that are not in the CMUDict, direct string equality is used. 
  
Our algorithm considers one verse or chorus at a time to mitigate false positives derived from rhymes detected across sections. In a given section, our algorithm operates as follows:

    rhymeNumber = 0
    for A in section: 
        for B in section[index of A onward]:
            if A rhymes with B: 
                Mark A with rhymeNumber
                Mark All instances of B with RhymeNumber
                RhymeNumber++

We generate a list of RhymeNumbers with a 1-1 correspondence with the lyrics of a given song which is stored in our database. The Rhyme Number of a word is used to determine the color it is ascribed in on the YFM WebService. 
<!-- TODO: DEFINE RHYME NUMBER MORE CLEARLY -->

### Spotify Integration
In addition to viewing one song at a time by searching on the YFM Homepage, users can log in with their Spotify account to grant YFM access to their playlists and recently listened songs. Users can then select a playlist  or number of recently listened songs they wish to analyze. Highlighted Lyrics are presented to the user with a dropdown menu to switch between songs.  


### Highlighting Lyrics:
A word's Rhyme Number is used to determine the color of its highlight: A word's rhyme number is mapped to an HSL hue value, a multiple of 10 ranging from 0 to 360. The luminance value of a rhyme given Rhyme Number alternates between a light and dark value to provide further differentiation between rhyme sets.   

A rhyme number of -1 corresponds to no highlighting.  
<!-- TODO: DESCRIBE MORE CLEARLY HOW HIGHLIGHTING WORKS  -->
### Hosting Lyrics and rhyming information
Web-scraping lyrics using LyricsGenius proved too inefficient to rely on for realtime analysis of more than one song at a time. We opted to build a MongDB database of over 100 artists (most of which had 100-300 songs), their lyrics, and their rhyme information in the following format: 

    {Database: 
        {'artist1' : [
                    {'song1': "songName" , 'lyrics' : "lyrics go here", 'rhyme' [[List of Rhyme Numbers]]}
                    {'song2': "songName" , 'lyrics' : "lyrics go here", 'rhyme' [[List of Rhyme Numbers]]}
                    ]
        }
        {'artist2' : [
                    {'song1': "songName" , 'lyrics' : "lyrics go here", 'rhyme' [[List of Rhyme Numbers]]}
                    {'song2': "songName" , 'lyrics' : "lyrics go here", 'rhyme' [[List of Rhyme Numbers]]}
                    ]
        }
    }

Artist and song names were made lowercase and stripped of any special characters. ('.' replaced with '' and '$' replaced with 's' to conform to MongoDB restrictions)
MongoDB's Text indexing to allows users to search our database in a case-insensitive manner.




### Next Steps 
1. Using Rhyme Information to generate Statistics: <br>
    We intend to calculate statistics for artists based on rhyming such as their average amount of unique rhymes per song. This information will be merged with the present Spotify page to allow a user to compare artists on their favorites list

2. Improving Rhyme Detection <br>
   Put a lil' bit of AI and ML in there and this thing'll be flyin'! 👍
   ![](http://www.google.com/url?sa=i&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FThumb_signal&psig=AOvVaw3hEzRyc5f1LGUDsdRAoVvZ&ust=1606194084787000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCLD_k7Hxl-0CFQAAAAAdAAAAABAD)
   
