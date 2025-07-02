import eyed3
import os
from pathlib import Path
import shutil
from dotenv import load_dotenv
import tempfile
import utils as ut


def migrate():
    load_dotenv()
    while True:
        migrate_input = input("Do you want to migrate songs to new directory structure? ([y]es/(n)o): ").lower()
        if (migrate_input == "y") or (migrate_input == ""):
            SONGS = Path(os.getenv("SONGS_DIRECTORY"))
            if not ut.is_flat_directory(SONGS):
                print(f"💀 {SONGS} directory doesn't conform to old organizational structure, can't migrate")
                exit()
            TEMP_SONGS = Path(tempfile.mkdtemp())
            ALBUM_ART = Path(os.getenv("ALBUM_ART_DIRECTORY"))
            if ALBUM_ART is None:
                ALBUM_ART = Path(os.getenv("BASE_DIRECTORY")) / "album_art"
            for mp3_file_name in os.listdir(SONGS):
                audiofile = eyed3.load(SONGS / mp3_file_name)
                mp3_file_name_components = mp3_file_name.split(".")
                del mp3_file_name_components[-2]
                track_number = str(audiofile.tag.track_num[0]).zfill(2)
                mp3_file_name_components.insert(0, track_number)
                mp3_file_name_new = ".".join(mp3_file_name_components)
                artist = ut.sanitize(audiofile.tag.artist)
                album = ut.sanitize(audiofile.tag.album)
                album_art_file_name_old = album + ".1.jpg"
                album_art_file_name_new = album + ".jpg"
                album_dir_new = TEMP_SONGS / artist / album
                album_dir_new_songs = album_dir_new / "songs"
                album_dir_new_songs.mkdir(parents=True, exist_ok=True)
                album_art_dir_new = album_dir_new / "album_art"
                album_art_dir_new.mkdir(parents=True, exist_ok=True)
                shutil.copy(
                    SONGS / mp3_file_name,
                    album_dir_new_songs / mp3_file_name_new
                )
                try:
                    shutil.copy(
                        ALBUM_ART / album_art_file_name_old,
                        album_art_dir_new / album_art_file_name_new
                    )
                except:
                    pass
            shutil.rmtree(SONGS)
            shutil.copytree(TEMP_SONGS, SONGS)
            shutil.rmtree(TEMP_SONGS)
            shutil.rmtree(ALBUM_ART)
            print("➡️ Migrated to new song directory organisation")
            exit()
        elif (migrate_input == "n"):
            exit()
        else:
            continue

if __name__ == "__main__":
    migrate()
