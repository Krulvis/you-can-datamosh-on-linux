import os
import ffmpeg
from utils import output_dir, get_resolution, Frame, convert_to_mp4

input_video = os.path.abspath('3.webm')
input_png = os.path.abspath('grid.jpg')
file_name = os.path.splitext(os.path.basename(input_video))[0]
temp_video = os.path.join(output_dir, 'temp_mosh_{}.avi'.format(
    file_name))  # this ensures we won't over-write your original video
output_mosh = os.path.join(output_dir, 'test_mosh_{}.avi'.format(
    file_name))  # this ensures we won't over-write your original video
output_video = os.path.join(output_dir, 'test_mosh_{}.mp4'.format(
    file_name))  # this ensures we won't over-write your original video
width, height = get_resolution(input_video)

fps = 25
start_sec = 0
end_sec = 20

process1 = (
    ffmpeg
        .input(input_video)
        .output(temp_video, r=fps, b='5000k', g=fps * (end_sec - start_sec), pix_fmt='yuv420p',
                keyint_min=999999,
                ss=start_sec, to=end_sec)
        .run(overwrite_output=True)
)

in_file = open(temp_video, 'rb')
out_file = open(output_mosh, 'wb')

# because we used 'rb' above when the file is read the output is in byte format instead of Unicode strings
in_file_bytes = in_file.read()

# 0x30306463 which is ASCII 00dc signals the end of a frame. '0x' is a common way to say that a number is in hexidecimal format.
frames = [Frame(d) for d in in_file_bytes.split(bytes.fromhex('30306463'))]


def write_frame(frame):
    out_file.write(frame + bytes.fromhex('30306463'))


pic1, err1 = (
    ffmpeg
        .input(input_png, s='{}x{}'.format(width, height))
        .trim(start_frame=0, end_frame=1)
        .output('pipe:', format='avi', pix_fmt='yuv420p', s='{}x{}'.format(width, height))
        .run(capture_stdout=True)
)
png_frame = pic1.split(bytes.fromhex('30306463'))[1]

has_iframe = False
for f in frames:
    if f.is_key_frame() and not has_iframe:
        write_frame(f.data)
        write_frame(png_frame)
        has_iframe = True
    else:
        write_frame(f.data)

out_file.close()

process2 = (
    ffmpeg
        .input(output_mosh)
        .output(output_video, format='mp4', pix_fmt='yuv420p', b='5000k', s='{}x{}'.format(width, height))
        .run(overwrite_output=True)
)
