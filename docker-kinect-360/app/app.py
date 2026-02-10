import freenect
import cv2
import numpy as np

rgb, _ = freenect.sync_get_video()
depth, _ = freenect.sync_get_depth()

print(rgb.shape, depth.shape)
