import os
from simple_term_menu import TerminalMenu
import multiprocessing
import subprocess


header = r"""

                                                                             888
                                                                             888
                                                                             888
 .d88b.  88888b.   .d88b.  88888b.  .d8888b   .d88b.  888  888 88888b.   .d88888
d88""88b 888 "88b d8P  Y8b 888 "88b 88K      d88""88b 888  888 888 "88b d88" 888
888  888 888  888 88888888 888  888 "Y8888b. 888  888 888  888 888  888 888  888
Y88..88P 888 d88P Y8b.     888  888      X88 Y88..88P Y88b 888 888  888 Y88b 888
 "Y88P"  88888P"   "Y8888  888  888  88888P'  "Y88P"   "Y88888 888  888  "Y88888
         888                                                                    
         888                                                                    
         888                                                                    
                                                                by David Toma
"""

ai_header = r"""


 ██████╗ ██╗  ██╗     ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗   ██╗████████╗███████╗██████╗ 
██╔═══██╗██║ ██╔╝    ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║   ██║╚══██╔══╝██╔════╝██╔══██╗
██║   ██║█████╔╝     ██║     ██║   ██║██╔████╔██║██████╔╝██║   ██║   ██║   █████╗  ██████╔╝
██║   ██║██╔═██╗     ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║   ██║   ██║   ██╔══╝  ██╔══██╗
╚██████╔╝██║  ██╗    ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ╚██████╔╝   ██║   ███████╗██║  ██║


"""


def clear():
    os.system('clear')
    os.system('stty sane')
    print(header)


""" User interaction """

def menu(options):
    """
    creates a TerminalMenu object with given options

    returns menu selected index
    """
    terminal_menu = TerminalMenu(options)
    index = terminal_menu.show()
    return index

def menu_process(options, q : multiprocessing.Process):
    """
    creates a TerminalMenu object with given options

    sends selected index to process q
    """
    index = menu(options)
    q.put(index)

def user_input(string):
    user_text = input(string)
    if user_text in ['q', 'Q']:
        return None
    return user_text


""" Present songs """

def print_playing_song_metadata(song):
    # print song data
    print(f"Title: {song[0]}")
    print(f"Artist: {song[1]}")
    print(f"Album: {song[2]}")
    print(" ....................................")

def print_album_cover(song):
    # print album cover with Ascii art using jp2a
    subprocess.run(["jp2a", song[-1], "--width=40", "--colors"])

def song_to_str(song):
    """
    returns a string that shows the song to the user
        "title - artist (album) duration"
    """
    return f"{song[0]} - {song[1]} ({song[2]}) {song[3]}"

def print_playlist_data(playlist):
    print(f"*** {playlist['name']} ***")
    print(f"{playlist['description']}")
    print(f"{len(playlist['songs'])} songs")

""" Play/Pause and Shuffle/Order buttons """

def shuffle_switch(shuffle):
    if shuffle: return "Shuffle 🔀"
    else: return "By order 🔁"

def pause_switch(paused):
    if paused: return 'Play ▶'
    else: return 'Pause ⏸' 

def like_switch(liked):
    if liked: return 'Liked 🤍'
    else: return 'Like ♡'

