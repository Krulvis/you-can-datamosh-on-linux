from utils import get_img_frame


class MoshProfile():

    def __init__(self, start_sec, duration, repeating, mask_img=None):
        self.start_sec = start_sec
        self.end_sec = start_sec + duration
        self.repeating = repeating
        self.start_frame = False
        self.end_frame = False
        self.mask_img = mask_img
        self.masked = False

    def info(self):
        print('mosh effect applied at: ', str(self.start_sec))
        print('mosh effect stops being applied at: ', str(self.end_sec))

    def should_mosh(self, frame_index, fps, frame):
        # if not self.moshing():
        #     return False
        # elif frame.is_key_frame():
        #     self.end_frame = frame_index
        #     print('Profile: {} - {} Moshed Frames: {} -> {}'.format(self.start_sec, self.end_sec, self.start_frame,
        #                                                             self.end_frame))
        #     return False
        # elif not self.start_frame:
        #     self.start_frame = frame_index
        return int(self.start_sec * fps) <= frame_index <= int(self.end_sec * fps)

    def should_mask(self):
        return self.mask_img is not None and not self.masked

    def moshing(self):
        return not self.end_frame
