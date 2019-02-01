from utility import panic, get_tmp_name
import os
from multiprocessing import Pool, cpu_count
from functools import partial
#-to id bugged use -t
#                            start input  end                                                  output
FFMPEG_NAME = "ffmpeg.exe"
FFMPEG_CREATE_CLIP_COMMAND = FFMPEG_NAME + " -ss %s -i %s -t %s -c copy -avoid_negative_ts 1 -hide_banner -loglevel panic -y %s "
OUTPUT_NAME_PATTERN = "tmp%s.mp4"
#concat is bugged, freezes
FFMPEG_CONCAT_VIDEO = FFMPEG_NAME + " -f concat -safe 0 -i %s -c copy -hide_banner -loglevel panic -y %s"
INSTRUCTION_FILE = "\nfile '%s'"
BANNER_INSTRUCTION_FILE = "#Autogenerated by AH25"

def init_module(new_ffmpeg_name):
  global FFMPEG_NAME
  FFMPEG_NAME = new_ffmpeg_name

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

#(video_filename, start in seconds, end in seconds) -> Bool result
def cut(retry, video, start,end, output):
  end = end - start
  cmd = FFMPEG_CREATE_CLIP_COMMAND % (start, video, end, output)
  sys_exec(cmd, retry)

def cut_wrapper(retry, video, start_end_output):
  start, end, output = start_end_output
  cut(retry, video, start, end, output)
  return True

def cut_video(input_video, timestamps, retry, tmp_folder):
  cores = cpu_count() 
  pool = Pool(cores)
  args = [(start, end, get_tmp_name(".mp4", "clip_", tmp_folder) ) for (start, end) in timestamps]
  partial_cut = partial(cut_wrapper, retry, input_video)
  pool.map(partial_cut, args)
  pool.close()
  pool.join()
  to_r = [ name for start, end, name in args ]  
  return to_r
  
def create_instruction(clips_path, output):
  f = open(output,"w+")
  f.write(BANNER_INSTRUCTION_FILE)
  for clip_path in clips_path:
    f.write(INSTRUCTION_FILE % clip_path)
  f.close()

def glue_clips(clips_path, output_path, tmp_floder):
  tmp_instruction = get_tmp_name(".videobuild", "tmp_", tmp_floder)
  create_instruction(clips_path, tmp_instruction)
  cmd = FFMPEG_CONCAT_VIDEO % (tmp_instruction, output_path)
  sys_exec(cmd,False)