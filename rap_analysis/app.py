'''
Juno Mayer, Alex Marozick and Abduarraheem Elfandi
'''

from flask import Flask, render_template, url_for, request, redirect, abort, flash, jsonify, session, make_response
from flask_session import Session
from pprint import pprint as pp
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException, default_exceptions, Aborter
from spotipy.oauth2 import SpotifyOAuth
from buildDB import get_lyrics
import os
import pprint
import requests
import json
import config
import spotipy
import time
import uuid
import lyricsgenius
import logging
import analyzeSong
import datetime
import spotifyData
import databaseops as dbops

# logging.basicConfig(level=app.logger.debug)
class FileTypeException(HTTPException):   # this error is thrown when the file type is incorrect
    code = 400
    description = 'Error: File Type Incorrect!'

default_exceptions[400] = FileTypeException
abort = Aborter()



session_counter = 0 # for debugging
app = Flask(__name__)
secret_key = os.urandom(64)
app.secret_key = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
scope = "user-read-private playlist-modify-private playlist-modify-public playlist-read-private user-follow-read user-read-recently-played"
client_id = config.get('SPOTIPY_CLIENT_ID','api') # NOTE hey do this
client_secret = config.get('SPOTIPY_CLIENT_SECRET','api') # NOTE hey do this
token_url = 'https://accounts.spotify.com/api/token'

# NOTE Make sure this is also the same in your Spotify app.
REDIRECT_URI = config.get('SPOTIPY_REDIRECT_URI','uri')
GENIUS_ACCESS_TOKEN = config.get('GENIUS_CLIENT_ACCESS_TOKEN','api')
# All the cached spotify data will be in this folder
# but will be deleted as soon as the user signsout/session ends.
caches_folder = '.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)
    

def session_cache_path():

    '''
    Function that returns the session cached path (basically the cache folder).
    '''

    app.logger.debug("Starting session_cache_path")        # for debugging
    app.logger.debug(caches_folder)                        # for debugging
    app.logger.debug(session.get('uuid'))                  # for debugging
    app.logger.debug("Finished session_cache_path")        # for debugging
    return caches_folder + session.get('uuid')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/_analyzeSpotify')
def analyzeSpotify():
    print(request.args)
    analyzeType = request.args.get('type')
    # print(playlist)
    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, 
                            scope=scope, cache_path=session_cache_path(), show_dialog=True)
    spotify = spotipy.Spotify(auth_manager=sp_oauth)
    songs = []
    if analyzeType == 'playlist':
        playlistID = request.args.get('playlistID')
        songs = dbops.getsongdata(spotifyData.get_songs_from_playlist(spotify, playlistID))
    elif analyzeType == 'recent':
        recent_num = int(request.args.get('recent_num'))
        # print(recent_num)
        # dbops.getsongdata(spotifyData.get_recent_plays(spotify, recent_num))
        songs = dbops.getsongdata(spotifyData.get_recent_plays(spotify, recent_num))
    return jsonify(result=songs)





@app.route('/spotify_login')
def spotify_login():
    # global session_counter # used for debugging
    # If a new user joins give random id to the user.
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())
        # session_counter +=1 # for debugging
        # print(f"Session counter: {session_counter}\n Session id: {session['uuid']}") # for debugging


    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, 
                            scope=scope, cache_path=session_cache_path(), show_dialog=True)
    
    # Authorization Code Flow Step 2
    if request.args.get('code'):
        auth_code = request.args.get('code')                        # get the code from the url.
        sp_token = sp_oauth.get_access_token(auth_code)             # use that code to get a token
        return redirect("/spotify_login")


    display = "Login to Spotify"
    if sp_oauth.get_cached_token():
        # Authorization Code Flow Step 3 
        # NOTE here we can get data from the Spotify API.
        spotify = spotipy.Spotify(auth_manager=sp_oauth)
        display = "User: " + spotify.me()["display_name"] + " (Sign Out)"
        spotify_data = spotifyData.spotify_data(spotify)
        pp(spotify_data)
        return render_template("spotify.html", display=display, artists=spotify_data["artists"], playlists=spotify_data["playlists"])
    return render_template("spotify_login.html", display=display)


@app.route('/login-btn', methods=['GET', 'POST'])    
def login():
    if request.method == 'POST':
        
        sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, 
                                scope=scope, cache_path=session_cache_path(), show_dialog=True)
        
        # So if we have a token(which means we are logged in) 
        # and the login button is clicked then we need to sign out

        if not sp_oauth.get_cached_token():
            # Authorization Code Flow Step 1
            auth_url = sp_oauth.get_authorize_url()
            return redirect(auth_url)
        return redirect("/sign_out")
    return redirect("spotify_login")



@app.route('/sign_out')
def sign_out():
    try:
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

@app.route('/user-lyrics')
def analyze_user_lyrics():
    print("GOT INTO USER LYRICS")
    lyrics = request.args.get('textboxid')
    print(lyrics)
    return jsonify(result=lyrics)



@app.route('/get-lyrics')
def get_input():
    
    song_name = request.args.get('songid')
    artist_name = request.args.get('artistid')

    print(song_name)
    print(artist_name)
    # song_name = song_name.lower()
    # artist_name = artist_name.lower()
    app.logger.debug(song_name)                                        # for debugging
    app.logger.debug(artist_name)                                      # for debugging        
    # TODO whatever is returned by get_lyrics, we have to return it in the format below so we can access it in the html page and display it
    #search mongodb database for the lyrics/colors/stats of song by artist 
    #if atrist, calc averages
        # for song in songs:
            # total num rhymes 

    #avg = num rhymes / num words

    proc_lyrics = []
    proc_colors = []
    highlighted = ""
    # pass in a dictionary to display and highlight in form {"song": song_name, "artist" : artist_name}
    songdata = dbops.getsongdata([{'song': song_name, 'artist': artist_name}])
    for item in songdata:
        for i in item:
             if song_name.lower() in i['song'].lower():
                proc_lyrics = i['lyrics']  # string
                proc_colors = i['colors']  # list of lists


        # if song_name.lower() in item[0]['song'].lower():
        #     print(item['song'])
    # proc_lyrics = songdata[0]['lyrics']  # string
    # proc_colors = songdata[0][0]['colors']  # list of lists
    print(proc_lyrics)
    print(proc_colors)
    # split the lyrics into a list of lists
    split_newl = proc_lyrics.replace('\n', '\n ').split(' ')
    # split_newl = [word for word in split_newl if '[' not in word and ']' not in word]
    # split_newl =  [word for word in split_newl if word is not '']
    colorlist = []
    for l in proc_colors:
        for color in l: 
            colorlist.append(color)
    print(len(split_newl))
    print(len(colorlist))
    size = len(split_newl)

    #skip = false 
    # if '[' in word 
        # skip = true 
    # if ']' in word 
        # skip = false
    return highlight_words(split_newl,colorlist)


def highlight_words(lyrics : str, colorlist : list):
    """
    Applies a list of colors to a list of lyrics 
    """
    highlighted = ""
    coloritr = 0
    for idx, word in enumerate(lyrics):
        if '[' in word: 
            skip = True

        if ']' in word: 
            skip = False
            continue
        try:
            if not skip or word == '\n' or word == '"':
                highlightword = '<mark style=\"background: #' + str(hex(colorlist[coloritr]))[2:] + ';\">' + word + "</mark> "
                if '\n' in word:
                    highlightword += '<br>'
                    word.replace('\n','<br>')
                if colorlist[coloritr] != 0:
                    highlighted += highlightword
                else: 
                    highlighted += word + " "
                coloritr +=1
            


        except:
            print(f"OVERFLOW at word {idx} out of {len(lyrics)}-- here's whats left") 
            print(lyrics[idx:])
            print(highlighted)
            return jsonify(result=highlighted)
        
    # if not skip
    print(split_newl)
    return jsonify(result=highlighted)



    #get indicies of all instances of empty string (these are blank lines inbetween sections)
    # idx_list = [idx + 1 for idx, val in enumerate(split_newl) if '[' in val ] 
    # #generate new list seperated by sections 
    # sections = [split_newl[i: j] for i, j in zip([0] + idx_list, idx_list + ([size] if idx_list[-1] != size else []))] 
    
    # for idx, section in enumerate(sections):
    #     words = []
    #     for line in section:
    #         for word in line.split(" "):
    #             if len(line.split(" ")) == 1 and '[' in word:
    #                 continue
    #             else:
    #                 words.append(word)
    #     print(words)
    #     print(len(words))
    #     print(proc_colors[idx])
    #     print(len(proc_colors[idx]))
    # # sections : [section][line][word]
    # # proc_colors : [section][word]
    # # generate the highlighted string

    # # AAAAA AAA AAAAAA AAAA 
    # # BBBBB BBBB BBBB BB 
    # # CCCC CC CCCCC 

    # highlighted = ""
    # print(f"number of sections in proc colors {len(proc_colors)}")
    # print(f"num sections {len(sections)}")
    # # print(proc_colors)
    # empties = 0
    # for idx, section in enumerate(sections): 
    # #for section in range(len(sections)):
    #     coloritr = 0
    #     print(f"number of colors in section {len(proc_colors[idx])}")
    #     for line in section:
    #     #for line in range(len(sections[section])):
    #         for word in line.split():
    #         #for word in range(len(sections[section][line])):
    #             try:
    #                 if proc_colors[idx][coloritr] != 0:
    #                     highlighted += '<mark style=\"background: #' + str(proc_colors[idx][coloritr]) + ';\">' + word + "</mark> "
    #                 else: 
    #                     highlighted += word + " "

    #                 if coloritr < len(proc_colors[idx]) - 1:
    #                     coloritr += 1
    #             except:
    #                 print(f"stopped in section {idx}")
    #                 print(section)
    #                 print(line)
    #                 print(word)
    #                 return jsonify(result=highlighted)

    #         highlighted += '\n'
                
    # lyricstext.innerHTML = highlighted
    # document.getElementById("result").innerHTML = highlighted;

    # print("\n\n Highlighting done")
    # print(highlighted)
    
 


@app.route('/unknown')
def give_data(): 
    return jsonify({})



@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def page_forbidden(e):
    return render_template("403.html"), 403


if __name__ == "__main__":
    app.run(debug=True)



#dont color brackets -- skip if they have []
# this shouldnt create an offset 

# place newlines after bracket 
