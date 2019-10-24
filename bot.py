import os
import discord
import asyncio
import time
import pathlib



SONG_FOLDER="songs"


if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

print("Opus loaded")

client = discord.Client()

#Define a cooldown class

class Cooldown:
    
    time = 0
    id = 0
    
    def __init__(self, idIn):

        #Implemet cooldown blacklist

        id = idIn
        time = time.time()

    def cooldownExpired(self):

        if time.time() - time > 300:
            return True
        else:
            return False

#Utilty functions

def songExists(id):
   
    id = "song-" + str(id)

    for i in os.listdir(SONG_FOLDER):
        path = pathlib.Path("songs/" + i)
        print(path.stem)
        if path.stem == str(id):
            return True
      

    return False

def handleCooldown(id):
    return 1 #NOT IMPlEMENTED YET

#Event handlers
@client.event
async def on_ready():
    print("logged in as " + client.user.name)
    print("id" + str(client.user.id))


@client.event
async def on_voice_state_update(member, before, after):
    
    print(str(member.display_name) + " changed voice state")

    #Begin logic checks to determine what to do

    #if we are no longer in a channel, then bot does not do anything
    if after.channel == None:
        return None

    #if we were in a channel before, then we switched channel, and don't need to do anything

    if before.channel != None:
        return None

    #Now that we have joined the channel, we must check if we have a song to play for this user

    if not songExists(member.id):
        return None

    #We have a song, but are we out of cooldown

    if handleCooldown(member.id) == False:
        return None
    
    #Okay, we now know we can play the song
    
    voiceClient = await after.channel.connect()

    audioPlayer = voiceClient.create_ffmpeg_player('songs/songs' + str(member.id))

    audioPlayer.start()

    while not auidoPlayer.is_done():
        pass

    await voiceClient.disconnect()

    #FUTURE, WHAT IF MULTIPLE CHANNELS EXPERINCE A JOIN ACROSS ONE GUILD?


client.run(os.environ.get('BOTTOKEN'))
