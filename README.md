# SYMP
SYMP (Soundboard for Youtube Music Playlists) allows you to quickly save the musics you're listening on Youtube in custome playlists, and later play these playlists using a Soundboard like GUI with customisable shortcuts and no Youtube ads.

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

**3 - Modify the pafy module**

This code relies on the pafy module (https://github.com/mps-youtube/pafy) to stream youtube music through the Python implementation of vlc.
Unfortunately, pafy has not been updated for quite a time and is under LGPLv3 licence, meaning I cannot distribute a modified version of pafy to work with this code.
You have thus to do the following modifications to the pafy module:

- navigate to the "Lib\site-packages\pafy" folder (the location of the "Lib" folder depends on your python installation and/or virtual environment setup)
- open the "backend_youtube_dl.py" file with any text editor and change the following lines:
  
```
[13] import youtube_dl
[53] self._likes = self._ydl_info['like_count']
[54] self._dislikes = self._ydl_info['dislike_count']
```

To:

```
[13] import yt_dlp as youtube_dl
[53] self._likes = self._ydl_info('like_count',0)
[54] self._dislikes = self._ydl_info('dislike_count',0)
```


**2 - Navigate to the "SYMP" folder. It should look like this:**

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



