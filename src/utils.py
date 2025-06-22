import uuid
import os
from dotenv import load_dotenv


def sanitize(filename):
    translation_table = str.maketrans(
        {
            "/": "-",
            ":": "_",
            " ": "_",
            "’": "",
            "'": "",
            "(": "-",
            ")": "-",
            "[": "-",
            "]": "-",
            "*": "-",
            '"': "",
            "?": "",
            "&": "and",
            "“": "",
            "”": "",
        }
    )
    return f"{filename.translate(translation_table).lower()}"

def duration_s_to_min_s(duration_s):
    duration_min = int(duration_s // 60)
    duration_s_remainder = round(duration_s % 60)
    duration_min_s = f"{duration_min:02}:{duration_s_remainder:02}"
    return duration_min_s

def print_song_title(title, track_number, duration):
    duration = duration_s_to_min_s(duration)
    if duration == "00:00":
        duration = "??:??"
    string_without_duration = f"{str(track_number).zfill(2)}) {title}"
    n_spaces = 70 - len(string_without_duration)
    spaces = " " * n_spaces
    underscores = "_" * n_spaces
    try:
        print(f"    \033[4m{string_without_duration}{spaces}{duration}\033[0m")
    except:
        print(f"{string_without_duration}{underscores}{duration}")

def print_release_id(release_id):
    print("🌐 Musicbrainz release page:")
    print(f"    🔗 https://www.musicbrainz.org/release/{release_id}")

def validate_release_id(parser, release_id_input):
    if release_id_input is not None:
        try:
            release_id = release_id_input.split("/")[-1]
            uuid.UUID(release_id)
            return release_id
        except:
            parser.error("💀 Invalid Musicbrains release ID")
    else:
        return release_id_input

def is_flat_directory(path):
    with os.scandir(path) as entries:
        return all(not entry.is_dir() for entry in entries)

def load_organize_songs():
    load_dotenv()
    if (
        (os.getenv("ORGANIZE_SONGS") is None) or
        (os.getenv("ORGANIZE_SONGS").lower() == "false")
    ):
        return False
    elif os.getenv("ORGANIZE_SONGS").lower() == "true":
        return True
    else:
        print("💀 Set ORGANIZE_SONGS variable in .env file to either true or false")
        exit()
