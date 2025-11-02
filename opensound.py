import os
import subprocess
from simple_term_menu import TerminalMenu
import json
from ytmusic import search_music
import sys
from mpv_socket import pause_mpv, forward_mpv, back_mpv, stop_mpv
import multiprocessing
import threading

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

# number of results apearing whe n«searching for songs
MAX_SEARCH_RESULTS = 5

# cleans screen -> prints only header
def clear():
    os.system('clear')
    print(header)



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


# plays a song 
def play_song(song):
    """
    plays a song inside a subprocess using mpv command

    :param song -> (title, artist, album, duration_string, url, album_cover_url)
    
    returns process playing the song, mpv socket_path
    """

    clear() # clears screen

    album_cover = song[-1] # get album cover

    # print album cover with Ascii art using jp2a
    subprocess.run(["jp2a", album_cover, "--width=40", "--colors"])

    # print song data
    print(f"Title: {song[0]}")
    print(f"Artist: {song[1]}")
    print(f"Album: {song[2]}")
    print(" ....................................")

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


def play_song_by_order(song, song_index=0):
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
    
    # thread that checks if song ended
    threading.Thread(target=song_end, daemon=True).start()


    while True:
        
        # queue receiving song's menu selection 
        q = multiprocessing.Queue()

        # process handling song's menu (play/pause, forward, back, next, ...) -> sends selection to queue q
        if not paused:
            # playing
            p = multiprocessing.Process(target=menu_process, args=(["[p] pause", "[a] ◀◀ 10s", "[d] ▶▶ 10s", "[w] ◀◀◀ prev", "[s] ▶▶▶ next", "[q] quit"], q))
        else:
            # paused
            p = multiprocessing.Process(target=menu_process, args=(["[p] play", "[a] ◀◀ 10s", "[d] ▶▶ 10s", "[w] ◀◀◀ prev", "[s] ▶▶▶ next", "[q] quit"], q))
        
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
        if menu_index == 0: # play/pause
            paused = not paused
            pause_mpv(socket_path)
        elif menu_index == 1: # back 10s
            back_mpv(socket_path)
        elif menu_index == 2: # forward 10s
            forward_mpv(socket_path)
        elif menu_index == 3: # previous song
            stop_mpv(socket_path)
            clear()
            return song_index-1 # return previous song's playlist index
        elif menu_index == 4: # next song
            stop_mpv(socket_path)
            clear()
            return song_index+1 # return next song's playlist index
        elif menu_index == 5: # quit
            stop_mpv(socket_path)
            clear()
            return song_index # same index is returned -> used to exit the playlist
        
    return song_index+1 # sond ended naturaly (get next song's index)


def song_to_str(song):
    """
    returns a string that shows the song to the user
        "title - artist (album) duration"
    """
    return f"{song[0]} - {song[1]} ({song[2]}) {song[3]}"


def search():
    """
    Search songs feature
    """

    # search box
    search = input(r"search ([q] to go back) : ")

    # quit searc (go back)
    if search in ['q', 'Q']:
        return
    
    # searches and gets metadata from obtained results
    metadata = search_music(search, MAX_SEARCH_RESULTS)

    # creates visual representations of obtained songs on a list
    results_options = []
    for song in metadata:
        results_options.append(song_to_str(song))

    # last item of the menu (go back)
    results_options.append("< Back")

    while True:
        # displays search results on a menu
        index = menu(results_options)

        # go back
        if index == MAX_SEARCH_RESULTS:
            sys.stdout.write("\033[F\r\033[K")
            break

        # play selected song
        selected_song = metadata[index]

        while True:
            # replay same song if user selectd next/prev or song ended
            if play_song_by_order(selected_song) != 0:
                continue
            else:
                break

        # user pressed quit
        # when leaving the song ask if add to playlist
        index = menu(["Add to playlist", "< Back"])

        if index == 0: # add to playlist
            add_song_to_playlist(selected_song)
        elif index == 1: # go back
            clear()


def get_stored_playlists():
    """
    returns the names of the stored playlists
    """
    playlists = [f[:-5] for f in os.listdir('playlists')]
    return playlists


def add_song_to_playlist(song):
    """
    Adds a song to a playlist
    """

    # get all playlists inside a menu
    playlists = get_stored_playlists()
    index = menu(playlists)

    # add song to selectef playlist and store results
    with open(f"playlists/{playlists[index]}.json", "r") as f:
        playlist = json.load(f)
        playlist['songs'].append(song)
        json_file = json.dumps(playlist)
    with open(f"playlists/{playlists[index]}.json", "w") as f:
        f.write(json_file)


def playlist():
    """
    Playlists feature
    """
    while True:
        # simple menu
        index = menu(["Your Playlists", "New Playlist", "< Back"])

        # Your Playlists
        if index == 0:

            # get stored playlists
            playlists = get_stored_playlists()

            if playlists == []: # if no playlists
                print("You have no created playlists!")

            # menu with playlists
            menu_options = ["< Back"] + playlists
            playlist_index = menu(menu_options)

            # go back
            if playlist_index == 0:
                return

            # get songs from selected playlist
            f = open(f"playlists/{playlists[playlist_index-1]}.json", "r")
            playlist_dict = json.load(f)
            songs = playlist_dict['songs']

            while True:
                # display songs from selected playlist  in a menu      
                menu_options = ["< Back"] + [song_to_str(song) for song in songs]
                song_index = menu(menu_options)

                # go back
                if song_index == 0:
                    break

                song_index -= 1 # compensate song index (< back is on pos 0

                while True:
                    # play songs by order
                    next_index = play_song_by_order(songs[song_index], song_index)

                    # handle song index outside of playlist dimensions (prev on first, next on last)
                    if next_index == len(songs):
                        song_index = 0
                    elif next_index < 0:
                        song_index = len(songs)-1
                    elif next_index == song_index:
                        # user pressed quit -> leaves playlist
                        break
                    else: song_index = next_index # set index for next song to be played
        
        # New Playlist
        if index == 1:
            # create a json file by inputing name and description (empty playlist)
            new_playlist = {'name': None, 'description': None, 'songs': []}
            name = input("Enter playlist name : ")
            new_playlist['name'] = name
            clear()
            description = input("Enter playlist description : ")
            new_playlist['description'] = description
            clear()
            playlist_json = json.dumps(new_playlist)
            f = open(f"playlists/{name}.json", "w")
            f.write(playlist_json)

        # go back
        if index == 2:
            break


def main():
    while True:
        clear()
        menu_selection = menu(["Search", "Playlists", "Exit"])
        if menu_selection == 0:
            search()
        elif menu_selection == 1:
            playlist()
        elif menu_selection == 2:
            os.system('clear')
            os.system('stty sane')
            return
        


if __name__ == "__main__":
    main()


# TODO add shuffled order to playlists
# TODO create playlists with AI