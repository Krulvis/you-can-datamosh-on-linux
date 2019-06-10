import os

from utils import get_img_frame, get_resolution

f = get_resolution(os.path.abspath("moshed_videos/datamoshing_input.avi"))
print(f)
