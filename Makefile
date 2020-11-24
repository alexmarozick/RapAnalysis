SHELL := /bin/bash

default: rebuild

install: rebuild

rebuild: clean env lyricsgenius dict 

lyricsgenius: 
	(source env/bin/activate; pip install git+https://github.com/johnwmillr/LyricsGenius.git)

activate: 
	(env/bin/activate)

run:
	(source env/bin/activate; python3 rap_analysis/app.py)

dict: 
	(source env/bin/activate; python3 clcmudict.py)
	
env:    requirements.txt
	(python3 -mvenv env; \
	source ./env/bin/activate; \
	pip3 install -r requirements.txt)

clean:
	rm -rf env
