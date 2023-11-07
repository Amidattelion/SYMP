# SYMP
SYMP (Soundboard for Youtube Music Playlists) allows you to quickly save the musics you're listening on Youtube in custome playlists, and later play these playlists using a Soundboard like GUI with customisable shortcuts and no Youtube ads.

# What ? Why ?

This code was motivated by several reasons: as a tabletop-RPG GameMaster, I love having lots of thematic playlists ready to launch for my player immersion: a playlist for epic fights, to explore a mysterious forest, or wandering in a cyberpunk city... Such playlists already exist on Youtube/Spotify/YourFavoriteStreamingWebsite, but I wanted something:
- without ads,
- with a soundboard like GUI and shortcuts to quickly start any playlist,
- highly customisable

Plus, I am a huge fan of film and video game soundtrack: modern OSTs are often orchestrated and they are by design created to serve the audience's immersion and stimulate its imagination. Listening to a lot of films OST and VGM compilations on Youtube, I wanted my tool to be able to connect to the running Youtube tab and allow me to quickly add the music I'm currently listening to any of my playlists with a simple click. 

With all of this in mind, I built this little tool:

![image](https://github.com/Amidattelion/SYMP/assets/87083034/b2a78161-19de-487d-8574-7d2d9d184ab6)

It comes with 2 versions of the same GUI: one that connects to a running Youtube session and allows to add the currently playing music (extracted from the other songs in the same video) to any of the registered playlists, and the other acting like a Soundboard with binded shortcuts to quickly launch any of my customs playlists without ads.

# Requirements:
- vlc (https://www.videolan.org/)
- git (https://git-scm.com/download/win)

You must define a git environment variable. On windows: 
- press Win+R
- write "SystemPropertiesAdvanced", press enter
- click on "Environment Variable"
- in the "user variables" pan (upper pan), click on "Path" and press "Edit"
- press "New" and add the following line: "C:\Program Files\Git\bin\" (this is the default path if you installed git for windows, otherwise change the path so it points toward the folder containing git.exe)

# Setup:
The code have only been tested on Windows, but should works on Linux.

**1 - Clone the repository with git (https://github.com/Amidattelion/SYMP.git) or download and extract it**

**2 - Install the requirements with pip:**

It is advised to first create and activate a dedicated virtual environment before proceeding.
Open a terminal and cd in the "SYMP" folder that you have just extracted, then run the following command to install the python dependencies:

```
$ pip install -r requirements.txt
```

This code relies on pafy, which has not been updated to the latest Youtube video format. We thus need to install a custom fork to fix the known "dislkike_count" bug from pafy:

```
$ pip install https://github.com/Amidattelion/pafy/archive/refs/heads/develop.zip
```

**3 - Navigate to the "SYMP" folder. It should look like this:**

![image](https://github.com/Amidattelion/SYMP/assets/87083034/cc5ec8e2-730a-498f-b023-8949726c6271)



**3 - (optional) Add playlist files:**

The code will scan the "playlists" folder for ".m3u" files to build the GUI, so the first thing to do is to create some empty playlists in the "playlists" folder. 
To do so simply open the "playlists" folder, right-click anywhere and create an empty text file. Rename the text file to "your_playlist_name.m3u" or any name you want, **but make sure it has the .m3u extension**.

There is already 4 working playlist example in the folder:
```
SYMP/Dubstep.m3u
SYMP/Rock.m3u
SYMP/Fight.m3u
SYMP/Forest.m3u
```

**4 - (optional) Setup the shortcuts**

You can link playlists with keyboard shortcuts. To do so, simply open the './shortcuts.txt' file in the "SYMP" directory and add a line with your playlist name, a ':' symbol and the shortcut.
The './shortcut.txt' file already have 4 lines corresponding to the examples playlists:

```
Rock.m3u 	: ctrl+f1
Dubstep.m3u	: ctrl+f2
Forest.m3u 	: ctrl+shift+f1
Fight.m3u 	: ctrl+shift+f2
```

The code will automatically organize the GUI based on the playlists found and their relative shortcuts.

# Play music

To play music, you can either launch the PlayMusic.py script or the PlayMusic.bat batch file (on Windows). This will open a GUI based on the .m3u files found in the "playlists" folder and the given shortcuts:

![image](https://github.com/Amidattelion/SYMP/assets/87083034/681b3f1b-781a-4920-ae8a-4908b9234bc2)

The GUI contains buttons (one per playlist in the folder): clicking one will launch the playlist using python-vlc to connect to youtube, hence enjoying your music without the ads !

Playlists for which shortcuts have been provided are arranged in a grid: in the example, pressing 'ctrl+f1' will launch the 'Rock' playlist

The right panel displays current playlist's music list: you can double click a music to play it, and search for a specific music using the blank field above the list.

The "loop current" button is a switch: when active, the music currently playing will loop until the button is unticked.

Advanced options can be setup for playlist buttons such as colors or playing behavior, these are described in the "Advanced Setup" section.

The music player comes with some shortcuts to control the playlist:
- ctrl+right arrow : skip to next music in playlist
- ctrl+left arrow  : previous song
- ctrl+down arrow  ! pause/unpause
- alt+page up      : increase volume
- alt+page down    : decrease volume

# Add Music

Adding music to a playlist requires to first launch the chrome web browser on the port 9222 in order for the python script to connect to the browser:

- On Windows, you can either run "launch_chrome.bat" or open a command prompt and run the following command:

```
$ start chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\selenum\ChromeProfile
```
Note that you may need to define chrome.exe in the PATH environment variable.

- On Linux, enter a terminal and run this command:

```
$ google-chrome --remote-debugging-port=9222 &
```

Once your chrome browser is running, use it to navigate to Youtube and pick a music video. The code supports three video format:

- **single music video:** the video contains a single music

  ![image](https://github.com/Amidattelion/SYMP/assets/87083034/6a303979-acc7-40f9-8acf-176ca669dd1a)

- **music video with chapters:** the video contains several musics identified with youtube chapters

![image](https://github.com/Amidattelion/SYMP/assets/87083034/02684328-5bbb-409c-bc69-63317a5bb4a1)

- **music video with tracklist in description:** the video contains several musics and the video description contains the tracklist with timecodes.

![image](https://github.com/Amidattelion/SYMP/assets/87083034/52442e63-9f85-4af5-b8e0-cee39956e455)

When your video is ready and running on youtube, launch the "AddMusic.py" script (or AddMusic.bat on Windows). The code will build up the AddMusic GUI:

![image](https://github.com/Amidattelion/SYMP/assets/87083034/8f77dfff-b9e7-4013-a098-a08afd4c11ae)

In this GUI, clicking a playlist button will add the music currently playing in Youtube to the associated playlist. In the above cases of a video containing several musics identified with chapters or a tracklist in description, the appropriate name and timecodes corresponding to the music currently playing will be extracted from the full video before being added to the playlist: you will not add the full video but only the section containing the title you are currently listening to.

Once a music has been added to a playlist, the button will still displayed in its "pressed" state while the music is still playing. This allows you to quickly identify if the music currently playing has already been saved to a playlist. If a pressed button is clicked again, the currently playing music will be removed from the corresponding playlist, and the button will regain its normal state.

![image](https://github.com/Amidattelion/SYMP/assets/87083034/ff5cfa31-77c5-43c6-9168-eace0e0e0da2)

In the above example, the music currently playing on youtube ("Title Screen Wii Play") has been added in the "Rock" playlist by the user. Clicking the "Rock" button again will remove this song from the playlist.

Finally, the AddMusic GUI contains a blank field under the name of the currently playing music. Whatever you type in this field will be added as a prefix to the currently playing music's title. This may be usefull for example when listening to videos containing several musics from the same artist/film/video game with chapter's name mentionning only the music title:

![image](https://github.com/Amidattelion/SYMP/assets/87083034/6a8dfbe6-1d10-4e97-8b8c-8c9957b6639d)

In the above example, the video contains several musics from Mario galaxy 1 but the chapter titles won't mention which video game is the music from. We hence add this information in the blank field to store it in the music's title.

# Advanced Setup

The first line in the playlist.m3u files can be used to further customize each playlist with arguments. To do so, add the following to the first line in a playlist file:

```
$ options = {"color" : "#a8a8a8", "autoplay" : False}
```

The color value is the color, in hex format, of the playlist's corresponding button in the GUI.
The autoplay option (True by default) determine wether the playlist automatically plays music when its button is pushed. Set it to False if you don't want the playlist to start automatically when clicking its button.

For example in the example "Fight.m3u" playlist:

```
$ options = {"color" : "#a8a8a8", "autoplay" : False}
https://www.youtube.com/watch?v=xi0M9SIaLb4&list=PLWXWbr9ex3iVqtmHSJ0OIeEnD2hOZnp2Q&index=9 # Xenoblade Chronicles OST - Engage the Enemy
https://www.youtube.com/watch?v=bgvywpXLDSg # Halo 3 - Warthog Run # 1104 # 1463
https://www.youtube.com/watch?v=dkTpqHLHk0c # With Mila’s Divine Protection – Super Smash Bros Brawl # 0 # 256
```

we see here the first line containing the options, followed by the playlist content: each music is described by its youtube url, its title, and optionnal start and stop timecodes to find the music in the video.


