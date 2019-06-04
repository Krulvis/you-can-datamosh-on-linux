import argparse
import os
import sys
import subprocess

from mosh import MoshProfile, Mosher

input_video = "1.webm"
fps = 25
output_width = 720
start_sec = 0
end_sec = 0


# this makes sure the video file exists. It is used below in the 'input_video' argparse
def quit_if_no_video_file(video_file):
    if not os.path.isfile(video_file):
        raise argparse.ArgumentTypeError("Couldn't find {}. You might want to check the file name??".format(video_file))
    else:
        return (video_file)


# make sure the output directory exists
def confirm_output_directory(output_directory):
    if not os.path.exists(output_directory): os.mkdir(output_directory)

    return (output_directory)


# this makes the options available at the command line for ease of use

# 'parser' is the name of our new parser which checks the variables we give it to make sure they will probably work
# or else offer helpful errors and tips to the user at the command line
parser = argparse.ArgumentParser()

parser.add_argument('input_video', type=quit_if_no_video_file, help="File to be moshed")

# this makes sure the local variables are up to date after all the argparsing
locals().update(parser.parse_args().__dict__.items())

# make sure ffmpeg is installed
try:
    # sends command line output to /dev/null when trying to open ffmpeg so it doesn't muck up our beautiful command line
    null = open("/dev/null", "w")
    # it tries to open ffmpeg
    subprocess.Popen("ffmpeg", stdout=null, stderr=null)
    # politely closes /dev/null
    null.close()

# if the OS can't find ffmpeg an error is printed and the program quits
except OSError:
    print("ffmpeg was not found. Please install it. Thanks.")
    sys.exit()

mosher = Mosher(input_video)

profiles = [MoshProfile(0, 5, 60), MoshProfile(2, 3, 60), MoshProfile(7, 10, 50), MoshProfile(19, 7, 100)]

mosher.mosh(profiles)

mosher.finish()
