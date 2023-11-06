# -*- coding: utf-8 -*-

'''
Launch the GUI to add musics from Youtube
See the readme for setup: you must have Youtube open in a web browser instance running on port 9222.
Make sure you have at least one playlist file in the "./playlists" folder.
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from symp.SYMP import Add_MusicGUI

print()
print('='*60)
print("Warning:")
print()
print("> Make sure you have at least one playlist file in the './playlists' folder.")
print()
print("> You must have Youtube open in a web browser instance running on port 9222. Launch './launch_chrome.bat' or see the readme for setup example.")
print('='*60)
print()

## Connect to existing chrome session (must be running on port 9222)
chrome_options = Options()
# initialize the driver on a specific port to connect the driver class to an already existing chrome session (that may have been opened externaly for example)
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

# sanity check: verify that we are connected to the correct running driver using its current url
print(driver.current_url)
actions = ActionChains(driver)
# wait until driver's current session is ready
driver.implicitly_wait(10)
##

## Build the playlist window
# dictionnary containing keyboard shortcuts to quickly add musics to playlists
shortcut_path = 'shortcuts.txt'
# create the GUI
GUI = Add_MusicGUI('./playlists/', shortcuts='shortcuts.txt', driver=driver)
# enter mainloop
GUI.mainloop()
##
