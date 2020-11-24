'''
Configuration code based on Prof Michal Young's Example: 
https://github.com/MichalYoung/Enroute/blob/master/config.py
'''
import os 
import configparser
import logging


CONFIG_FILE1 = 'rap_analysis/config.ini'
CONFIG_FILE2 = 'config.ini'
config_files = [CONFIG_FILE1,CONFIG_FILE2]

typedict = {'api': 'APIKEYS', 'uri': 'REDIRECT_URI', "MONGODB" : "MONGODB"}

config_key = ['Spotify','Genius']

config_dict = {}

config = configparser.ConfigParser()
have_file = False 
for item in config_files:
    if os.path.exists(item):
        logging.info(f"Found a config file, loading from {item}... ")
        have_file = True
        config.read(item)


def get(key : str,keytype : str):
    '''
    Gets a value from the config file
    In this case, its only really the Mapbox API key 
    We check OS evironment variables first so that devs can put keys in 
    hosting service's config vars intead of supply an ini file
    '''
    t = typedict[keytype]

    if key in os.environ:
        val = os.environ[key]
    elif have_file:
        val = config[t][key]
    else:
        raise NameError(f"{key} is not a valid config -- not found in file")


    return val