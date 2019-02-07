import os
import sys
import time
from math import pow, sqrt

import cv2
import numpy as np

from utility import panic, soft_panic

RECOGNITION_TRESHOLD=0.9
SAMPLING = 90 #s
BLUE_KILL = [130.6, 73.3, 9.3]
YELLOW_COLOR = [4.6, 201, 251]
KILL_LOCATION_CONSTRAINT = [
    [[(1912, 241), (1920, 302)], BLUE_KILL],
    [[(1769, 246), (1820, 248)], YELLOW_COLOR]
]
kill_images = []

def signal_progress(workdone):
    print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(workdone * 50), workdone*100), end="", flush=True)

#video_path -> cv2.VideoCapture
def get_video_stream(path):
    if not os.path.isfile(path):
        panic("%s does not name a file" % path)
    video = cv2.VideoCapture(path)
    if not video.isOpened():
        panic("Failed to read %s" % path)
    return video
#cv2.VideoCapture -> Bool
def end_of_video(video_stream):
    return video_stream.get(cv2.CAP_PROP_POS_FRAMES) == video_stream.get(cv2.CAP_PROP_FRAME_COUNT)
#frame -> Bool
def frame_contains_kill(frame):
    for rect, color in KILL_LOCATION_CONSTRAINT:
        avg_rec_color = calculate_avg_color_rect(rect, frame)
        loc_deviance = 1 - distance_colors(avg_rec_color, color)
        if loc_deviance < RECOGNITION_TRESHOLD:
            return False
    return True
def calculate_avg_color_rect(rect, img):
    (base_x, base_y), (top_x, top_y) = rect
    mean = img[base_y:top_y, base_x:top_x].mean(axis=0).mean(axis=0)
    return mean
#(color, color) -> 0...1
def distance_colors(color1, color2):
    r,g,b = color1
    r1,g1,b1 = color2
    return (sqrt(pow(r-r1,2) + pow(g-g1, 2) + pow(b-b1,2))) / sqrt(255**2 + 255**2 + 255**2)
#video_path -> [timstamp, ...]
def get_kills(video_path):
    video_stream = get_video_stream(video_path)
    skip = SAMPLING
    msecond_number = 0
    fps = video_stream.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
    frameCount = int(video_stream.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frameCount/fps
    kill_frames = []
    while not end_of_video(video_stream):
        frame_ready, frame = video_stream.read()
        if frame_ready:
            if frame_contains_kill(frame):
                kill_frames.append(int(video_stream.get(cv2.CAP_PROP_POS_MSEC) / 1000))
        else:
            soft_panic("Frame is not yet ready")
        msecond_number += skip
        signal_progress(msecond_number / duration)
        video_stream.set(cv2.CAP_PROP_POS_MSEC , msecond_number * 1000)
    video_stream.release()
    print()
    return kill_frames
