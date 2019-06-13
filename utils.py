# where we make new file names
# basename seperates the file name from the directory it's in so /home/user/you/video.mp4 becomes video.mp4
# splitext short for "split extension" splits video.mp4 into a list ['video','.mp4'] and [0] returns 'video' to file_name
import os
import re
import subprocess
import ffmpeg

iframe = bytes.fromhex('0001B0')
pframe = bytes.fromhex('0001B6')
output_dir = 'moshed_videos'
abs_out = os.path.abspath(output_dir)

# 0x0001B0 signals the beginning of an i-frame. Additional info: 0x0001B6 signals a p-frame



def get_resolution(filename):
    print('Getting video size for {!r}'.format(filename))
    probe = ffmpeg.probe(filename)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    print(width, height)
    return width, height


def convert_to_avi(input_video, target_avi, fps, start_sec, end_sec):
    print("Converting input file!")
    process1 = (
        ffmpeg
            .input(input_video)
            .output(target_avi, r=fps, b='5000k', g=fps * (end_sec - start_sec), pix_fmt='yuv420p', keyint_min=999999,
                    ss=start_sec, to=end_sec)
            .run(overwrite_output=True)
    )
    # subprocess.call('ffmpeg -loglevel error -y -i ' + input_video + ' ' +
    #                 ' -crf 0 -pix_fmt yuv420p -r ' + str(fps) + ' ' + ' -b 5000k -x264-params keyint=99999999:min-keyint=99999999'
    #                                                                   ' -ss ' + str(start_sec) + ' -to ' + str(
    #     end_sec) + ' ' +
    #                 target_avi, shell=True)
    print("Converting input done!")


def get_img_frame(img, width, height):
    file_name = os.path.splitext(os.path.basename(img))[0]

    output = os.path.abspath(os.path.join(output_dir,
                                          'png_{}.avi'.format(
                                              file_name)))  # must be an AVI so i-frames can be located in binary file

    # subprocess.call('ffmpeg -loglevel error -y -i ' + img + ' ' +
    #                 ' -crf 0 -pix_fmt yuv420p -r ' + str(25) + ' ' + ' -b 5000k ' +
    #                 '-s {}x{}'.format(width, height) +
    #                 output, shell=True)
    out, err = (
        ffmpeg
            .input(img)
            .filter('select', 'gte(n,{})'.format(0))
            .output(output, vframes=1)
            .run(capture_stdout=True, overwrite_output=True)
    )
    in_file = open(output, 'rb')
    frames = [Frame(d) for d in in_file.read().split(bytes.fromhex('30306463'))]
    return [f for f in frames if f.is_key_frame()][0]


def get_frames(input_avi, output_avi):
    # convert original file to avi

    # open up the new files so we can read and write bytes to them
    in_file = open(input_avi, 'rb')
    out_file = open(output_avi, 'wb')

    # because we used 'rb' above when the file is read the output is in byte format instead of Unicode strings
    in_file_bytes = in_file.read()

    # 0x30306463 which is ASCII 00dc signals the end of a frame. '0x' is a common way to say that a number is in hexidecimal format.
    frames = [Frame(d) for d in in_file_bytes.split(bytes.fromhex('30306463'))]

    return in_file, out_file, frames


def convert_to_mp4(output_avi, output_video, output_width, fps, start_sec, end_sec):
    print("Converting file back to mp4")
    # Convert avi to mp4. If you want a different format try changing the output variable's file extension
    # and commenting out the line that starts with -crf. If that doesn't work you'll be making friends with ffmpeg's many, many options.
    # It's normal for ffmpeg to complain a lot about malformed headers if it processes the end of a datamoshed avi.
    # The -t option specifies the duration of the final video and usually helps avoid the malformed headers at the end.
    subprocess.call('ffmpeg -loglevel error -y -i ' + output_avi + ' ' +
                    ' -crf 18 -pix_fmt yuv420p -vcodec libx264 -acodec aac -r ' + str(fps) + ' ' +
                    ' -vf "scale=' + str(output_width) + ':-2:flags=lanczos" ' + ' ' +
                    ' -max_muxing_queue_size 1024 ' +
                    # ' -ss ' + str(start_sec) + ' -to ' + str(end_sec) + ' ' +
                    output_video, shell=True)


class Frame():

    def __init__(self, data):
        self.header = data[5:8]
        self.data = data

    def is_key_frame(self):
        return self.header == iframe

    def is_delta_frame(self):
        return self.header == pframe