#A wrapper file for audio handling in the website section of the ThemeSongBot

from mutagen.mp3 import MP3;
from pydub import AudioSegment;
import os

import constants


#A helper method to find the file extension and filename file
def get_extension(filename)
    output = filename.rsplit('.',1)
    return output[0], output[1]


#This is a method that will peform audio normilization on a file, it seperate to allow being spin off in a different thread so we don't stall returning the webpage
#Filename should be actual on disk, output should not have an extension either
def normalize_audio(filename, output=None):
    sound = AudioSegment.from_file(filename, "mp3")
    change_in_dbfs = constants.TARGET_AUDIO_DBFS - sound.dBFS
    normal_sound = sound.apply_gain(change_in_dbfs)

    if(output == None):
        os.remove(filename)
        output = filename
    

    normal_sound.export(filename, format="mp3")
    return (output + ".mp3")

#In order to handle multiple formats, we are going to convert to mp3 from any input audio files.
#This should be able to handle a lot more formats than the one's coming in, but we will limit earlier
#File name should be an on disk, output should not have an extension
def convert_to_mp3(filename, output=None):
    stripped_name, extension = get_extension(filename)
  
    if(output==None):
        os.remove(filename)
        output = stripped_name

    input_audio = Audio_Segment.from_file(filename, get_extension(extension)) 
    input_audio = Audio_Segment.export(output,format="mp3")

    return (output + ".mp3")


#This method will get the length of a file on disk
