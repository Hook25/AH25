import math
import os
import random

from utility import get_tmp_name, panic

#TODO: make this module parametric
CONCAT_COMMAND = "ffmpeg -f concat -safe 0 -i %s -c copy -hide_banner -loglevel panic -y %s"
SET_MUSIC_COMMAND = "ffmpeg -i %s -i %s -c:v copy -map 0:v:0 -map 1:a:0 -hide_banner -loglevel panic -shortest -y %s"
BANNER_INPUT = "#File auto generater for AH25"
FILE_LINE = "\nfile '%s'"
AVG_MUSIC_LEN = 3*60

def build_input(music_paths):
  to_print = BANNER_INPUT
  for music_path in music_paths:
    to_print += (FILE_LINE % music_path)
  return to_print

def get_clip_len(clips):
  l = 0
  for start, end in clips:
    l += (end - start)
  return l

def sys_exec(command, retry):
  done = False
  cwd = os.getcwd()
  while not done:
    res_val = os.system(command)
    if res_val == 0:
      return True
    elif retry:
      whants_retry = input("Command %s failed, \nDo you want to retry? [Y/n]: " % command)
      if whants_retry[0] in 'nN':
        panic("Faled to execute %s from folder %s" % (command, cwd),True)
    else:
      panic("Failed to execute %s from folder %s" % (command, cwd),True)

def put_music(input, music_path, clips, tmp_folder):
  music_tracks = [os.path.abspath(os.path.join(music_path, x)) for x in os.listdir(music_path) if os.path.isfile(os.path.join(music_path,x)) and 'mp3' in x]
  needed_len_sec = get_clip_len(clips)
  needed_music = int(math.ceil(needed_len_sec/AVG_MUSIC_LEN))
  print(needed_music)
  to_use_music = random.sample(music_tracks, needed_music)
  input_instruction = build_input(to_use_music)
  musicbuild_name = get_tmp_name(".musicbuild", "tmp_", tmp_folder)
  f = open(musicbuild_name, "w+")
  f.write(input_instruction)
  f.close()
  music_file_name = get_tmp_name(".mp3", "tmp_", tmp_folder)
  sys_exec(CONCAT_COMMAND % (musicbuild_name, music_file_name), False)
  output_name_file = get_tmp_name(".mp4", "tmp_", tmp_folder)
  sys_exec(SET_MUSIC_COMMAND % (input, music_file_name, output_name_file), False)
  return (output_name_file)
