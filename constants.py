import os

#Import the config selected
CONFIG_SELECTED = os.environ['ENVIROMENT'] #either DEV or PRODUCTION
if CONFIG_SELECTED != "DEV" and CONFIG_SELECTED != "PRODUCTION":
    print("No correct config selected, ENVIROMENT should either be DEV or PRODUCTION")

#Import the various bot secret and tokens from the os enviromental variables, you need to set these
OAUTH2_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']

if CONFIG_SELECTED == "PRODUCTION":
    OAUTH2_REDIRECT_URI = 'http://teandfriends.rocks:5000/callback'
if CONFIG_SELECTED == "DEV":
    OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

#Store the urls for the bot
API_BASE_URL = os.environ.get('API_BASE_URI','https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

#Store the location of the upload folder,db folder and the allowed data type
UPLOAD_FOLDER="upload"
DB_FOLDER="songs"
ALLOWED_EXTENSIONS = {'mp3','ogg','wav'}
ALLOWED_LENGTH = 3 #max allowed length in seconds
TARGET_AUDIO_DBFS = -33 #the audio target in dbfs

#Store the bot token
BOT_TOKEN = os.environ['BOT_TOKEN']

#Bot cooldown info
START_COOLDOWN = 5 #in seconds
MIN_COOLDOWN = 5
COOLDOWN_MULTPLIER = 2
MAX_COOLDOWN = 40

if CONFIG_SELECTED == "DEV":
    COOLDOWN_MULTIPLIER = 0

