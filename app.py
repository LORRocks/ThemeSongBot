import os
import threading

from pydub import AudioSegment
from requests_oauthlib import OAuth2Session

from flask import *
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import constants
import audio

#Initalize the flask app
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = constants.OAUTH2_CLIENT_SECRET

#Set up the rate limiter
limiter = Limiter(app, key_func=get_remote_address,  default_limits=["64 per day", "8 per hour"])

#Check if we are using sls or not, set the appropriate settings
if 'http://' in constants.OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


#----HELPER METHODS-----
#A helper method to check if the user is uploading an allowed file
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in constants.ALLOWED_EXTENSIONS
#A helper method to find the file extension of an uplaoded file
def get_extension(filename):
    return filename.rsplit('.',1)[1].lower()

#----FLASK SESSION METHODS-----
#Make a flask oauth session, so that it is persistent across sessions
def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=constants.OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,

        redirect_uri=constants.OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id' : constants.OAUTH2_CLIENT_ID,
            'client_secret' : constants.OAUTH2_CLIENT_SECRET
        },

        auto_refresh_url=constants.TOKEN_URL,
        token_updater=token_updater
    )
def token_updater(token):
    session['oauth_token'] = token
 
#---ALL THE ROUTE METHODS FOR FLASK

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
    authorization_url, state = discord.authorization_url(constants.AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state

    return redirect(authorization_url)

#This is where the user is sent back from the oauth
@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))

    token = discord.fetch_token(
        constants.TOKEN_URL,
        client_secret=constants.OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token

    return redirect(url_for('me'))

#This is the users page once they are oauthed
@app.route('/me')
def me():

    if('oauth2_token' not in session):
        return redirect(url_for("index"))

    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(constants.API_BASE_URL + '/users/@me').json()

    #check if the user currently has a song
    filename = "song-" + user["id"]
    file_exists = os.path.exists(os.path.join(constants.UPLOAD_FOLDER, filename)+".mp3");
   
    if(file_exists):
        return render_template("user.html",height=4,username=user["username"], extratext = "You currently have a theme song stored. ")
   
    return render_template("user.html",height=4,username=user["username"])



#This is where we will send the songs to be uploaded and handled
@app.route('/upload', methods=["GET","POST"])
def upload():

    if('oauth2_token' not in session):
        return redirect(url_for("index"))

    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(constants.API_BASE_URL + '/users/@me').json()

    if request.method == 'POST':
        #Perform a series of sanity checks on the file input
        if 'file' not in request.files:
            return "Something boinked"
        file = request.files["file"]
        if file.filename == '':
            return render_template("user.html",username=user["username"],height=10,extratext="Your song you choose had an empty filename, and was not saved.  ")
        if not allowed_file(file.filename):
            return render_template("user.html",username=user["username"],height=10,extratext="Your song was not an allowed file type, and was not saved. ")

        #Peform checks on the valid input file
        if file:
            #Get the extension and filename
            extension = get_extension(file.filename) 
            filename = "song-" + user['id']
           
            #Save the file to the upload folder, while we're performing all the actions on it
            filepath = os.path.join(constants.UPLOAD_FOLDER, filename+"."+extension)
            file.save(filepath)

            #File length check
            print(filepath)
            length = audio.get_audio_length(filepath)
            if length > constants.ALLOWED_LENGTH:
                os.remove(filepath)
                return render_template("user.html",username=user["username"],height=10,extratext="Your song was too long and was not saved. ")

            print(filepath)
            #If needed, convert to our mp3 forma
            if not extension == "mp3":
                filepath = audio.convert_to_mp3(filepath)                                  

            #Peform the audio normal
            filepath = audio.normalize_audio(filepath)

            #Move the song to the db folder, clear up the upload folder
            sound_input = AudioSegment.from_file(filepath)
            sound_input.export(os.path.join(constants.DB_FOLDER,filename+".mp3"),format="mp3")
            os.remove(filepath)

            #Signal success
            return render_template("user.html",username=user["username"],height=10, extratext="Your song was uploaded successfully. ")

    if request.method == "GET": #we should never get to this page, it only acts as a REST endpoint for uploading files
        redirect(url_for("me"))


#---SETUP
#run the flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)

