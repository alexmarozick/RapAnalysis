SHELL := /bin/bash

default: rebuild

install: rebuild

rebuild: env 

run:
	(source env/bin/activate; gunicorn app:app)

env:    requirements.txt
	(python3 -mvenv env; \
	source ./env/bin/activate; \
	pip3 install -r requirements.txt)

clean:
	rm -rf env
