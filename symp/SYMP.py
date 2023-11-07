# -*- coding: utf-8 -*-

"""
SYMP: a Soundboard for Youtube Music playlists

SYMP (Soundboard for Youtube Music Playlists) allows you to quickly save the musics you're listening on Youtube in custome playlists, and later play these playlists using a Soundboard like GUI with customisable shortcuts and no Youtube ads.

https://github.com/Amidattelion/SYMP

Copyright (C)  2013-2014 np1

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


# Modules, class & functions for the main program

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import os
import sys
import time
import keyboard
import pafy
import vlc
import json
import re
import numpy as np
import random as rd
import tkinter as tk
from tkinter import filedialog
from os import path
from functools import partial
from threading import Thread

## TO DO LIST :
# - add a "remove" feature to the Play GUI to remove current song from its playlist if needed
# - find a solution so that a playlist in autoplay will continue to play after playing a single song from it by double clicking the tracklist
# - add a readme, and/or labels in the GUI, with the shortcuts (ctrl+down to pause/unpause, ctrl+right for next song, ctrl+shift+q to stop current playlist, alt+page_up to increase volume, alt+page_down to decrease voume, double click on a song from the tracklist to play it specifically (will stop the playlist !))
# - improve the tracklist in the Play GUI so that it fit the whole space in the window
##

# Tkinter window containing the playlist buttons
class PlaylistWindow(tk.Tk):
    '''
    PlaylistWindow class
    This class is a children of tk.Tk class.
    Provided a directory, it will construct a tkinter window acting as a GUI to feed the
    program with the playlists files contained in the directory.
    '''
    def __init__(self, dir, use_shortcuts=None):
        # initialize this children class through the parent initialization process
        tk.Tk.__init__(self)
        self.title("SYMP")
        # the directory containing the playlists
        self.dir = dir
        # create the mainframe that hold both buttons & the log
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side='left',fill='y',expand=True,padx=20,pady=10)
        # create the console frame
        self.create_logframe()
        # load each playlist in the directory
        self.load(dir)
        # the dictionnary containing the shortcuts if any
        self.dic_shortcuts = None
        # create button widgets
        self.create_widgets(use_shortcuts)

    def create_widgets(self,use_shortcuts=None):
        '''
        Build the buttons widget, one per playlist in the directory.
        By default, buttons will be sorted in an arbitrary order. If a dictionnary containing
        shortcuts is provided in use_shortcuts, then buttons may be arranged intelligently
        according to their shortcuts (using the last key of the shortcut as column index, and the other first
        keys as row index). Playlist that are not linked to a shortcut will be displayed randomly under the
        other ones.
        '''
        # create the frame
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(fill='both', expand='True', padx = 20, pady = 10)

        self.buttons_dic = {}

        if use_shortcuts is None:
            col = 0
            row = 0
        else:
            self.dic_shortcuts = read_shortcuts(use_shortcuts)
            shortcuts = list(self.dic_shortcuts.values())
            # get column index = all possible last key in given shortcuts combination
            col_labels = list(dict.fromkeys([el.split('+')[-1] for el in shortcuts])) # converting to dic type with dict.from_keys then back to list allows to remove all duplicate in the list
            # sort column labels
            col_labels.sort(key=natural_keys)
            # get row index
            row_labels = list(dict.fromkeys(['+'.join(el.split('+')[:-1]) for el in shortcuts]))
            # place labels
            for index,current_label in enumerate(col_labels):
                label = tk.Label(self.button_frame,text=current_label)
                label.grid(column=index+1,row=0,sticky='NSEW')
            for index,current_label in enumerate(row_labels):
                label = tk.Label(self.button_frame,text=current_label)
                label.grid(column=0,row=index+1,sticky='NSEW')

            col = 1
            row = len(row_labels)+1

        for playlist in self.content:
            # get button background color
            if (playlist.options is not None) and ('color' in playlist.options.keys()):
                back_color = playlist.options['color']
            else:
                back_color = "white"

            # create button
            self.buttons_dic[playlist] = tk.Button(self.button_frame,text=playlist.name,bg=back_color,fg="black")

            # put it in the correct place
            if use_shortcuts is None:
                self.buttons_dic[playlist].grid(column=col%5,row=row,sticky='NSEW')
                col += 1
                if(col%5==0): row += 1

            else:
                if playlist.name+'.m3u' in self.dic_shortcuts.keys():
                    shortcut = self.dic_shortcuts[playlist.name+'.m3u']
                    shortcut_col_label = shortcut.split('+')[-1]
                    shortcut_row_label = shortcut.replace('+'+shortcut_col_label,'')
                    col_index = col_labels.index(shortcut_col_label) + 1
                    row_index = row_labels.index(shortcut_row_label) + 1
                else:
                    col_index = col%len(col_labels) + 1
                    row_index = row + 1
                    col += 1
                    if(col%len(col_labels)==0) : row +=1

                self.buttons_dic[playlist].grid(column=col_index,row=row_index,sticky='NSEW',padx=2,pady=2)

                # weighting so that the frame adjust to main window size
                self.button_frame.grid_rowconfigure(row_index,weight=1)
                self.button_frame.grid_columnconfigure(col_index,weight=1)

    def create_logframe(self):
        # create the frame
        self.log_frame = tk.Frame(self.main_frame, bg = 'white')
        self.log_frame.pack(side = "bottom", fill='both', expand='True', padx = 20, pady = 10)
        # create the scrollbar
        self.scrollbar = tk.Scrollbar(self.log_frame)
        self.scrollbar.pack(side = 'right', fill = 'y')
        # create the text widget that will receive the log
        self.log = tk.Text(self.log_frame, yscrollcommand = self.scrollbar.set)
        self.log.pack(fill='both', expand='True')
        self.log.bind("<Key>", lambda e: "break") # overwritte behavior for key press to prevent user from editing the text inside
        # link the scrollbar to the view command for the text
        self.scrollbar.config(command = self.log.yview)

    def write_log(self,entry):
        '''
        Write the given entry in the log frame
        '''
        # add the new entry
        self.log.insert('end',entry)
        # focus on the end of the text
        self.log.see('end')

    def load(self,dir):
        # load all playlists in directory
        self.content = []
        list_playlist = os.listdir(dir)
        self.write_log(f"Loading playlists in .m3u format from '{dir}' :\n")
        for playlist_name in list_playlist:
            if not '.m3u' in playlist_name: continue
            playlist = Playlist(dir+playlist_name)
            self.content.append(playlist)
            self.write_log(f'Loaded {playlist.name}.m3u, {len(playlist.content)} songs')
            print(f'Loaded {playlist.name}.m3u, {len(playlist.content)} songs')
            if playlist.options is None: self.write_log('\n')
            else: self.write_log(f' with options : {playlist.options}\n')

# GUI to add musics to playlists
class Add_MusicGUI(PlaylistWindow):
    def __init__(self, dir, shortcuts, driver):
        # initialize the parent class
        PlaylistWindow.__init__(self, dir, use_shortcuts=shortcuts)
        self.driver = driver
        # connect each GUI button to the add_to_playlist function and link it with the corresponding shortcut if any
        for playlist, button in self.buttons_dic.items():
            button.configure(command = partial(self.add_to_playlist,playlist))
            # if any shortcut exist for this playlist, we connect it to the function
            try:
                shortcut = self.dic_shortcuts[playlist.name + '.m3u']
                keyboard.add_hotkey(shortcut,partial(self.add_to_playlist,playlist))
            except Exception as e:
                print(e)
                pass
        # add a field to print currently playing music
        self.currently_playing_frame = tk.Frame(self.main_frame)
        self.currently_playing_frame.pack(fill='both', expand='True', padx=20, pady=10)
        self.currently_playing_field = tk.Text(self.currently_playing_frame, height=1, bg=self.cget('bg'), bd=0) # height option in line number
        self.currently_playing_field.bind("<Key>", lambda e: "break") # overwritte behavior for key press to prevent user from editing the text inside
        self.currently_playing_field.pack(fill='x', expand='True')
        # add a field to add a prefix name for all musics added (for example the video game title if not present)
        self.title_prefix_frame = tk.Frame(self.main_frame)
        self.title_prefix_frame.pack(fill='both',expand='True',padx=20,pady=20)
        self.title_prefix_field = tk.Text(self.currently_playing_frame, height=1, bg='white')
        self.title_prefix_field.pack(fill='x', expand='True')
        # launch update process on a separate thread
        self.update_thread = Thread(target = self.update_gui)
        self.stop_thread = False
        self.update_thread.start()
        # create protocol for closing window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_to_playlist(self, playlist):
        '''
        find the youtube music video or chapter currently playing in the connected driver
        and add it to the given playlist. Return True if current track has been added, False otherwise.
        '''
        url, video_title, time_start, time_stop = self.get_current_music_info()
        # check if music already in playlist, and abort if so
        if video_title in [track.name for track in playlist.content]:
            self.write_log(f'"{video_title}" already in {playlist.name} !\n')
            return(False)

        entry = f"{self.driver.current_url} # {video_title}"
        if time_start is not None:
            entry += f" # {time_start}"
        if time_stop is not None:
            entry += f" # {time_stop}"
        entry += '\n'

        with open(playlist.path,'r+',encoding='utf-8') as f:
            # add to playlist file
            f.readlines()
            f.write(entry)
            # also update the corresponding playlist object
            playlist.content.append(Track(self.driver.current_url,video_title,time_start,time_stop))
            self.write_log(f'"{video_title}" added to {playlist.name}.m3u !\n')
            return(True)

    def has_chapter(self):
        '''
        Return True if the currently active tab in given driver is a youtube video
        with chapters
        '''
        # show the chapters list, otherwise it will not be visible for next commands
        self.driver.execute_script("(arguments[0]).click();", self.driver.find_element(By.CLASS_NAME,'ytp-chapter-container'))
        # determine wether video has chapters or not
        if self.driver.find_element(By.CLASS_NAME,'ytp-chapter-title').text == '':
            has_chapter = False
        else:
            has_chapter = True

        return(has_chapter)

    def has_tracklist_in_desc(self):
        '''
        Return True if the currently active tab in given driver has the tracklist in video description
        '''
        try:
            # click the "plus" button to get full desc
            plus_button = self.driver.find_element(By.ID,"expand")
            self.driver.execute_script("(arguments[0]).click();", plus_button)
        except Exception as e:
            print(e)
            pass
        try:
            # get the description
            desc = self.driver.find_element(By.ID,'description-inline-expander')
            description = desc.text.split('\n')
            # extract the tracklist if their is one:
            tracklist = []
            for el in description:
                try:
                    int(el[0])
                    if(':' in el): tracklist.append(el)
                except :
                    pass
            if len(tracklist)>0:
                self.desc_tracklist = tracklist
                return(True)
            else:
                return(False)
        except Exception as e:
            print(e)
            return(False)

    def remove_from_playlist(self, playlist):
        '''
        Remove currently playing music from given playlist
        '''
        url, video_title, time_start, time_stop = self.get_current_music_info()
        with open(playlist.path,'r+',encoding='utf-8') as f:
            # copy playlist content
            copy_f = f.readlines()
            # get back to file's beginning
            f.seek(0)
            # rewrite file, omitting lines containing the entry
            for line in copy_f:
                try:
                    title = line.split(' # ')[1]
                    # remove space and '\n' to recognise identical title even if spaces are different
                    if video_title.replace(' ','') == title.replace(' ','').replace('\n',''):
                        self.write_log(f'ATTENTION : {title} removed from {playlist.name}.m3u !\n')
                        continue
                    else:
                        f.write(line)
                except Exception as E:
                    f.write(line)
            f.truncate()
            # reload playlist content
            playlist.load()

    def get_current_music_info(self):
        '''
        Get the following informations about the music currently playing in the connected driver:
        - url
        - music name (the video's title or the chapter name if any)
        - time at which the chapter start & stop (if any)
        These informations are then returned in this order : "url, name, time_start, time_stop", with missing values being None (for example for if no chapter has been found)
        '''
        # has chapters
        if self.has_chapter():
            # find the chapter list if it exist, otherwise return an error
            chapters = self.driver.find_element(By.CLASS_NAME,'style-scope ytd-macro-markers-list-renderer')
            # stop at -1 because last item is "Sync with video" button
            chapter_names = chapters.text.split('\n')[0:-1:2]
            chapter_times = chapters.text.split('\n')[1::2]
            current_index = 0
            # now find current chapter
            for index,name in enumerate(chapter_names):
                # compare each chapter name to the currently displayed text in the progress bar
                if name in self.driver.find_element(By.CLASS_NAME,'ytp-progress-bar').get_attribute('aria-valuetext'):
                    current_index = index
                    break
            # get chapter's name
            video_title = chapter_names[current_index] # current chapter title
            video_title.replace('#',' ') # to avoid messing with # in video title
            # get start time
            start_time  = 0 # current chapter starting time (in secondes)
            for k,element in enumerate(chapter_times[current_index].split(':')[::-1]):
                start_time += int(element) * 60**k
            # if there is a chapter after the current one, get stop time
            if current_index+1 < len(chapter_names):
                stop_time  = 0 # in secondes
                for k,element in enumerate(chapter_times[current_index+1].split(':')[::-1]):
                    stop_time += int(element) * 60**k
            else:
                stop_time = None

            # add prefix field content to video_title
            video_title = self.title_prefix_field.get("1.0","end-1c") + video_title # .get(1.0,end-1c) means read the prefix field input from the first character to the end -1 caracter (which is a line break)

            return(self.driver.current_url, video_title, start_time, stop_time)

        ## has tracklist in video description
        elif self.has_tracklist_in_desc():
            # get current video time
            while True:
                try:
                    current_time = [el for el in self.driver.find_elements(By.CLASS_NAME,"ytp-time-current") if ':' in el.text][0] # find the only element with that id that has a ':' in his text
                    current_time = convert_to_sec(current_time.text)
                    # search to what tracklist entry current playing music corresponds
                    for k,el in enumerate(self.desc_tracklist):
                        stop_time = convert_to_sec(el.split(' ')[0])
                        if stop_time > current_time:
                            curr_el = self.desc_tracklist[k-1]
                            start_time = convert_to_sec(curr_el.split(' ')[0])
                            video_title = ' '.join(curr_el.split(' ')[1:]).replace('-','').replace('~','')
                            break
                    # add prefix field content to video_title
                    video_title = self.title_prefix_field.get("1.0","end-1c") + video_title # .get(1.0,end-1c) means read the prefix field input from the first character to the end -1 caracter (which is a line break)
                    return(self.driver.current_url, video_title, start_time, stop_time)
                except Exception as e:
                    print(e)
                    pass

        ## has no chapters
        else :
            video_title = self.driver.find_element(By.CLASS_NAME,'style-scope ytd-watch-metadata').text.split('\n')[0]
            video_title.replace('#','').replace(';',' ') # to avoid messing with # in video title
            # if current music already in given playlist, warn and abort
            # add prefix field content to video_title
            video_title = self.title_prefix_field.get("1.0","end-1c") + video_title # .get(1.0,end-1c) means read the prefix field input from the first character to the end -1 caracter (which is a line break)
            return(self.driver.current_url, video_title, None, None)

    def update_gui(self):
        '''
        Check the currently opened connected browser to update the current playing song
        '''
        while not self.stop_thread:
            # get current music info
            url, video_title, time_start, time_stop = self.get_current_music_info()
            # update the music info field
            self.currently_playing_field.delete('1.0','end')
            self.currently_playing_field.insert('1.0',f'Currently playing : {video_title}')
            self.currently_playing_field.see('1.0')
            # update buttons aspect for playlist already containing the music
            for playlist, button in self.buttons_dic.items():
                if video_title in [track.name for track in playlist.content]:
                    button.configure(relief='sunken')
                    button.configure(command = partial(self.remove_from_playlist,playlist))
                else:
                    button.configure(relief='raised')
                    button.configure(command = partial(self.add_to_playlist,playlist))
            # apply update to window
            self.update_idletasks()
            time.sleep(0.2)
        return()

    def on_closing(self):
        # handles closing GUI window event
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            # stop loop in update_thread. The thread will close the window and close itself before terminating program
            self.stop_thread = True
            # close currently active window
            self.destroy()
            # wait for update Thread to close
            print('Closing...')
            self.update_thread.join()
            # exit thread
            sys.exit()

# GUI to play playlists
class Play_MusicGUI(PlaylistWindow):
    def __init__(self, dir, shortcuts):
        # initialize the parent class
        PlaylistWindow.__init__(self, dir, use_shortcuts=shortcuts)
        # initialize the vlc player, with 'prefer-insecure' set as an Instance option to preferentially use http instead of https, thus avoiding some connection issues
        self.vlc_object = VLC(['prefer-insecure','--no-video','--mkv-seek-percent'])
        # initialize the vlc thread
        self.vlc_thread = None
        # create a frame to handle the track list
        self.tracklist = Tracklist(self, pack_options={'side':'right', 'padx':20, 'pady':10})
        # link double click in tracklist event to play corresponding track
        self.tracklist.lbox.bind('<Double-Button>',self.play_track_with_thread)
        # playlist currently playing
        self.current_playlist = None
        # add a field to print currently playing music
        self.currently_playing_frame = tk.Frame(self.main_frame)
        self.currently_playing_frame.pack(fill='x', padx=20, pady=10)
        self.current_track_name = tk.StringVar(self.main_frame)
        self.current_track_name.set('Currently playing :')
        self.currently_playing_field = tk.Label(self.currently_playing_frame, textvariable=self.current_track_name, height=1, bg=self.cget('bg'), bd=0, anchor='w') # height option in line number
        self.currently_playing_field.pack(fill='x')
        # loop box : if active, current song will loop until untick
        self.loop_var = tk.IntVar() # whether to infinitely loop on current media
        self.loop_box = tk.Checkbutton(self.tracklist, text='loop current',variable=self.loop_var, command=self.set_loop)
        self.loop_box.grid(row=2,column=0,padx=10,pady=10,sticky='NSEW')
        # hotkey to stop playlist
        keyboard.add_hotkey('ctrl+shift+q',self.stop_current)
        # connect buttons to commands and shortcuts
        for playlist, button in self.buttons_dic.items():
            button.configure(command = partial(self.play,playlist))
            # if any shortcut exist for this playlist, we connect it to the function
            try:
                shortcut = self.dic_shortcuts[playlist.name + '.m3u']
                keyboard.add_hotkey(shortcut,partial(self.play,playlist))
            except Exception as e:
                print(e)
                pass
        # create protocol for closing window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def play(self, playlist):
        # stop currently playing playlist if any
        self.stop_current()
        # define the thread used to play vlc music
        self.vlc_thread = Thread(target = playlist.play, args = [self.vlc_object,self.current_track_name])
        # launch thread
        self.vlc_thread.start()
        self.current_playlist = playlist
        # update tracklist frame
        self.tracklist.list = [track.name for track in playlist.content]
        self.tracklist.update_list()
        # write log
        self.write_log(f'Starting playing {playlist.name}.m3u\n')

    def play_track_with_thread(self, event):
        # first, stop current track but keep tracklist
        self.stop_current(abandon_playlist = False)
        self.vlc_object.set_stop()
        # define the thread used to play vlc music
        self.vlc_thread = Thread(target = self.play_track)
        # launch thread
        self.vlc_thread.start()

    def play_track(self):
        # play a single track given its index in its playlist
        track_name = self.tracklist.lbox.get(self.tracklist.lbox.curselection())
        track_index = [track.name for track in self.current_playlist.content].index(track_name)
        track = self.current_playlist.content[track_index]
        self.write_log(f'Starting playing {track.name}\n')
        # update currently_playing field
        self.current_track_name.set(f'Currently playing: {track.name}')
        track.play(self.vlc_object)

    def stop_current(self, abandon_playlist = True):
        # stop currently playing playlist
        if not self.current_playlist is None:
            # stop playlist
            self.current_playlist.stop(self.vlc_object)
            # empty tracklist
            if abandon_playlist:
                self.write_log(f'Stopped {self.current_playlist.name}.m3u\n')
                self.current_playlist = None
                self.tracklist.lbox.delete(0,'end')
        else:
            pass

    def set_loop(self):
        self.vlc_object.loop = self.loop_var.get()

    def on_closing(self):
        # handles closing GUI window event
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            # stop current playlist
            self.stop_current()
            # stop player
            self.vlc_object.set_stop()
            # wait for thread to stop
            if not self.vlc_thread is None:
                self.vlc_thread.join()
            # close currently active window
            self.destroy()
            # exit
            sys.exit()

# Tkinter window containing the current playlist
class Tracklist(tk.Frame):

    def __init__(self, master=None,list=[],pack_options={}):
        tk.Frame.__init__(self, master)
        self.list = list
        self.pack(**pack_options)
        self.create_widgets()


    # Create main GUI window
    def create_widgets(self):
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_list())
        self.entry = tk.Entry(self, textvariable=self.search_var, width=13)
        self.lbox = tk.Listbox(self, width=45, height=15)
        # self.title = tk.Label()

        # self.instructions = "Press:\nCTRL+UP to raise volume\nCTRL+DOWN to lower volume\nCTRL+P to pause\n CTRL+R to resume\nCTRL+RIGHT to play next song\nCTRL+Q to stop playing this playlist"
        # self.label = tk.Label(self,text=self.instructions)
        # self.label.grid(row=0, column=1)

        self.entry.grid(row=0, column=0, sticky = 'ew', padx = 20, pady = 10 ) #padx=20, pady=3
        self.lbox.grid(row=1, column=0, sticky='swe', padx = 20, pady = 10)

        # Function for updating the list/doing the search.
        # It needs to be called here to populate the listbox.
        self.update_list()

    def update_list(self):
        search_term = self.search_var.get()

        self.lbox.delete(0, tk.END)
        lbox_list = self.list

        for item in lbox_list:
            if search_term.lower() in item.lower():
                self.lbox.insert(tk.END, item)

# Playlist class
class Playlist():
    def __init__(self,path):
        if not '.m3u' in path: raise ValueError(f'Playlist {path} is not in .m3u format.')
        self.path = path
        self.name = path.split('/')[-1].replace('.m3u','')
        self.stop_playlist = None
        # load playlist content
        self.load()
        # current playing track
        self.current_track = None
        self.current_track_name = tk.StringVar()

    def load(self,encoding='utf-8'):
        '''
        Load the content from the playlist.

        First line in a playlist.m3u file can contain specific options to tell the program how to handle it.
        In this case, the first line must be in the form '$ options = {"option_1" : "string_value", "option_2" : int_value}'
        Pay attention that all strings must be in double quote mark "" and that the beginning '$ options = ' must be exactly written in this form
        Available options are :
         - color     : color string or HEX value supported by tkinter. Example : {"color" : "white"} ; {"color" : "#54FA9B"}
         - autoplay : whether the playlist should automatically start once loaded or wait for user to launch it by picking a song.
                       Accept boolean, True by default, so to prevent autoplay on start just add : {"auto_play" : False} in options.
         - track_number : number of track that will be played in playlist. By default all tracks are played
        '''
        valid_options = ['color','autoplay','track_number']
        self.content = []
        with open(self.path,'r',encoding=encoding) as f:
            file_content = f.readlines()
            if len(file_content) == 0: # if file is empty
                self.options = None
            # handle options if any
            elif '$options=' in file_content[0].lower().replace(' ',''):
                options_string = file_content[0].lower().replace(' ','').replace('$options=','').replace('\'','"')
                self.options = json.loads(options_string)
                for key in self.options.keys():
                    if not key in valid_options:
                        raise ValueError(f'Error reading {self.path} : invalid option "{key}". Valid options are : {valid_options}')
            else:
                self.options = None
                first_track = Track(*file_content[0].split(' # '))
                self.content.append(first_track)

            # load content
            for line in file_content[1:]:
                track = Track(*line.replace('\n','').split(' # '))
                self.content.append(track)

    def play(self,vlc_object,track_name_string_var):
        '''
        Play the track inside playlist in random order until stop_playlist is set to True by external class
        '''
        if (self.options is not None) and ('autoplay' in list(self.options.keys())):
            if self.options['autoplay'] == True:
                self.stop_playlist = False
            else:
                self.stop_playlist = True # if autoplay is off, don't start the playlist
        else:
            self.stop_playlist = False

        if (self.options is not None) and ("track_number" in list(self.options.keys())):
            shuffled_content = rd.sample(self.content,self.options["track_number"])
            for track in shuffled_content :
                if self.stop_playlist:
                    break
                try:
                    track_name_string_var.set(f'Currently playing: {track.name}') # set the provided string var variable (from another class) to current track name
                    track.play(vlc_object)
                    self.current_track = track
                except Exception as e:
                        print(f'/!\ "{track.name}" did not play')
                        write_unavailable_musics(exception=e,track=track)

        else:
            while not self.stop_playlist:
                shuffled_content = rd.sample(self.content,len(self.content))
                for track in shuffled_content :
                    if self.stop_playlist:
                        return()
                    try:
                        track_name_string_var.set(f'Currently playing: {track.name}') # set the provided string var variable (from another class) to current track name
                        track.play(vlc_object)
                        self.current_track = track
                    except Exception as e:
                        print(f'/!\ "{track.name}" did not play')
                        write_unavailable_musics(exception=e,track=track)

    def update_currently_playing_frame(self,string_var):
        # given a string_var variable from another class, set it to currently playing track name
        string_var.set()

    def stop(self,vlc_object):
        self.stop_playlist = True
        # self.current_track_name.trace_remove(*self.current_track_name.trace_info()[0]) # remove the tracing of current track name (which was linked to the currently playing field of GUI)
        vlc_object.set_stop()

# Track class
class Track():
    def __init__(self,url,name,time_start=None,time_stop=None):
        self.url = url
        self.name = name
        self.time_start = time_start
        self.time_stop = time_stop

    def play(self,vlc_object):
        # play the track using the given vlc_object
        media_options = {}
        if self.time_start is not None: media_options['start-time']=self.time_start
        if self.time_stop is not None: media_options['stop-time']=self.time_stop

        vlc_object.play_url(self.url,media_options)

# VLC class
class VLC():
    def __init__(self,args):
        # prefer-insecure allows to preferentially use http instead of https to avoid network error
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()
        # stop attribute to stop current media on shortcut
        self.stop = None
        # wether to loop on current media or not
        self.loop = False
        # bind shortcuts
        self.bind_shortcuts()

    def play_url(self,url,media_options = {}):
        '''
        Use vlc player to play given url. Options is a dictionnary containing optionnal options to be passed to the vlc Media such as time-start or time-stop.
        '''
        video = pafy.new(url)
        # best = video.getbestaudio()
        best = video.getbest() # use getbest instead of getbestaudio seems to solve the mp4 demux discontinuity issue
        playurl = best.url
        Media = self.Instance.media_new(playurl)
        for option_name, option_value in media_options.items():
            Media.add_option(f'{option_name}={option_value}')
        while True:
            self.player.set_media(Media)
            self.player.play()
            self.stop = False
            # play untile self.stop() is called or media is over
            while not (self.stop or self.player.get_state() == vlc.State.Ended):
                time.sleep(0.2)
            # stop player
            self.player.stop()
            if not self.loop:
                break
            time.sleep(0.2)

    def set_stop(self):
        '''
        If a media is currently playing, calling this function will stop the player
        '''
        self.stop = True

    def raise_vol(self):
        if self.player.audio_get_volume() <= 95:
            self.player.audio_set_volume(self.player.audio_get_volume()+5)
        else:
            self.player.audio_set_volume(100)

    def lower_vol(self):
        if self.player.audio_get_volume() >= 5 :
            self.player.audio_set_volume(self.player.audio_get_volume()-5)
        else:
            self.player.audio_set_volume(0)

    def bind_shortcuts(self):
        keyboard.add_hotkey('ctrl+down',self.player.pause)
        keyboard.add_hotkey('ctrl+right',self.set_stop)
        keyboard.add_hotkey('alt+page_up',self.raise_vol)
        keyboard.add_hotkey('alt+page_down',self.lower_vol)

# reconnect to existing driver session, for example when opening a web browser through windows console -> should be deleted, as we don't use it ?
def attach_to_session(executor_url, session_id):
    original_execute = WebDriver.execute
    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return original_execute(self, command, params)
    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    driver.session_id = session_id
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver

# read shortcuts in the given file and return a dictionnary
def read_shortcuts(path,encoding='utf-8'):
    '''
    Read shortcuts in a file given its path and return a dictionnary
    whose keys are the different playlist names and their corresponding
    keyboard shortcut as their keys.

    File format must be the following:
    playlist_name.m3u : keyboard_shortcut

    For example, let have a shortcut.txt file containing the following:
    my playlist 1 : shift+f1
    my playlist 2 : alt+f2
    my playlist 3 : ctrl+shift+k
    '''
    shortcut = {}
    with open(path,'r+',encoding=encoding) as f:
        for l in f.readlines():
            file,key = l.split(' : ')
            key = key.replace('\n','')
            shortcut[file]=key
    return(shortcut)

# sorting tools
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def write_unavailable_musics(exception,track,log_file='./unavailable_musics.txt'):
    # write in a log file the list of unavailable songs
    with open(log_file,'a+',encoding='utf-8') as f:
        entry = '-'*10+f'\nDidn\'t played : {track.name}; {track.url}; {track.time_start}; {track.time_stop}\nIssue : {exception}\n'+'-'*10+'\n'
        content = f.readlines()
        if not entry in content:
            f.write(entry)
            content.append(entry)

def convert_to_sec(text):
    '''
    convert a text in the hh:mm:ss or mm:ss format to the corresponding nb of second in a int variable
    '''
    time = 0
    for k,el in enumerate(text.split(':')[::-1]):
        time += int(el)*(60**k)
    return(time)
