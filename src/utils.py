import time
import functools


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
