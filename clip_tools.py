from video_tools import cut_video, glue_clips
import os

TMP_FILE_NAME_PATTERN = "%s_tmp_file.%s"
SECONDS_MAX_DURATION = 40
SECONDS_AFTER_TIMESTAMP = 1
SECONDS_BEFORE_TIMESTAMP = 20

#[timestamp...] -> [(start, end)...]
def timestamps_to_clips(timestamps):
    timestamps = [(max(0,end - SECONDS_BEFORE_TIMESTAMP + SECONDS_AFTER_TIMESTAMP), end + SECONDS_AFTER_TIMESTAMP) for end in timestamps]
    clips = []
    tmp_start, tmp_end = timestamps[0]
    for i in range(1, len(timestamps)):
        new_start, new_end = timestamps[i]
        if new_end > (tmp_start + SECONDS_MAX_DURATION):
            clips.append((tmp_start, tmp_end))
            tmp_start, tmp_end = new_start, new_end
        else:
            tmp_end = new_end
    clips.append((tmp_start, tmp_end))
    return clips

def create_clips(clips, video, tmp_folder):
    return cut_video(video, clips, False, tmp_folder)
