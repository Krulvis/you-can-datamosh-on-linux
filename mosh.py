import utils
import os
from utils import get_frames, convert_to_mp4, iframe, pframe


class Mosher():

    def __init__(self, input_video, end_sec):
        self.input_video = input_video
        self.fps = 25
        self.output_width = 720
        self.start_sec = 0
        self.end_sec = end_sec

        output_dir = 'moshed_videos'

        file_name = os.path.splitext(os.path.basename(self.input_video))[0]
        self.output_video = os.path.join(output_dir,
                                         'moshed_{}.mp4'.format(
                                             file_name))  # this ensures we won't over-write your original video

        # path.join pushes the directory and file name together and makes sure there's a / between them
        self.input_avi = os.path.join(output_dir,
                                      'datamoshing_input.avi')  # must be an AVI so i-frames can be located in binary file
        self.output_avi = os.path.join(output_dir, 'datamoshing_output.avi')

        self.in_file, self.out_file, self.frames = get_frames(self.input_video, self.input_avi, self.output_avi,
                                                              self.fps,
                                                              self.start_sec, self.end_sec)

    def remove_keyframes(self):
        key_frame = None

        for index, frame in enumerate(self.frames):
            if not key_frame:
                self.write_frame(frame)

                if frame[5:8] == iframe:
                    key_frame = frame

            elif frame[5:8] != iframe:
                self.write_frame(frame)

    def mosh(self, profiles):
        for p in profiles:
            p.info()

        # We want at least one i-frame before the glitching starts
        i_frame_yet = False

        for index, frame in enumerate(self.frames):

            if not i_frame_yet:
                # the split above removed the end of frame signal so we put it back in
                self.write_frame(frame)

                # found an i-frame, let the glitching begin
                if frame[5:8] == iframe:
                    i_frame_yet = True

            elif not any([p.should_mosh(index, self.fps) for p in profiles]):
                self.write_frame(frame)

            elif frame[5:8] != iframe:
                # else:
                # while we're moshing we're repeating p-frames and multiplying i-frames
                for profile in profiles:
                    if profile.should_mosh(index, self.fps):
                        # this repeats the p-frame x times
                        for i in range(profile.repeating):
                            self.out_file.write(frame)

                        self.out_file.write(bytes.fromhex('30306463'))

    def get_first_frames(self):
        length = 5
        for index in range(length):
            frame = self.frames[index]
            print(frame)
            header = frame[5:8]
            print(header, 'iframe: ', header == iframe, 'pframe: ', header == pframe)
            a = bytearray(frame)
            print('OG', a[5:8])
            a[5:8] = [b for b in pframe]
            print('MOD', a[5:8])
            convert = bytes(a)
            print(convert == frame)

    def mutate_to_deltaframes(self):
        first_key_frame = None

        for index, frame in enumerate(self.frames):
            if not first_key_frame:
                self.write_frame(frame)

                if frame[5:8] == iframe:
                    first_key_frame = frame

            elif frame[5:8] == iframe:
                a = bytearray(frame)
                a[5:8] = [b for b in pframe]
                self.write_frame(bytes(a))

    def write_frame(self, frame):
        self.out_file.write(frame + bytes.fromhex('30306463'))

    def reset_frames(self):
        self.frames = open(self.output_avi, 'rb').read().split(bytes.fromhex('30306463'))
        self.out_file = open(self.output_avi, 'wb')

    def finish(self):
        convert_to_mp4(self.output_avi, self.output_video, self.output_width, self.fps)
        # gets rid of the in-between files so they're not crudding up your system
        os.remove(self.input_avi)
        os.remove(self.output_avi)
        print('Mosh Complete: ', self.output_video)


class MoshProfile():

    def __init__(self, start_sec, duration, repeating):
        self.start_sec = start_sec
        self.end_sec = start_sec + duration
        self.repeating = repeating

    def info(self):
        print('mosh effect applied at: ', str(self.start_sec))
        print('mosh effect stops being applied at: ', str(self.end_sec))

    def should_mosh(self, frame_index, fps):
        return int(self.start_sec * fps) <= frame_index <= int(self.end_sec * fps)
