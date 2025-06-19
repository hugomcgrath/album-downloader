# Album downloader (Looking for a good name!)

This tool was born of my stubborn refusal to use music streaming services like a normal person. I would use an online [YouTube to .mp3 convertor](https://ytmp3.as/) and paste in youtube links to download the .mp3 files one by one. I would then usually have to rename the file and manually set the metadata. As you can imagine, this was very frustrating and often I didn't bother. But every incorrectly set metadata tag, every wrong album art image slowly nibbled away at my sanity until one day I had to do something about it. Since I enjoy slapping together mediocre python code, I slapped together (with only moderate use of ChatGPT) a solution to all my music related problems - an album downloader!

As a side note, I also found that while listening to randomly shuffled songs I would just skip through many of them to avoid the emotinal whiplash of [*Down in a Hole*](https://www.youtube.com/watch?v=f8hT3oDDf6c) followed by [*Walking on Sunshine*](https://www.youtube.com/watch?v=iPUmE-tne5U) (or the other way around). I find that listening to full albums is quite a different and rewarding experience since an album is usually thematically consistent. I want to push myself more toward this way of engaging with music. When selecting music to download I would often cherry pick a handfull of songs while completely ignoring the rest of an artists œuvre and making myself listen to a full album gives me a better idea about an artist as a whole. Perhaps I can get some of you to come around to this way of thinking about music.

Thank you for reading my manifesto.

## How it works

The user inputs the artist name and album title OR the Musicbrainz release URL and the code does the rest. First it finds the album tracklist and album art from the [Musicbrains database](https://musicbrainz.org/), then it uses the [YouTube Data API](https://developers.google.com/youtube/v3) to search for the songs and tries to get the best match, then downloads the .mp3 files using the [YouTube to .mp3 convertor](https://ytmp3.as/) and finally sets the correct metadata including album art for each .mp3 file! The .mp3 files and album art are saved in the directories you specify in the ```.env``` file. You can then just copy the .mp3 files to your phone and any music player app should be able to recognise the metadata and sort everything correctly. I strongly recommend the [Oto Music Player](https://play.google.com/store/apps/details?id=com.piyush.music&hl=cs), it doesn't show adds!

## Installation and usage

The project installation can seem a bit complicated but bear with me! In the future I will try and find a way to simplify this setup.

1.  **Download the project**

    If you know how to use git, use:

    ```git clone https://github.com/hugomcgrath/album-downloader.git```

    in your desired directory, otherwise click on the green <> Code button and click Download ZIP. Then unzip the file in your desired directory.

2.  **Get the YouTube API key**

    This project uses the YouTube Data API and this means you, the user, need to supply your own API key. Follow the instructions [here](https://developers.google.com/youtube/v3/getting-started). Once you get your API key, copy it into the ```.env.example``` file provided in the project directory and follow the instructions in the file.

3.  **Install Miniconda**

    To manage all the python packages this project uses I use the ```conda``` package manager. Miniconda is a light-weight distribution of this package manager. Follow the installation instructions [here](https://www.anaconda.com/docs/getting-started/miniconda/install). If you don't want the (base) environment to activate each time you open your command prompt, run this:

    ```conda config --set auto_activate_base false```

4.  **Install the ```conda``` environment**

    Run ```conda env create -f environment.yaml``` to create a conda environment and install all the required python packages into it. It's possible this may take a while.

5.  **Activate the ```conda``` environment**

    Run ```conda activate album-downloader-env```.

6.  **Navigate to src/ in the project directory**

7.  **Run get_album.py**

    Hooray! If all the previous steps went smoothly, you can now finally start using the album downloader. There are two ways to use it.

    1.  Supply artist name and album title (example):

        ```python get_album.py --artist "Michael Gira" --album "Drainland"```

    2.  Supply the Musicbrainz release ID or the release page URL (example):

        ```python get_album.py --mbid 649b5e91-07f9-40d0-a209-9bb860f19b81```

        or alternatively:

        ```python get_album.py --mbid https://musicbrainz.org/release/649b5e91-07f9-40d0-a209-9bb860f19b81```

        The Musicbrainz release ID is just the last part of the release page URL.


## Limitations

Of course nothing is ever perfect in this vale of tears, the album downloader included. The biggest limitation is the fact that the YouTube API has a daily quota which means you will only be able to download approx. 90 songs a day.

Another problem is that YouTube search is not perfect, sometimes the returned URL won't be for the best version of the song (though I try to deal with this in the code). It works quite well for well known artists, it may struggle with lesser known ones. I eventually intend to add functionality to the program to allow users to modify the YouTube URL that will be used for the download.

The program should hopefully work on all PC platforms, but I only tried it out on Linux so there may be some issues I missed.

The Musicbrainz database may not have all Czech artists you may be interested in.

Please let me know if you encounter any bugs and I'll be happy to hear any suggestions on how to improve the album downloader (and suggestions for a good name). Enjoy! 🎷🎷🎷
