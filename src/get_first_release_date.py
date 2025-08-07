import musicbrainzngs as mbz
from dotenv import load_dotenv
import os
from pathlib import Path
import eyed3


def get_first_release_date():
    mbz.set_useragent("testing", "0.1")
    load_dotenv()
    SONGS = Path(os.getenv("SONGS_DIRECTORY"))
    print("🗂️ Setting first release date metadata")
    for artist_dir in os.listdir(SONGS):
        for album_dir in os.listdir(SONGS / artist_dir):
            mp3_dir = SONGS / artist_dir / album_dir / "songs"
            for i, song in enumerate(os.listdir(mp3_dir)):
                audio_file = eyed3.load(mp3_dir / song)
                if i == 0:
                    artist = audio_file.tag.album_artist
                    album = audio_file.tag.album
                    release_group_data = mbz.search_release_groups(
                        artist=artist,
                        releasegroup=album,
                        limit=1
                    )["release-group-list"][0]
                    first_release_date = release_group_data["first-release-date"]
                audio_file.tag.original_release_date = first_release_date
                audio_file.tag.save()
            n_spaces = 70 - len(str(first_release_date)) - len(artist) - len(album)
            spaces = " " * n_spaces
            print(f"✅ {artist}: {album}{spaces}{first_release_date}")

if __name__ == "__main__":
    get_first_release_date()
