import PIL
import av
from av.video.stream import VideoStream
import numpy as np
from IPython.display import Image, display

from dream import Dream


def plot_image(image):
    # Assume the pixel-values are scaled between 0 and 255.

    # Ensure the pixel-values are between 0 and 255.
    image = np.clip(image, 0.0, 255.0)

    # Convert pixels to bytes.
    image = image.astype(np.uint8)

    # Convert to a PIL-image and display it.
    display(PIL.Image.fromarray(image))


## Input video
input_container = av.open('no_key_frames.avi', 'r')

## Ouput video
output_container = av.open('moshed_videos/output_packets.mp4', 'w')
stream = output_container.add_stream('mpeg4', rate=30)
stream.width = 720
stream.height = 1280
stream.pix_fmt = 'yuv420p'

## Temp file
temp_file = 'moshed_videos/temp_packets.mp4'
temp_container = av.open(temp_file, 'w')
strm = temp_container.add_stream('mpeg4', rate=30)
strm.width = 720
strm.height = 1280
strm.pix_fmt = 'yuv420p'

for packet in input_container.demux():
    if packet.stream.type == 'video':
        if packet.is_keyframe:
            ## Extract full frame and deep dream
            print(packet, packet.is_keyframe)
            for frame in packet.decode():
                print(frame)
                img = np.asarray(frame.to_image())
                plot_image(img)
                print(img.shape)

                img_result = img * 0.3
                # img_result = dream.recursive_optimize(image=img,
                #                                       num_iterations=1, step_size=3.0, rescale_factor=0.7,
                #                                       num_repeats=1, blend=0.5)
                result = np.clip(img_result, 0.0, 255.0)
                # Convert pixels to bytes.
                result = result.astype(np.uint8)

                print(result.shape)
                plot_image(result)
                new_frame = av.VideoFrame.from_ndarray(result, format='rgb24')
                ## Add frame to streams
                for packet in stream.encode(new_frame):
                    output_container.mux(packet)
                for packet in strm.encode(new_frame):
                    temp_container.mux(packet)
        else:
            ## Put frame into temp stream
            temp_container.mux_one(packet)
            tmp_reader = av.open('')
            for i, p in enumerate(temp_container.demux()):
                for frame in p.decode():
                    print('P-Frame', frame)
                    img = np.asarray(frame.to_image())
                    plot_image(img)

            break
output_container.close()
