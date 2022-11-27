import subprocess

# how many images per second in final video
FRAMERATE = 5

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
#   - Yhdistetään videot > finished_video.mp4
# - Tyhjennetään newclips-kansio
# - Tulostetaan, että valmista tuli!

print("Aloitetaan...")

for i in range(len(originalclips)):
    print(f"Käsitellään klippiä {i}")
    
