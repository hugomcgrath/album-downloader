import musicbrainzngs as mbz
import requests
from googleapiclient.discovery import build
import os
import eyed3
from PIL import Image
from io import BytesIO
from pathlib import Path
import shutil
import subprocess
import utils as ut
from isodate import parse_duration
from dotenv import load_dotenv
from rapidfuzz.fuzz import partial_ratio
import tempfile
import argparse
import datetime
from zoneinfo import ZoneInfo
import yt_dlp


load_dotenv()
SONGS = Path(os.getenv("SONGS_DIRECTORY"))
SONGS.mkdir(parents=True, exist_ok=True)

ORGANIZE_SONGS = ut.load_organize_songs()

if not ORGANIZE_SONGS:
    ALBUM_ART = Path(os.getenv("ALBUM_ART_DIRECTORY"))
    ALBUM_ART.mkdir(parents=True, exist_ok=True)

TEMP_ALBUM = Path(tempfile.mkdtemp())
TEMP_ART = Path(tempfile.mkdtemp())

YT_API_KEY = os.getenv("YT_API_KEY")
if  (YT_API_KEY == "your-yt-api-key-goes-here") or (YT_API_KEY is None):
    print("💀 Set YT_API_KEY variable in .env file to your YouTube Data API key (see README.md)")
    exit()

THUMBNAIL_SIZE = (500, 500)
DURATION_TOLERANCE = 10 # s
MIN_FUZZY = 90

youtube = build("youtube", "v3", developerKey=YT_API_KEY)
mbz.set_useragent("testing", "0.1")


class Album:
    def __init__(
        self,
        artist=None,
        album_title=None,
        release_id=None
    ):
        self.artist = artist
        self.album_title = album_title
        self.release_id = release_id
        self.album_art_path = None
        self.track_list = []

    def get_artist_and_album_title(self):
        release_data = mbz.get_release_by_id(self.release_id, includes=["artists"])
        self.artist = release_data["release"]["artist-credit"][0]["artist"]["name"]
        self.album_title = release_data["release"]["title"]

    def _has_album_art(self):
        try:
            images = mbz.get_image_list(self.release_id)
            return len(images.get("images", [])) > 0
        except mbz.ResponseError as e:
            if e.cause.code == 404:
                return False
            else:
                raise

    def get_release_id(self):
        release_group_result = mbz.search_release_groups(
            artist=self.artist,
            releasegroup=self.album_title,
            type="album",
            status="official"
        )
        for release_group in release_group_result["release-group-list"]:
            if release_group["title"].lower() == self.album_title.lower():
                release_group_id = release_group["id"]
                break
        else:
            raise ValueError("Album not found")
        releases = mbz.get_release_group_by_id(
            release_group_id,
            includes=["releases"]
        )["release-group"]["release-list"]
        for release in releases:
            self.release_id = release["id"]
            if self._has_album_art():
                return
            else:
                continue
        # if can't find album art, default to first release
        self.release_id = releases[0]["id"]

    def get_album_art(self):
        if self._has_album_art():
            url = f"https://coverartarchive.org/release/{self.release_id}/front"
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image = image.convert("RGB")
                image.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
                if ORGANIZE_SONGS:
                    self.album_art_path = TEMP_ART / f"{ut.sanitize(self.album_title)}.jpg"
                else:
                    self.album_art_path = TEMP_ART / f"{ut.sanitize(self.album_title)}.1.jpg"
                image.save(self.album_art_path, format="JPEG", quality=85)
                print("✅ Downloaded album art")
                try:
                    subprocess.run(["kitten", "icat", self.album_art_path])
                except:
                    pass
            else:
                print("❌ Album art not available")

        else:
            print("❌ Album art not available")

    def get_track_list(self):
        discs = mbz.get_release_by_id(
            self.release_id,
            includes=["recordings"]
        )["release"]["medium-list"]
        print("📝 Tracklist:")
        track_number = 0
        for disc in discs:
            for track in disc["track-list"]:
                title = track["recording"]["title"]
                track_number += 1
                try:
                    duration = int(track["recording"]["length"]) / 1000 # ms -> s
                except:
                    duration = 0
                self.track_list.append(
                    Song(
                        title,
                        track_number,
                        duration,
                        self.artist,
                        self.album_title,
                        self.album_art_path,
                    )
                )
                ut.print_song_title(title, track_number, duration)

    def get_youtube_urls(self):
        for song in self.track_list:
            song._get_youtube_url()

    def download_mp3s(self):
        for song in self.track_list:
            song._download_mp3()
            song._set_metadata()

        if ORGANIZE_SONGS:
            ALBUM_DIR = SONGS / ut.sanitize(self.artist) / ut.sanitize(self.album_title)
            SONGS_ORGANIZED = ALBUM_DIR / "songs"
            SONGS_ORGANIZED.mkdir(parents=True, exist_ok=True)
            ALBUM_ART_ORGANIZED = ALBUM_DIR / "album_art"
            ALBUM_ART_ORGANIZED.mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(TEMP_ART / os.listdir(TEMP_ART)[0], ALBUM_ART_ORGANIZED)
            except:
                pass

            for mp3_file in os.listdir(TEMP_ALBUM):
                shutil.move(TEMP_ALBUM / mp3_file, SONGS_ORGANIZED)
        else:
            try:
                shutil.move(TEMP_ART / os.listdir(TEMP_ART)[0], ALBUM_ART)
            except:
                pass

            for mp3_file in os.listdir(TEMP_ALBUM):
                shutil.move(TEMP_ALBUM / mp3_file, SONGS)


class Song:
    def __init__(
        self,
        title,
        track_number,
        duration,
        artist,
        album_title,
        album_art
    ):
        self.title = title
        self.track_number = track_number
        self.duration = duration
        self.artist = artist
        self.album_title = album_title
        self.album_art_path = album_art
        self.youtube_url = None
        if ORGANIZE_SONGS:
            self.mp3_file_name = str(self.track_number).zfill(2) + "." + ut.sanitize(self.title) + ".mp3"
        else:
            self.mp3_file_name = ut.sanitize(self.title) + ".1.mp3"

    def _get_youtube_url(self):
        ut.print_song_title(self.title, self.track_number, self.duration)

        search_query = f"{self.artist} - {self.title}"
        try:
            search_items = youtube.search().list(
                q=search_query,
                part="id,snippet",
                type="video",
                videoCategoryId="10",
                maxResults=5,
                fields="items(id(videoId),snippet(channelTitle))"
            ).execute()["items"]
        except:
            pacific = ZoneInfo("America/Los_Angeles")
            midnight_pacific = datetime.datetime.combine(datetime.datetime.now(), datetime.time(0, 0)).replace(tzinfo=pacific)
            local_time = midnight_pacific.astimezone()
            print(f"💀 YouTube API daily quota exceeded, try again tomorrow at {local_time.strftime('%H:%M %Z')}")
            raise
        video_ids = [item["id"]["videoId"] for item in search_items]
        channels = [item["snippet"]["channelTitle"] for item in search_items]

        videos_items = youtube.videos().list(
            part="contentDetails,snippet",
            id=",".join(video_ids),
            fields="items(contentDetails(duration),snippet(title,description))"
        ).execute()["items"]
        durations_iso = [item["contentDetails"]["duration"] for item in videos_items]
        durations = [parse_duration(d).total_seconds() for d in durations_iso]
        video_titles = [item["snippet"]["title"] for item in videos_items]
        descriptions = [item["snippet"]["description"] for item in videos_items]

        warnings_videos = []
        warning_scores = []
        for duration, video_title, description, channel in zip(
            durations,
            video_titles,
            descriptions,
            channels
        ):
            warnings_video = []
            warning_score = 0
            if (partial_ratio(self.artist.lower(), channel.lower()) < MIN_FUZZY):
                warnings_video.append(
                    "🟡 Possibly not from official channel"
                )
                warning_score += 1
            if partial_ratio(self.title.lower(), video_title.lower()) < MIN_FUZZY:
                warnings_video.append(
                    "🟠 Song title doesn't match video title"
                )
                warning_score += 2
            if abs(duration - self.duration) > DURATION_TOLERANCE:
                warnings_video.append(
                    f"🔴 Duration outside {DURATION_TOLERANCE} s tolerance"
                )
                warning_score += 4
            warnings_videos.append(warnings_video)
            warning_scores.append(warning_score)
        best_i = 0
        best_warning_score = 8
        for i, warning_score in enumerate(warning_scores):
            if warning_score < best_warning_score:
                best_warning_score = warning_score
                best_i = i
                if warning_score == 0:
                    self.youtube_url = f"https://www.youtube.com/watch?v={video_ids[best_i]}"
                    print(f"\t✅ {self.youtube_url}")
                    return
        # falls back on the first result if no perfect result found
        self.youtube_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
        if warning_scores[0] >= 4:
            print(f"\t⚠️ {self.youtube_url}")
        elif (warning_scores[0] >= 2) and (best_warning_score < 4):
            print(f"\t⚠️ {self.youtube_url}")
        elif warning_scores[0] == 1:
            print(f"\t⚠️ {self.youtube_url}")
        for warning in warnings_videos[0]:
            print(f"\t    {warning}")

    def _set_metadata(self):
        audiofile = eyed3.load(TEMP_ALBUM / self.mp3_file_name)
        audiofile.tag.clear()
        audiofile.initTag()
        audiofile.tag.title = self.title
        audiofile.tag.artist = self.artist
        audiofile.tag.album_artist = self.artist
        audiofile.tag.album = self.album_title
        audiofile.tag.track_num = self.track_number
        if self.album_art_path is not None:
            with open(self.album_art_path, "rb") as image:
                audiofile.tag.images.set(3, image.read(), "image/jpeg")
        audiofile.tag.save()
        print("\t✅ Set metadata")

    def _download_mp3(self):
        try:
            ut.print_song_title(self.title, self.track_number, self.duration)
            ydl_opts = {
                "format": "bestaudio/best",
                # yt-dlp always adds .mp3 suffix
                "outtmpl": str(TEMP_ALBUM / self.mp3_file_name).replace(".mp3", ""),
                "retries": 5,
                "fragment_retries": 5,
                "sleep_interval": 0,
                "max_sleep_interval": 1,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.youtube_url])

            if not ORGANIZE_SONGS:
                mp3_file_name_old = self.mp3_file_name
                # increment number in filename if a song of the same name already
                # exists in the SONGS directory (only if ORGANIZE_SONGS=false)
                while self.mp3_file_name in os.listdir(SONGS):
                    split_filename = self.mp3_file_name.split(".")
                    split_filename[-2] = str(int(split_filename[-2]) + 1)
                    self.mp3_file_name = ".".join(split_filename)
                shutil.move(
                    TEMP_ALBUM / mp3_file_name_old,
                    TEMP_ALBUM / self.mp3_file_name
                )

            print("\t✅ Downloaded mp3")
        except:
            print(f"💀 Failed to download .mp3 file")
            raise


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            description="Download an album by artist and album name or MusicBrainz release ID/release page URL"
        )
        parser.add_argument("--artist", type=str, help="Artist name")
        parser.add_argument("--album", type=str, help="Album name")
        parser.add_argument("--mbid", type=str, help="MusicBrainz release ID or release page URL")
        args = parser.parse_args()
        if args.mbid:
            if args.artist or args.album:
                parser.error("💀 Cannot use --mbid with --artist or --album")
        elif args.artist and args.album:
            pass
        else:
            parser.error("💀 You must provide either --mbid OR both --artist and --album")

        ARTIST = args.artist
        ALBUM_TITLE = args.album
        RELEASE_ID = ut.validate_release_id(parser, args.mbid)

        album = Album(
            artist=ARTIST,
            album_title=ALBUM_TITLE,
            release_id=RELEASE_ID,
        )
        if album.release_id is None:
            album.get_release_id()
            album.get_artist_and_album_title()
        else:
            album.get_artist_and_album_title()
        print(f"🎸 Artist:\t{album.artist}")
        print(f"💿 Album:\t{album.album_title}")
        ut.print_release_id(album.release_id)
        album.get_album_art()
        album.get_track_list()

        while True:
            user_input_urls = input(
                "🔗 Get YouTube URLs? [y]es/(n)o/(m)odify Musicbrainz release ID: "
            ).lower()
            if user_input_urls == "y" or user_input_urls == "":
                album.get_youtube_urls()
                break
            elif user_input_urls == "n":
                exit()
            elif user_input_urls == "m":
                user_input_release_id = input("Enter new Musicbrainz release ID or URL: ")
                album.release_id = ut.validate_release_id(parser, user_input_release_id)
                ut.print_release_id(album.release_id)
                album.get_album_art()
                album.get_track_list()
            else:
                continue

        while True:
            user_input_download = input(
                "🎶 Download songs? [y]es/(n)o/(m)odify YouTube URLs: "
            ).lower()
            if user_input_download == "y" or user_input_download == "":
                album.download_mp3s()
                break
            elif user_input_download == "n":
                exit()
            elif user_input_download == "m":
                while True:
                    user_input_track_number = input(
                        "Enter track number of song with URL you want to modify/(c)ancel: "
                    ).lower()
                    if user_input_track_number == "c":
                        break
                    try:
                        track_index = int(user_input_track_number) - 1
                        song = album.track_list[track_index]
                        ut.print_song_title(song.title, song.track_number, song.duration)
                        print(f"\t❓ {song.youtube_url} (Old URL)")
                    except:
                        print("Invalid track number, try again")
                        continue
                    user_input_url = input("Enter new YouTube URL/(c)ancel: ")
                    if user_input_url == "c":
                        break
                    song.youtube_url = user_input_url
                    ut.print_song_title(song.title, song.track_number, song.duration)
                    print(f"\t✅ {song.youtube_url} (New URL)")
                    break
            else:
                continue

    except:
        raise
    finally:
        print("🧹 Cleaning up")
        for temp_dir in [TEMP_ALBUM, TEMP_ART]:
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)
    print("🎷 Enjoy!")
