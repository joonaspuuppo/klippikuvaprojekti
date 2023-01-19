import os
import sys
import shutil
import math
import subprocess
import ffmpeg
from ffprobe import FFProbe

FRAMERATE = 5 # how many images per second in final video
SOURCE_VIDEO_FOLDER_PATH = "D:\\klippikuvaprojekti_data\\originalclips"
VIDEO_FRAMES_FOLDER_PATH = "H:\\koodausprojektit\\klippikuvaprojekti\\frames"
OUTPUT_VIDEO_FOLDER_PATH = "H:\\koodausprojektit\\klippikuvaprojekti\\newclips"
OUTPUT_VIDEO_LIST_PATH = "H:\\koodausprojektit\\klippikuvaprojekti\\newclips.txt"
FINAL_VIDEO_PATH = "H:\\koodausprojektit\\klippikuvaprojekti\\klippikuvaprojekti.mp4"

def frame_interval(frames):
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
    try:
        (
        ffmpeg
        .input(os.path.join(VIDEO_FRAMES_FOLDER_PATH, "frame%3d.jpeg"), framerate=3)
        .output(os.path.join(OUTPUT_VIDEO_FOLDER_PATH, f"frames_{filename}"))
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)

def already_made(filename):
    return f"frames_{filename}" in os.listdir(OUTPUT_VIDEO_FOLDER_PATH)

def videos_to_finalvideo():
    subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {OUTPUT_VIDEO_LIST_PATH} -c copy {FINAL_VIDEO_PATH}")

def write_videolist():
    with open(OUTPUT_VIDEO_LIST_PATH, "w") as file:
        for newclip in os.listdir(OUTPUT_VIDEO_FOLDER_PATH):
            path = os.path.join(OUTPUT_VIDEO_FOLDER_PATH, newclip)
            if ".txt" not in newclip:
                file.write(f"file \'{path}\'\n")

def fix_unsafe_filenames():
    for filename in os.listdir(SOURCE_VIDEO_FOLDER_PATH):
        fixed_filename = filename.replace(" ", "_").replace("ä", "a")
        old_path = os.path.join(SOURCE_VIDEO_FOLDER_PATH, filename)
        new_path = os.path.join(SOURCE_VIDEO_FOLDER_PATH, fixed_filename)
        os.rename(old_path, new_path)

# Algoritmi:
# - Tulostetaan, että aloitetaan...
# - Määritellään kuvataajuus (ehkä 5-10fps?)
# - Jokaiselle originalclips-videolle:
#   - Tulostetaan monennessa videossa ollaan menossa
#   - Lasketaan monennes ruutu tallennetaan:
#     - klipin pituus = Math.floor(videon pituus / kk-päivien määrällä)
#     - monennes ruutu = klipin pituus * videon framerate
#   - Ruudut frames-kansioon:
#     - ffmpeg -i originalclip.mp4 -vf "select=not(mod(n\,MONENNES RUUTU))" -vsync vfr "frames\frame%3d.jpeg"
#   - Luodaan newclip:
#     - ffmpeg -framerate KUVATAAJUUS -i frames\image-%3d.jpeg "newclips\newclip%3d.mp4"
#   - Tyhjennetään frames-kansio
# - Tulostetaan, että yhdistetään videot
# - Jokaiselle newclips-videolle:
#   - Yhdistetään videot > finiyshed_video.mp4
# - Tyhjennetään newclips-kansio
# - Tulostetaan, että valmista tuli!

print("Aloitetaan...")

fix_unsafe_filenames()

for originalclip in os.listdir(SOURCE_VIDEO_FOLDER_PATH):
    if already_made(originalclip):
        print(f"Käsitellään videota {originalclip}")
        continue
    print(f"Käsitellään videota {originalclip}")
    file = os.path.join(SOURCE_VIDEO_FOLDER_PATH, originalclip)
    frames = FFProbe(file).streams[0].frames()
    video_to_frames(file, frames)
    frames_to_video(originalclip)

write_videolist()
videos_to_finalvideo()