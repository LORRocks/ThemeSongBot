import os
from flask import *
from requests_oauthlib import OAuth2Session
from mutagen.mp3 import MP3;
#import songHandler

#Import the various bot secret and tokens from the os enviromental variables, you need to set these
OAUTH2_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback' #This will need to be changed when the bot website is hosted
API_BASE_URL = os.environ.get('API_BASE_URI','https://discordapp.com/api')

#Store the urls for the bot
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

#Store the location of the upload folder and the allowed data type
UPLOAD_FOLDER="songs"
ALLOWED_EXTENSIONS = {'mp3'}
ALLOWED_LENGTH = 500 #max allowed length in seconds

#Initalize the flask app
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

#Check if we are using sls or not, set the appropriate settings
if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token

#Make a flask oauth session, so that it is persistent across sessions
def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,

        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id' : OAUTH2_CLIENT_ID,
            'client_secret' : OAUTH2_CLIENT_SECRET
        },

        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater
    )

#When the user goes to the home page, check if they have a o auth cookie or not, otherwise just return the standard template
@app.route('/')
def index():

    if('oauth2_token' in session):
        return redirect(url_for("me"))

    return render_template("index.html")

#This should send the user along the path of getting verified
@app.route('/verify')
def verify():
    scope = request.args.get(
        'scope',
        'identify')

    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state

    return redirect(authorization_url)

#This is where the user is sent back from the oauth
@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))

    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token

    return redirect(url_for('me'))

#This is the users page once they are oauthed
@app.route('/me')
def me():

    if('oauth2_token' not in session):
        return redirect(url_for("index"))

    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()

    #print(user)

    return render_template("user.html",height=4,username=user["username"])

#A helper method to check if the user is uploading an allowed file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#This is where we will send the songs to be uploaded and handled
@app.route('/upload', methods=["GET","POST"])
def upload():

    if('oauth2_token' not in session):
        return redirect(url_for("index"))

    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()

    if request.method == 'POST':
        if 'file' not in request.files:
            return "Something boinked"
        file = request.files["file"]
        if file.filename == '':
            return render_template("user.html",username=user["username"],height=10,extratext="Your song you choose had an empty filename, and was not saved.  ")
        if not allowed_file(file.filename):
            return render_template("user.html",username=user["username"],height=10,extratext="Your song was not an allowed file type, and was not saved. ")

        
        if file:
            filename = "song-" + user['id']
            file.save(os.path.join(UPLOAD_FOLDER, filename)+".mp3")

            #File length check
            fileCheck = MP3(os.path.join(UPLOAD_FOLDER, filename)+".mp3")
            if(fileCheck.info.length > ALLOWED_LENGTH):
                os.remove(os.path.join(UPLOAD_FOLDER, filename)+".mp3")
                return render_template("user.html",username=user["username"],height=10, extratext="Your song was too long, it was not saved. ")

            return render_template("user.html",username=user["username"],height=10, extratext="Your song was uploaded successfully. ")

    if request.method == "GET":
        redirect(url_for("me"))



if __name__ == '__main__':
    app.run()

