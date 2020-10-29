'''
Juno Mayer, Alex Marozick and Abduarraheem Elfandi
'''

from flask import Flask, render_template, url_for, request, redirect, abort, flash, jsonify, session, make_response
from flask_session import Session
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException, default_exceptions, Aborter
import pprint
import requests
import json
import config
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
import uuid
import lyricsgenius




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

client_id = 'Insert spotify client id' # NOTE hey do this
client_secret = 'Insert spotify client secret' # NOTE hey do this
token_url = 'https://accounts.spotify.com/api/token'

# NOTE Make sure this is also the same in your Spotify app.
REDIRECT_URI = "http://127.0.0.1:5000/spotifyRequest"

# All the cached spotify data will be in this folder
# but will be deleted as soon as the user signsout/session ends.
caches_folder = '.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)
    

def session_cache_path():

    '''
    Function that returns the session cached path (basically the cache folder).
    '''

    print("Starting session_cache_path")        # for debugging
    print(caches_folder)                        # for debugging
    print(session.get('uuid'))                  # for debugging
    print("Finished session_cache_path")        # for debugging
    return caches_folder + session.get('uuid')


@app.route('/')
def index():

    # global session_counter # used for debugging
    # If a new user joins give random id to the user.
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())
        # session_counter +=1 # for debugging
        # print(f"Session counter: {session_counter}\n Session id: {session['uuid']}") # for debugging


    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, 
                            scope="user-read-private", cache_path=session_cache_path(), show_dialog=True)
    
    display = "Login to Spotify"
    if sp_oauth.get_cached_token(): # FIXME this causes a warning, easy fix, leave this to me - Abduarraheem
        # Authorization Code Flow Step 3 
        # NOTE here we can get data from the Spotify API.
        spotify = spotipy.Spotify(auth_manager=sp_oauth)
        display = "User: " + spotify.me()["display_name"] + " (Sign Out)"
    return render_template("index.html", display=display)


#TODO basically put whatever is in the index function in here, leave this to me - Abduarraheem
@app.route('/spotify')
def spotify():
    return render_template("spotify.html")



@app.route('/login-btn', methods=['GET', 'POST'])    
def login():
    if request.method == 'POST':
        
        sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, 
                                scope="user-read-private", cache_path=session_cache_path(), show_dialog=True)
        
        # So if we have a token(which means we are logged in) 
        # and the login button is clicked then we need to sign out
        # TODO change naming conenetions to make this less confusing - Abduarraheem

        if not sp_oauth.get_cached_token():
            return redirect("/spotifyLogin")
        return redirect("/sign_out")


# Could put this in the login-btn route instead.
# Authorization Code Flow Step 1
@app.route("/spotifyLogin", methods=['GET', 'POST'])
def spotifyLogin():
    '''
        User login to spotify for app authoriztion.
        A GET request is sent to the /authorize endpoint of spotify,
        after loggging the Spotify Accounts service presents details of the scopes for which access is being sought.
        After they accept or decline the user is redirected to the given redirect_uri,
        in this case our redirect_uri redirects to /spotifyRequest where
        the token is gotten from.
    '''


    print("Entered spotifyLogin")                       # for debugging
    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri= REDIRECT_URI, scope="user-read-private", cache_path=session_cache_path(), show_dialog=True)
    auth_url = sp_oauth.get_authorize_url()
    print(f'/spotifyLogin authorizeurl: {auth_url}')    # for debugging
    print("Leaving spotifyLogin")                       # for debugging
    return redirect(auth_url)



# Authorization Code Flow Step 2
@app.route("/spotifyRequest")
def spotifyRequest():
    '''
    Post request which returns the access and refresh token.
    '''
    print("Entered spotifyRequest")

    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, 
                            scope="user-read-private", cache_path=session_cache_path(), show_dialog=True)
    
    # session.clear()
    auth_code = request.args.get('code')                # get the code from the url.
    sp_token = sp_oauth.get_access_token(auth_code)     # use that code to get a token
    print(f'Code: {auth_code} Token: {sp_token}')       # for debugging
    session["spotify-token"] = sp_token                 # store token into the sessio, NOTE this might not be needed anymore because of how we store the session into the cache
    print("Leaving spotifyRequest")                     # for debugging
    return redirect("/")


@app.route('/sign_out')
def sign_out():

    # Remove the cached path when a user signs out and also clear the session
    os.remove(session_cache_path())
    
    # session.clear() # NOTE this causes a bug where the session id will be removed.
    try:
        os.remove(session_cache_path())
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/get-lyrics', methods=['POST'])
def get_lyrics():
    if request.method == "POST":
        print("Starting POST get-lyrics")                       # for debugging
        req = request.form
        song_name = req.get("song")
        artist_name = req.get("artist")
        print(song_name)                                        # for debugging
        print(artist_name)                                      # for debugging
        genius = lyricsgenius.Genius('Client Access Token')     # NOTE get client access token here https://genius.com/api-clients
        # artist = genius.search_artist(artist_name,max_songs=3)
        # print(artist)
        song = genius.search_song(song_name, artist_name)
        print(song.lyrics)                                      # for debugging
        print("Finished POST get-lyrics")                       # for debugging
        return redirect('/')


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