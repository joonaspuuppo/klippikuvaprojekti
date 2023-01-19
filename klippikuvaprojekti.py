import os
import sys
import shutil
import math
import subprocess
import ffmpeg
from ffprobe import FFProbe
import config

FRAMERATE = 5 # how many images per second in final video
ONLY_PROCESS_NEW_CLIPS = True # Switch to False to turn every originalclip to a newclip even if it has already been done
SOURCE_VIDEO_FOLDER_PATH = config.SOURCE_VIDEO_FOLDER_PATH
VIDEO_FRAMES_FOLDER_PATH = config.VIDEO_FRAMES_FOLDER_PATH
OUTPUT_VIDEO_FOLDER_PATH = config.OUTPUT_VIDEO_FOLDER_PATH
OUTPUT_VIDEO_LIST_PATH = config.OUTPUT_VIDEO_LIST_PATH
FINAL_VIDEO_PATH = config.FINAL_VIDEO_PATH

# Algorithm
# - For each originalclip:
#   - Every nth frame gets included, calculate n:
#       - frames / 30 (because each month's video consists of around 30 clips, rough approximation)
#   - Extract frames to frames folder
#   - Create newclip from frames
#   - Empty frames folder
# - For each newclip:
#   - Concatenate clips to a final video

def frame_interval(frames):
    if frames == 0:
        return 180
    return math.floor(frames / 30)

def video_to_frames(file, frames):
    #removing old frames and creating empty frames dir
    if os.path.exists(VIDEO_FRAMES_FOLDER_PATH):
        shutil.rmtree(VIDEO_FRAMES_FOLDER_PATH)
    os.mkdir(VIDEO_FRAMES_FOLDER_PATH)

    try:
        (
        ffmpeg
        .input(file)
        .filter("scale", size='hd1080')
        .filter("select", f"not(mod(n,{frame_interval(frames)}))")
        .output(os.path.join(VIDEO_FRAMES_FOLDER_PATH, "frame%3d.jpeg"), vsync="vfr")
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
       )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)

def frames_to_video(filename):
    # making sure all output videos are mp4
    filenameWithMp4 = filename.split(".")[0] + ".mp4"

    try:
        (
        ffmpeg
        .input(os.path.join(VIDEO_FRAMES_FOLDER_PATH, "frame%3d.jpeg"), framerate=FRAMERATE)
        .output(os.path.join(OUTPUT_VIDEO_FOLDER_PATH, f"frames_{filenameWithMp4}"))
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)

def already_made(filename):
    filenameWithMp4 = filename.split(".")[0] + ".mp4"
    return f"frames_{filenameWithMp4}" in os.listdir(OUTPUT_VIDEO_FOLDER_PATH)

def videos_to_finalvideo():
    # I had to use command line ffmpeg here because I couldn't get concat to work properly on the ffmpeg python wrapper
    subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {OUTPUT_VIDEO_LIST_PATH} {FINAL_VIDEO_PATH}")

def write_videolist():
    with open(OUTPUT_VIDEO_LIST_PATH, "w") as file:
        for newclip in os.listdir(OUTPUT_VIDEO_FOLDER_PATH):
            path = os.path.join(OUTPUT_VIDEO_FOLDER_PATH, newclip)
            file.write(f"file \'{path}\'\n")

def fix_unsafe_filenames():
    for filename in os.listdir(SOURCE_VIDEO_FOLDER_PATH):
        fixed_filename = filename.replace(" ", "_").replace("ä", "a")
        old_path = os.path.join(SOURCE_VIDEO_FOLDER_PATH, filename)
        new_path = os.path.join(SOURCE_VIDEO_FOLDER_PATH, fixed_filename)
        os.replace(old_path, new_path)

print("Fixing filenames")
fix_unsafe_filenames()

for originalclip in os.listdir(SOURCE_VIDEO_FOLDER_PATH):
    print(f"Processing: {originalclip}")
    
    if already_made(originalclip) and ONLY_PROCESS_NEW_CLIPS:
        continue
    
    file = os.path.join(SOURCE_VIDEO_FOLDER_PATH, originalclip)
    frames = FFProbe(file).streams[0].frames()
    video_to_frames(file, frames)
    frames_to_video(originalclip)

write_videolist()
videos_to_finalvideo()