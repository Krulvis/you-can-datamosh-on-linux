# where we make new file names
# basename seperates the file name from the directory it's in so /home/user/you/video.mp4 becomes video.mp4
# splitext short for "split extension" splits video.mp4 into a list ['video','.mp4'] and [0] returns 'video' to file_name
import subprocess

# 0x0001B0 signals the beginning of an i-frame. Additional info: 0x0001B6 signals a p-frame
iframe = bytes.fromhex('0001B0')
pframe = bytes.fromhex('0001B6')


def get_frames(input_video, input_avi, output_avi, fps, start_sec, end_sec):
    # convert original file to avi
    subprocess.call('ffmpeg -loglevel error -y -i ' + input_video + ' ' +
                    ' -crf 0 -pix_fmt yuv420p -r ' + str(fps) + ' ' +
                    ' -ss ' + str(start_sec) + ' -to ' + str(end_sec) + ' ' +
                    input_avi, shell=True)

    # open up the new files so we can read and write bytes to them
    in_file = open(input_avi, 'rb')
    out_file = open(output_avi, 'wb')

    # because we used 'rb' above when the file is read the output is in byte format instead of Unicode strings
    in_file_bytes = in_file.read()

    # 0x30306463 which is ASCII 00dc signals the end of a frame. '0x' is a common way to say that a number is in hexidecimal format.
    frames = in_file_bytes.split(bytes.fromhex('30306463'))

    return in_file, out_file, frames


def convert_to_mp4(output_avi, output_video, output_width, fps):
    # Convert avi to mp4. If you want a different format try changing the output variable's file extension
    # and commenting out the line that starts with -crf. If that doesn't work you'll be making friends with ffmpeg's many, many options.
    # It's normal for ffmpeg to complain a lot about malformed headers if it processes the end of a datamoshed avi.
    # The -t option specifies the duration of the final video and usually helps avoid the malformed headers at the end.
    subprocess.call('ffmpeg -loglevel error -y -i ' + output_avi + ' ' +
                    ' -crf 18 -pix_fmt yuv420p -vcodec libx264 -acodec aac -r ' + str(fps) + ' ' +
                    ' -vf "scale=' + str(output_width) + ':-2:flags=lanczos" ' + ' ' +
                    # ' -ss ' + str(start_sec) + ' -to ' + str(end_sec) + ' ' +
                    output_video, shell=True)
