import os
import shutil
import sys

from clip_tools import create_clips, timestamps_to_clips
from lol_tools import get_kills
from music_tools import put_music
from utility import (enter_and_setup_fakeroot_env, get_tmp_name,
                     load_static_conf, log, panic, parse_cli_args, warn)
from video_tools import glue_clips

#def put_outro(mounted_path, outro):
#    glue_together([mounted_path, outro], "output/end.mp4")

#cli args have precedence over static conf
def load_conf():
    static_conf = load_static_conf()
    cli_args = parse_cli_args(sys.argv)
    for key in cli_args:
        static_conf[key] = cli_args[key]
    return static_conf

def clean(folder, to_do):
    files = [os.path.join(folder, x) for x in  os.listdir(folder)]
    if to_do.lower() in ["true", "yes"]:
        for f in files:
            os.remove(f)

def main():
    old_term_path = os.getcwd()
    cli_args = load_conf()
    enter_and_setup_fakeroot_env(cli_args)
    video_path, tmp_folder_path, music_folder_path, out_path = cli_args["video"], cli_args["tmp_folder"], cli_args["music_folder"], cli_args["out"]
    log("Elaborating input video")
    timestamps = get_kills(video_path)
    log("Timestamp aquired correctly")
    clips = timestamps_to_clips(timestamps)
    log("Found %s clips that are \n%s\n" % (len(clips), str(clips)))
    #log("Found %s clips" % (len(clips)))
    actual_clips_path = create_clips(clips, video_path, tmp_folder_path)
    name_tmp_without_music = get_tmp_name(".mp4", "intermidiate", tmp_folder_path)
    glue_clips(actual_clips_path, name_tmp_without_music, tmp_folder_path)
    mounted_with_music_path = put_music(name_tmp_without_music, music_folder_path, clips, tmp_folder_path)
    #bugged -> put_outro(mounted_with_music_path, "input/outro.mp4")
    shutil.move(mounted_with_music_path, out_path)
    log("Cleaning if needed")
    clean(tmp_folder_path, cli_args["clean"])
    log("Exiting fakeroot enviroment")
    os.chdir(old_term_path)

if __name__ == '__main__':
    main()
