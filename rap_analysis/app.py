'''
Juno Mayer, Alex Marozick and Abduarraheem Elfandi

'''

from flask import Flask, render_template, url_for, request, redirect, abort, flash, jsonify, session, make_response
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException, default_exceptions, Aborter
import pprint
import requests
import json
import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class FileTypeException(HTTPException):   # this error is thrown when the file type is incorrect
    code = 400
    description = 'Error: File Type Incorrect!'

default_exceptions[400] = FileTypeException
abort = Aborter()


app = Flask(__name__)
# app.config['UPLOAD_PATH'] = 'TestFiles'
# app.config['UPLOAD_EXTENSIONS'] = ['.gpx', '.xml'] # can add other file types in the list
secret_key = os.urandom(24)
app.secret_key = secret_key




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect("/spotifyLogin")
    return render_template("index.html")

client_id = '9abfe52d27b7448abe084a11ea04ca7b'
client_secret = '3b7c548da5b44417b25e10ef5143b481'
token_url = 'https://accounts.spotify.com/api/token'

REDIRECT_URI = "http://127.0.0.1:5000/spotifyRequest"


# Authorization Code Flow Step 1
@app.route("/spotifyLogin")
def spotifyLogin():
    '''
        User login to spotify for app authoriztion.
        A GET request is sent to the /authorize endpoint of spotify,
        after loggging the Spotify Accounts service presents details of the scopes for which access is being sought.
        After they accept or decline the user is redirected to the given redirect_uri.
    '''
    print("Entered spotifyLogin")
    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, scope="user-read-private")
    auth_url = sp_oauth.get_authorize_url()
    print(f'/spotifyLogin authorizeurl: {auth_url}')
    print("Leaving spotifyLogin")
    return redirect(auth_url)

# Authorization Code Flow Step 2
@app.route("/spotifyRequest")
def spotifyRequest():
    print("Entered spotifyRequest")

    sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI, scope="user-read-private")
    session.clear()
    auth_code = request.args.get('code')
    sp_token = sp_oauth.get_access_token(auth_code)
    print(f'Code: {auth_code} Token: {sp_token}')
    session["spotify-token"] = sp_token
    
    print("Leaving spotifyRequest")
    return redirect("/")

@app.route('/unknown')
def give_data(): 
    return jsonify({})

@app.route('/spotify')
def spotify():
    return render_template("spotify.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def page_forbidden(e):
    return render_template("403.html"), 403



if __name__ == "__main__":
    app.run(debug=True)