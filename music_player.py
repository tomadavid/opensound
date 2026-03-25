import os
import subprocess
import json
from ytmusic import *
from mpv_socket import *
from graphics import *
import multiprocessing
import threading
import time
from playlists import add_song_to_playlist, store_playlist
from stats import update_statistics

########################
# Song playing methods #
########################

# plays a song 
def play_song(song):
    """
    plays a song inside a subprocess using mpv command

    :param song -> (title, artist, album, duration_string, url, album_cover_url)
    
    returns process playing the song, mpv socket_path
    """

    clear() # clears screen

    # print album cover
    print_album_cover(song)

    # print song data
    print_playing_song_metadata(song)

    # socket for communucation with mpv player 
    # (mpv is playing on background, used to customize mpv keyboard actions)
    socket_path = f"/tmp/mpvsocket_{os.getpid()}"

    # uses mpv to play the song on the background
    process = subprocess.Popen(["mpv", 
                    "--no-video", # audio only
                    "--really-quiet", # no display on terminal
                    "--ytdl-raw-options=cookies=cookies.txt", # use cookies.txt file for cookies
                    "--no-input-default-bindings", # disable keyboard actions
                    f"--input-ipc-server={socket_path}", # input commands from socket
                    song[4]])

    return process, socket_path


def music_player(song, shuffle_state=False, song_index=0):
    """
    Song playing logic
    Handles playlist operations (next/prev song, playing by order)

    :param song -> (title, artist, album, duration_string, url, album_cover_url)
    :param song index -> song's index inside the playlist that is being played (defaul=0 -> outside playlist)

    returns index of the next song to play
    """

    # plays the song in the background
    process, socket_path = play_song(song)

    end = False # flag for song ending
    paused = False # flag for pause
    shuffle = shuffle_state # flag for shuffle state changing
    liked = check_liked_song(song) # flag if song was liked

    def song_end():
        """
        Loops checking if song ended
        Changes the end flag
        """
        while True:
            if process.poll() != None: # checks if song ended
                nonlocal end
                end = True # Changes the end flag
                return
    
    # checks if song is being played for the minimum time to be counted as listen
    def detect_song_playing():
        time.sleep(30)
        if process.poll() is None:
            update_statistics(song)
            
    # thread that checks if song ended
    threading.Thread(target=song_end, daemon=True).start()
            
    # thread that checks if song was played for longer than 30 seconds
    threading.Thread(target=detect_song_playing, daemon=True).start()

    while True:
     
        # queue receiving song's menu selection 
        q = multiprocessing.Queue()

        # process handling song's menu (play/pause, forward, back, next, ...) -> sends selection to queue q
        p = multiprocessing.Process(target=menu_process, args=([f"[o] {shuffle_switch(shuffle)}", f"[l] {like_switch(liked)}", f"[p] {pause_switch(paused)}", "[a] ◀◀ 10s", "[d] ▶▶ 10s", "[w] ◀◀◀ prev", "[s] ▶▶▶ next", "[q] quit"], q))
        
        # start song menu process 
        p.start()

        # timeout for selecting from the menu (0.05 for smoothness)
        p.join(timeout=0.05)

        # if nothing was selected from the menu, kill menu's process
        if p.is_alive():
            p.terminate()
            p.join()
            menu_index = None

        # get menu's selected index from queue q
        else:
            try:
                menu_index = q.get_nowait()
            except:
                menu_index = None

        if end: #song ended
            break

        # handle menu selection
        # send commands to mpv via mpv socket
        if menu_index == 0: # shuffle/order playing
            shuffle = not shuffle
        elif menu_index == 1: # like/unlike song
            if not liked:
                add_song_to_playlist(song, "LIKED_SONGS")
            else:
                unlike_song(song)
            liked = not liked
        elif menu_index == 2: # play/pause
            paused = not paused
            pause_mpv(socket_path)
        elif menu_index == 3: # back 10s
            back_mpv(socket_path)
        elif menu_index == 4: # forward 10s
            forward_mpv(socket_path)
        elif menu_index == 5: # previous song
            stop_mpv(socket_path)
            clear()
            return song_index-1, shuffle # return previous song's playlist index
        elif menu_index == 6: # next song
            stop_mpv(socket_path)
            clear()
            return song_index+1, shuffle # return next song's playlist index
        elif menu_index == 7: # quit
            stop_mpv(socket_path)
            clear()
            return song_index, shuffle # same index is returned -> used to exit the playlist
        
    return song_index+1, shuffle # sond ended naturaly (get next song's index), shuffle flag

def check_liked_song(song_info):
    with open("playlists/LIKED_SONGS.json", "r") as f:
        liked_songs = json.load(f)

    for song in liked_songs['songs']:
        if list(song_info) == song:
            return True
    return False

def unlike_song(song_info):
    with open("playlists/LIKED_SONGS.json", "r") as f:
        liked_songs = json.load(f)

    if song_info in liked_songs['songs']:
        liked_songs['songs'].remove(song_info)
    store_playlist(liked_songs)