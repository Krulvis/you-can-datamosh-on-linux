import numpy as np
import av
from av.video.stream import VideoStream
from utils import convert_to_avi
from dream import *
import inception5h

inception5h.maybe_download()
model = inception5h.Inception5h()
layer_tensor = model.layer_tensors[6]

# Load deep dreaming lib
dream = Dream(layer=6)

### Some base functions
def transform_img(img, iterations=1, repeats=1):
#     img_result = img * 0.3
    img_result = dream.recursive_optimize(image=img,
                                          num_iterations=iterations,
                                          num_repeats=repeats,
                                          step_size=3.0,
                                          rescale_factor=0.7,
                                          blend=0.5)
    result = np.clip(img_result, 0.0, 255.0).astype(np.uint8)
    return result

def get_writer(file, width, height, fps):
    container = av.open(file, 'w')
    stream = container.add_stream('mpeg4', rate=fps)
    stream.width = width
    stream.height = height
    stream.pix_fmt = 'yuv420p'
    return container, stream

def get_reader(file):
    return av.open(file, 'r')

def write_frame(container, stream, frame):
    for packet in stream.encode(frame):
        container.mux(packet)

### First input video
input_video = 'sea.mp4'

# Get information
probe = ffmpeg.probe(input_video)
video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
width = int(video_info['width'])
height = int(video_info['height'])
fps = round(eval(video_info['avg_frame_rate']))
print(f'Fps: {fps}, Width: {width}, Height: {height}')

### Convert video to 1 key-frame avi
no_key_video = 'no_key_frames.avi'
convert_to_avi(input_video, no_key_video, fps, 0, 5)


## Input video
container = get_reader(no_key_video)

## Ouput video
output_container, output_stream = get_writer('moshed_videos/pyav_output.mp4', width, height, fps)

temp_file = 'moshed_videos/temp_packets.mp4'

temp_output_container, tmp_strm = get_writer(temp_file, width, height, fps)

f_index = 0
for packet in container.demux():
    if packet.stream.type == 'video':
        ## I am converting every video to have only 1 key-frame
        if packet.is_keyframe:
            ## Extract full frame and deep dream
            for frame in packet.decode():
                print(frame)
                img = np.asarray(frame.to_image())
                result = transform_img(img, iterations=10, repeats=4)
                new_frame = av.VideoFrame.from_ndarray(result, format='rgb24')
                ## Add frame to streams
                write_frame(output_container, output_stream, new_frame)
                write_frame(temp_output_container, tmp_strm, new_frame)

        # Every frame other than the first is not a key-frame
        else:
            ## Put p-frame into temp stream
            temp_output_container.mux_one(packet)
            temp_output_container.close()

            # Now read full frame from temp
            temp_input_container = av.open(temp_file, 'r')

            last_frame = None
            for packet in temp_input_container.demux():
                if packet.stream.type == 'video':
                    for frame in packet.decode():
                        print(frame)
                        last_frame = frame
            img = np.asarray(frame.to_image())
            print(img.shape)

            # Get transformed img
            result = transform_img(img, iterations=10)

            new_frame = av.VideoFrame.from_ndarray(result, format='rgb24')

            # Reopen output
            temp_output_container, tmp_strm = get_writer(temp_file, width, height, fps)
            ## Add frame to streams
            write_frame(output_container, output_stream, new_frame)
            write_frame(temp_output_container, tmp_strm, new_frame)

    print('Did frame:', f_index)
    f_index += 1
output_container.close()
