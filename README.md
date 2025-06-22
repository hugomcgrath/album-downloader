## ⚠️ Possibly breaking change ⚠️

I have changed the way songs are saved to the ```SONGS_DIRECTORY```, now instead of downloading everything into one flat directory, it is structured the following way: ```SONGS_DIRECTORY/artist/album_title/songs/track_number.song_title.mp3``` and the ```ALBUM_ART_DIRECTORY``` is moved to ```SONGS_DIRECTORY/artist/album_title/album_art/album_title.jpg```.

### What do I have to do?

First of all, modify your ```.env``` file according to the new ```.env.example``` template. If you want to use the new directory organization structure, it is important you set the ```ORGANIZE_SONGS``` flag to ```true```.

If you've used ```src/get_album.py``` to download albums before, you can migrate to the new directory structure by running ```src/migrate.py``` (as long as you didn't rename the .mp3 files).

# 💿 Album downloader (Looking for a good name!)

This tool was born of my stubborn refusal to use music streaming services like a normal person. I don't like that more and more services use the subscription model and I don't want to support it. The alternatives often aren't great. The way I did things before, I would use an online [YouTube to .mp3 convertor](https://ytmp3.as/) and paste in YouTube links to download the .mp3 files one by one. I would then usually have to rename the file and manually set the metadata. As you can imagine, this was very frustrating and often I didn't bother. But every incorrectly set metadata tag, every wrong album art image slowly nibbled away at my sanity until one day I had to do something about it. Since I enjoy slapping together mediocre python code, I slapped together (with only moderate use of ChatGPT) a solution to all my music related problems - an album downloader!

As a side note, I also found that while listening to randomly shuffled songs I would just skip through many of them to avoid the emotinal whiplash of [*Down in a Hole*](https://www.youtube.com/watch?v=f8hT3oDDf6c) followed by [*Walking on Sunshine*](https://www.youtube.com/watch?v=iPUmE-tne5U) (or the other way around). I find that listening to full albums is quite a different and rewarding experience since an album is usually thematically consistent. I want to push myself more toward this way of engaging with music. When selecting music to download I would often cherry pick a handfull of songs while completely ignoring the rest of an artists œuvre and making myself listen to a full album gives me a better idea about an artist as a whole.

As a final thought, I realize this is probably not very nice towards artists, so I ask you to consider buying some physical music once in a while. Though it is extremely impractical (so I don't do it that often), I do very much enjoy listening to vinyl records. Putting on a vinyl and then changing sides is a little ritual of sorts. Sometimes it's nice to do things slowly. There's no prize for getting to the finish line first. I hope I can get some of you to come around to this way of thinking about music and taking things a little more slowly in life in general. Thank you for reading my manifesto.

## How it works

The user inputs the artist name and album title OR the Musicbrainz release URL and the code does the rest. First it finds the album tracklist and album art from the [Musicbrains database](https://musicbrainz.org/), then it uses the [YouTube Data API](https://developers.google.com/youtube/v3) to search for the songs and tries to get the best match, then downloads the .mp3 files using the [YouTube to .mp3 convertor](https://ytmp3.as/) and finally sets the correct metadata including album art for each .mp3 file! The .mp3 files and album art are saved in the directories you specify in the ```.env``` file. You can then just copy the .mp3 files to your phone and any music player app should be able to recognise the metadata and sort everything correctly. I strongly recommend the [Oto Music Player](https://play.google.com/store/apps/details?id=com.piyush.music&hl=cs), it doesn't show adds!

## Installation

The project installation can seem a bit complicated but bear with me! In the future I will try and find a way to simplify this setup.

1.  **Download the project**

    If you know how to use git, use:

    ```git clone https://github.com/hugomcgrath/album-downloader.git```

    in your desired directory, otherwise click on the green <> Code button and click Download ZIP. Then unzip the file in your desired directory.

    The ```git clone``` method is preferable, as it simplifies downloading the updates, you can just run ```git pull``` to get the latest version, otherwise you'll have to redownload the ZIP.

2.  **Get the YouTube API key**

    This project uses the YouTube Data API and this means you, the user, need to supply your own API key. Follow the instructions [here](https://developers.google.com/youtube/v3/getting-started). Once you get your API key, copy it into the ```.env.example``` file provided in the project directory and follow the instructions in the file.

3.  **Install Google Chrome**

4.  **Install Miniconda**

    To manage all the python packages this project uses I use the ```conda``` package manager. Miniconda is a light-weight distribution of this package manager. Follow the installation instructions [here](https://www.anaconda.com/docs/getting-started/miniconda/install). If you don't want the (base) environment to activate each time you open your command prompt, run this:

    ```conda config --set auto_activate_base false```

5.  **Install the ```conda``` environment**

    Run ```conda env create -f environment.yaml``` to create a conda environment and install all the required python packages into it.

## Usage

1.  **Navigate to src/ in the project directory**

2.  **Activate the ```conda``` environment**

    Run ```conda activate album-downloader-env``` to activate the conda environment. You need to do this again any time you open the terminal and want to run the album downloader.

3.  **Run get_album.py**

    Hooray! If all the previous steps went smoothly, you can now finally start using the album downloader. There are two ways to use it.

    1.  Supply artist name and album title (example):

        ```python get_album.py --artist "Michael Gira" --album "Drainland"```

    2.  Supply the Musicbrainz release page URL:

        ```python get_album.py --mbid https://musicbrainz.org/release/649b5e91-07f9-40d0-a209-9bb860f19b81```

        or the release ID (the last part of the release page URL):

        ```python get_album.py --mbid 649b5e91-07f9-40d0-a209-9bb860f19b81```


## Limitations

Of course nothing is ever perfect in this vale of tears, the album downloader included. The biggest limitation is the fact that the YouTube API has a daily quota which means you will only be able to download approx. 90 songs a day, that works out to roughly 7-8 albums a day. The quota resets at 09:00 CEST.

If you search for the album by ```--artist``` and ```--album```, there is a small chance the release (version of the album) may not be the one you want (sometimes different releases have songs added or removed, album art may be different). You can correct this, when asked ```🔗 Get YouTube URLs? [y]es/(n)o/(m)odify Musicbrainz release ID:```, input ```m``` and then paste in the correct Musicbrainz release ID or URL.

Another problem is that YouTube search is not perfect, sometimes the returned URL won't be for the best version of the song (though I try to deal with this in the code) or it may be the wrong video altogether. This is usually a problem with lesser known/obscure artists. If the program detects the YouTube video is not quite right, it will show a ⚠️ warning. This is a sign to you, the user, to check the link to see if it's the song version you want. If it isn't, when asked ```🎶 Download songs? [y]es/(n)o/(m)odify YouTube URLs:```, input ```m``` to modify the offending URL, first you select the song by inputing the track number and then you paste in the correct URL.

The program should hopefully work on all PC platforms, but I only tried it out on Linux so there may be some issues I missed.

The Musicbrainz database may not have all Czech artists you may be interested in.

Please let me know if you encounter any bugs and I'll be happy to hear any suggestions on how to improve the album downloader (and suggestions for a good name). Enjoy! 🎷🎷🎷
