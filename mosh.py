import os

from utils import get_frames, convert_to_mp4, iframe, pframe, convert_to_avi, abs_out, output_dir, get_resolution, \
    get_img_frame


class Mosher():

    def __init__(self, input_video, end_sec):
        self.input_video = input_video
        self.fps = 25
        self.output_width = 720
        self.start_sec = 0
        self.end_sec = end_sec

        if not os.path.exists(abs_out):
            os.makedirs(abs_out)

        file_name = os.path.splitext(os.path.basename(self.input_video))[0]
        self.output_video = os.path.join(output_dir,
                                         'moshed_{}.mp4'.format(
                                             file_name))  # this ensures we won't over-write your original video

        # path.join pushes the directory and file name together and makes sure there's a / between them
        self.input_avi = os.path.join(output_dir,
                                      'datamoshing_input.avi')  # must be an AVI so i-frames can be located in binary file
        self.output_avi = os.path.join(output_dir, 'datamoshing_output.avi')

        # Initialize empty list of frames
        self.frames = []

    def get_frames(self):
        # Convert the input video to AVI, and get a list of all the frames
        convert_to_avi(self.input_video, self.input_avi,
                       self.fps,
                       self.start_sec, self.end_sec)
        self.in_file, self.out_file, self.frames = get_frames(self.input_avi, self.output_avi)

    def get_resolutions(self):
        self.width, self.height = get_resolution(self.input_avi)
        print('Found resolution: {} x {}'.format(self.width, self.height))

    def remove_keyframes(self):
        key_frame = None

        for index, frame in enumerate(self.frames):
            if not key_frame:
                self.write_frame(frame)

                if frame.is_key_frame():
                    key_frame = frame

            elif not frame.is_key_frame():
                self.write_frame(frame)

    def remove_deltaframes(self):

        for index, frame in enumerate(self.frames):
            if not frame.is_delta_frame():
                self.write_frame(frame)

    def mosh(self, profiles):
        for p in profiles:
            p.info()

        # We want at least one i-frame before the glitching starts
        i_frame_yet = False
        moshing = False

        for index, frame in enumerate(self.frames):

            # Find an i-frame before going on with moshing
            if not i_frame_yet:
                # the split above removed the end of frame signal so we put it back in
                self.write_frame(frame)

                # found an i-frame, let the glitching begin
                if frame.is_key_frame():
                    i_frame_yet = True

            elif not any([p.should_mosh(index, self.fps, frame) for p in profiles]):
                self.write_frame(frame)

            elif not frame.is_key_frame():
                # while we're moshing we're repeating p-frames and multiplying i-frames
                for profile in profiles:
                    if profile.should_mosh(index, self.fps, frame):
                        # this repeats the p-frame x times
                        if profile.should_mask():
                            self.write_frame(get_img_frame(profile.mask_img, self.width, self.height))
                            profile.masked = True
                        for i in range(profile.repeating):
                            f = self.frames[index]
                            if f.is_delta_frame():
                                # self.out_file.write(f.data)
                                self.write_frame(f)

                        # self.out_file.write(bytes.fromhex('30306463'))

    def analyze(self):
        headers = []
        iframes = []
        pframes = []
        for f in self.frames:
            header = f.header
            if not header in headers:
                headers.append(header)
            if header == iframe:
                iframes.append(f)
            elif header == pframe:
                pframes.append(f)
        print('Total frames: ', len(self.frames))
        print('KeyFrames: {0:d}, {1:.2f}%'.format(len(iframes), (len(iframes) / len(self.frames) * 100.0)))
        print('DeltaFrames: {0:d}, {1:.2f}%'.format(len(pframes), (len(pframes) / len(self.frames) * 100.0)))
        for h in headers:
            print(h, ' : ', h.hex())

    def write_frame(self, frame):
        self.out_file.write(frame.data + bytes.fromhex('30306463'))

    def reset_frames(self):
        self.frames = open(self.output_avi, 'rb').read().split(bytes.fromhex('30306463'))
        self.out_file = open(self.output_avi, 'wb')

    def finish(self):
        convert_to_mp4(self.output_avi, self.output_video, self.output_width, self.fps, self.start_sec, self.end_sec)
        # gets rid of the in-between files so they're not crudding up your system
        # os.remove(self.input_avi)
        # os.remove(self.output_avi)
        print('Mosh Complete: ', self.output_video)
