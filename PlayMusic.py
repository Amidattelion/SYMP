# -*- coding: utf-8 -*-

'''
Launch the GUI to play the musics !
Build the PlayMusic GUI based on the "./playlists" folder content.
'''


import sys
from symp.SYMP import Play_MusicGUI

# IF ERROR LIKE "main libvlc error: stale plugins cache" ARE SPAMMING AT PROGRAM'S LAUNCH, HEAD TO YOUR VLC DIRECTORY
# (WHERE vlc.exe IS LOCATED) AND LAUNCH "vlc-cache-gen.exe" (WINDOWS), THEN LAUNCH PROGRAM AGAIN !
# IF IT STILL DOESN'T WORK, DELETE "plugin.dat" AT C:\Program Files\VideoLAN\VLC\plugins\plugin.dat

current_path = sys.path[0]
GUI = Play_MusicGUI('./playlists/',shortcuts='./shortcuts.txt')

print()
print('='*60)
print("Warning:")
print()
print("> Error has been detected in pafy since Youtube does not count dislikes anymore, but pafy has not been updated yet.")
print("> To manually correct this 'dislike_count' error, go in the python39\lib\site-packages\pafy\backend_youtube_dl.py file")
print("> and manually replace lines 53 & 54 by :")
print()
print("> 52:  self._likes = self._ydl_info.get['like_count', 0]")
print("> 53:  self._dislikes = self._ydl_info.get['dislike_count', 0]")
print()
print("> Also if error like 'unable to extract uploader id' shows, then install yt-dlp with pip install yt-dlp and replace all 'import youtube_dl' by 'import yt_dlp as youtube_dl' in all pafy's file (2 occurences). youtube-dl is not maintained anymore & yt-dlp aims at replacing it with an updated version following youtube evolution.'")
print('='*60)
print()

GUI.mainloop()
