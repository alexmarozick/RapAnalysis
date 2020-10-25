'''
Juno Mayer, Alex Marozick and Abduarraheem Elfandi

'''

from flask import Flask, render_template, url_for, request, redirect, abort, flash, jsonify, session
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException, default_exceptions, Aborter
import pprint
import locationParse
import requests
import json
import config


class FileTypeException(HTTPException):   # this error is thrown when the file type is incorrect
    code = 400
    description = 'Error: File Type Incorrect!'

default_exceptions[400] = FileTypeException
abort = Aborter()

app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'TestFiles'
app.config['UPLOAD_EXTENSIONS'] = ['.gpx', '.xml'] # can add other file types in the list
secret_key = os.urandom(24)
app.secret_key = secret_key

mapbox_key = config.get('mapbox_key')

@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template("index.html"), 200

@app.route('/unknown')
def give_coords(): 
    #also give tehe mapbox key 
    return jsonify({})



@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def page_forbidden(e):
    return render_template("403.html"), 403



if __name__ == "__main__":
    app.run(debug=True)