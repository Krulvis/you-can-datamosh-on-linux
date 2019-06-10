from utils import iframe, pframe


class Frame():

    def __init__(self, data):
        self.header = data[5:8]
        self.data = data

    def is_key_frame(self):
        return self.header == iframe

    def is_delta_frame(self):
        return self.header == pframe
