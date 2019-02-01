import os
import shutil
import sys
import tempfile

CONFIG_FILENAME="config.ini"

def get_tmp_name(suffix, prefix, dir):
    f = tempfile.NamedTemporaryFile(mode='w+b', suffix=suffix, prefix=prefix, dir=dir, delete=False)
    f.close()
    return f.name

def panic(message, exception=False):
    import traceback
    import sys
    sys.stdout.flush()
    traceback.print_stack()
    print()
    print("#"*len(message))
    print(message)
    print("#"*len(message))
    sys.stdout.flush()
    if exception:
        raise Exception(message)
    else:
        sys.exit(1)

def warn(message):
    sys.stdout.flush()
    print()
    print("!" * len(message))
    print(message)
    print("!" * len(message))
    sys.stdout.flush()


def parse_cli_args(argv):
    args = {}
    for arg in argv:
        if "=" in arg:
            key, val = arg.split("=")
            args[key] = val
    return args

def load_static_conf():
    if not os.path.isfile(CONFIG_FILENAME):
        return {}
    config = {}
    f = open(CONFIG_FILENAME)
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.lstrip().rstrip()
        if len(line) > 0 and not(line[0] == '#'):
            key, arg = line.split('=')
            config[key] = arg
    return config

def log(message):
    print(message)

def clean(files, cli_args):
    if "clean" in cli_args and cli_args["clean"] == "True":
        log("Cleaning")
        for file in files:
            os.remove(file)

def soft_panic(message):
    choice = input("%s \nRetry? [Y/n] > " % message)
    if choice == 'n':
        panic(message)

def enter_and_setup_fakeroot_env(cli_args):
    if 'fakeroot_env' not in cli_args:
        warn("Running without fakeroot enviroment, this is not a good idea")
    else:
        if not os.path.isdir(cli_args["fakeroot_env"]):
            panic("Specified fakeroot does not exist")
        log("Entering fakeroot enviroment")
        os.chdir(cli_args["fakeroot_env"])
    if 'video' not in cli_args:
        panic("No input was provided, use video=? or configure video in config.ini")
    if 'tmp_folder' not in cli_args:
        panic("No tmp folder was provided, use tmp_folder=? or configure tmp_folder in config.ini")
    if 'out' not in cli_args:
        panic("No out file was provided, use out=? or configure out in config.ini")
    if "music_folder" not in cli_args:
        panic("No music_folder was provided, use music_folder=? or configure music_folder in config.ini")
    if not os.path.isfile(cli_args['video']):
        log(os.getcwd())
        panic("%s does not exist in fakeroot enviroment" % cli_args['video'])
    if not os.path.isdir(cli_args['tmp_folder']):
        os.makedirs(cli_args['tmp_folder'])
    if os.path.isfile(cli_args['out']):
        log("Out file was already present, backing it up")
        shutil.copy(cli_args['out'],cli_args['out'] + ".old")
    if "clean" not in cli_args:
        warn("clean was not specified, everything will be cleaned")  
    if not os.path.isdir(cli_args["music_folder"]):
        panic("Provided music_folder does not exist under fakeroot enviroment")
