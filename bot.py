import os
import discord
import asyncio
import time
import pathlib
import constants
import threading

#Load the sound library
if not discord.opus.is_loaded():
 discord.opus.load_opus('libopus.so');

#declare our discord client
client = discord.Client()

#___HELPER FUNCTIONS____
def song_exists(id):
    filename = "song-" + str(id)
    return os.path.exists(os.path.join(constants.UPLOAD_FOLDER,filename)+".mp3")
def get_song_name(id):
    return os.path.join(constants.UPLOAD_FOLDER,"song-" + str(id))+".mp3"

#___COOLDOWN FUNCTIONS___
users_in_cooldown = {}
cooldown_lock = False
def update_user_cooldown(id):
    if str(id) not in users_in_cooldown:
        users_in_cooldown[str(id)] = constants.START_COOLDOWN
    elif users_in_cooldown[str(id)] == 0:
        users_in_cooldown[str(id)] = constants.START_COOLDOWN
    else:
        users_in_cooldown[str(id)] = users_in_cooldown[str(id)] * constants.COOLDOWN_MULTPLIER
        if users_in_cooldown[str(id)] < constants.MIN_COOLDOWN :
                users_in_cooldown[str(id)] = constants.MIN_COOLDOWN

def update_all_cooldowns():
    for id, cooldown in users_in_cooldown.items():
        if cooldown > 0:
            print("Cooldown for user " + id + " is " + str(cooldown - 1))
            users_in_cooldown[id] = cooldown - 1

def cooldown_loop():
    while True:
        time.sleep(1)
        cooldown_lock = True
        update_all_cooldowns()
        cooldown_lock = False

def get_cooldown(id):
    if str(id) not in users_in_cooldown:
        return 0
    return users_in_cooldown[str(id)];

#___DISCORD EVENT HANDLERS____
@client.event
async def on_ready():
    print("Ready to go.")
    print("Logged in as " + client.user.name)

@client.event
async def on_voice_state_update(user, before, after):

    #If this was non channel update, then no purpose doing anything
    if before.channel == after.channel:
        return

    #If there is no song, there is no point doing all this logic
    if not song_exists(user.id):
        return 

    #await release of cooldown lock
    while cooldown_lock:
        pass

    #If the player is leaving a channel
    if after.channel == None:
        update_user_cooldown(user.id);
        return
     
    #if the player is entering a channel
    if before.channel == None and after.channel != None:
        if get_cooldown(user.id) != 0:
            print("Not playing song for user " + user.name + " becuase of cooldown")
            update_user_cooldown(user.id)
            return
        update_user_cooldown(user.id)

        print("Playing user song for " + user.name);

        voice_client = await after.channel.connect()
        voice_client.play(discord.FFmpegPCMAudio(get_song_name(user.id)))

        abort_time = 0
        while voice_client.is_playing() :
            time.sleep(0.1)
            abort_time += 0.1
            if(abort_time > constants.ALLOWED_LENGTH):
                print("Was forced to abort playing song for " + user.name)
                break

        await voice_client.disconnect()

    #if the player is switching channels, then we do nothing
    if before.channel != None and after.channel != None:
        pass

#__START COOLDOWN LOOP__
cooldown_thread = threading.Thread(target=cooldown_loop, args=(), daemon=True)
cooldown_thread.start()

#___RUN DISCORD CLIENT___
client.run(constants.BOT_TOKEN)

