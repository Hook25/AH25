import cv2
from threading import Thread
from queue import Queue

class FastVideoStream():
    def __init__(self, path, sampling):
       self._vc = cv2.VideoCapture(path)
       self._sampling = sampling
       self._queue = Queue()

    def __enter__(self):
        self.done = False
        self._thread = Thread(target = self._fetch)
        self._thread.daemon = True
        self._thread.start()
        return self

    def __exit__(self, t, v, traceback):
        self.done = True

    def _fetch(self):
        t_p = -1
        while not self.done:
            self.done = not self._vc.grab()
            if not self.done:
                t_n = self._vc.get(cv2.CAP_PROP_POS_MSEC) / 1000
                if int(t_n) >= (int(t_p) + self._sampling):
                    self._queue.put(self._vc.retrieve())
                t_p = t_n

    def read(self):
         return self._queue.get()

video_capture = cv2.VideoCapture("video.mp4")

frames = {}
def get_all_frames_by_ms():
    time = 0
    while True:
        video_capture.set(cv2.CAP_PROP_POS_MSEC, time)
        capture_success, frames[time] = video_capture.read()
        if (not capture_success) or len(frames) > 100:
            break
        time += 1000

def get_all_frames_in_order():
    prev_time = -1
    while True:
        grabbed = video_capture.grab()
        if grabbed and len(frames) < 100:
            time_s = video_capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if int(time_s) > int(prev_time):
                # Only retrieve and save the first frame in each new second
                frames[int(time_s)] = video_capture.retrieve()
            prev_time = time_s
        else:
            break
import time
t = time.time()
get_all_frames_by_ms()
dt = time.time() - t
dt /= 100
print("slow MS: %sms" % dt)
frames = {}
video_capture = cv2.VideoCapture("video.mp4")
t = time.time()
get_all_frames_in_order()
dt = time.time() - t
dt /= 100
print("fast MS: %sms" % dt)
t = time.time()
frames = {}
with FastVideoStream("video.mp4", 1) as fvs:
    for i in range(100):
        frames[i] = fvs.read()
dt = time.time() - t
dt /= 100
print("parallel MS: %sms" % dt)
