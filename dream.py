import os
import numpy as np
import ffmpeg

from tensorflow_stream import DeepDream, run
from utils import abs_out, output_dir


class Dream():

    def __init__(self, input_vid):
        self.input = input_vid

        abs_input = os.path.abspath(input_vid)
        if not os.path.exists(abs_out):
            os.makedirs(abs_out)

        file_name = os.path.splitext(os.path.basename(self.input))[0]
        self.output_video = os.path.join(output_dir,
                                         'moshed_{}.mp4'.format(
                                             file_name))  # this ensures we won't over-write your original video

        deep_dream = DeepDream()
        run(abs_input, self.output_video, deep_dream.process_frame)


if __name__ == '__main__':
    import tensorflow as tf

    Dream('moshed_11.mp4')
