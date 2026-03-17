import os
import subprocess
import json
from ytmusic import search_music
from mpv_socket import *
from graphics import *
import multiprocessing
import threading
import random
from ai_playlist_generator.playlist_generator import playlist_generator
from copy import deepcopy


# number of results apearing whe n«searching for songs
MAX_SEARCH_RESULTS = 10

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
    
    # thread that checks if song ended
    threading.Thread(target=song_end, daemon=True).start()


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


#############################
# Playlist managing methods #
#############################

# playlists are seen by the program as dict objects and stored in JSON files


def new_playlist(ai_header=None):   
    """
    User creates a new playlist by inputing name and description
    Playlist is stored in memory

    returns the playlist created or None if action was cancelled
    """
    # create a json file by inputing name and description (empty playlist)
    while True:
        if ai_header: print(ai_header)
        new_playlist = {'name': None, 'description': None, 'songs': []}
        new_playlist['name'] = user_input("Enter playlist name : ([q] to go back) : ")
        if new_playlist['name'] == None: 
            clear()
            return None

        while True:
            new_playlist['description'] = user_input("Enter playlist description : ([q] to go back) : ")
            if new_playlist['description'] == None: 
                clear()
                break

            store_playlist(new_playlist)
            return new_playlist
        

def get_stored_playlists():
    """
    returns the names of the stored playlists
    """
    playlists = [f[:-5] for f in os.listdir('playlists') if f != "LIKED_SONGS.json"]
    playlists = ["📌 LIKED_SONGS 🤍"] + playlists
    return playlists


def get_playlist(playlist_name):
    """
    Loads the JSON file of a playlist that is stored
    """
    with open(f"playlists/{playlist_name}.json", "r") as f:
        return json.load(f)
    

def store_playlist(playlist):
    """
    Dumps a playlist into a JSON file and stores it
    """
    with open(f"playlists/{playlist['name']}.json", "w") as f:
        playlist = json.dumps(playlist)
        f.write(playlist)


def get_songs_from_playlist(playlist_name):
    """
    returns the list of songs from a playlist
    """
    playlist = get_playlist(playlist_name)
    return playlist['songs']
        

def add_song_to_playlist(song, playlist_name):
    playlist = get_playlist(playlist_name)
    playlist['songs'].append(song)
    store_playlist(playlist)


def select_playlist():
    """
    Displays all the playlists in a menu
    Lets user select one

    returns the name of the selected playlist 
    or None if operation was canceled
    """
    menu_options = ['< Back'] + get_stored_playlists()
    index = menu(menu_options)
    
    if index == 0:
        return None
    elif index == 1: # select liked songs playlist (because of the pinned emojis the name in the menu is different)
        return "LIKED_SONGS"
    return menu_options[index]


def shuffle_playlist_on_song(song, playlist):
    """
    returns a shuffled playlist starting with a given song
    (Used to shuffle songs when user selects shuffled playing)

    :param song -> starting song
    :param playlist -> playlist to shuffle
    """
    shuffled_playlist = deepcopy(playlist)
    shuffled_playlist.remove(song)
    random.shuffle(shuffled_playlist) 
    shuffled_playlist = [song] + shuffled_playlist
    return shuffled_playlist


def playlist_player(playlist_name):
    """
    Playlist playing logic

    Plays songs from playlist handling Shuffling
    """

    print_playlist_data(get_playlist(playlist_name))

    # get songs from selected playlist
    songs = get_songs_from_playlist(playlist_name)

    # shuffle deactivated
    shuffle = False
    shuffled_songs = None # shuffled playlist

    while True:
        
        # shuffle on/off display
        shuffle_string = shuffle_switch(shuffle)

        # display songs from selected playlist in a menu      
        menu_options = ["[q] < Back", "[p] Play ▶", f"[s] {shuffle_string}"] + [song_to_str(song) for song in songs]
        song_index = menu(menu_options)

        # go back button
        if song_index == 0:
            clear()
            break
        
        # play playlist button
        elif song_index == 1:
            if not shuffle: # play by ordered
                song_index = 0
            else: # play shuffled
                song_index = random.randint(0, len(songs)-1) # get random start song
                shuffled_songs = shuffle_playlist_on_song(songs[song_index], songs) # build shuffled playlist

        # shuffle on/off button
        elif song_index == 2:
            shuffle = not shuffle
            continue

        # specific song was selected
        else:
            song_index -= 3 # compensate menu options offset

            if shuffle:
                # builds shuffled playlist starting on selected song
                shuffled_songs = shuffle_playlist_on_song(songs[song_index], songs) 
                song_index = 0 # plays the selected song first


        while True:

            current_song = None

            # get song to play (ordered or shuffled playlist)
            if shuffle: current_song = shuffled_songs[song_index]
            else: current_song = songs[song_index]

            # play song
            next_index, shuffle_song = music_player(current_song, shuffle, song_index)

            shuffle = shuffle_song # update shuffle state after the song finishes

            if shuffle and shuffled_songs is None: # shuffle was activated during the song
                # create shuffled playlist starting with played song -> play next song
                shuffled_songs = shuffle_playlist_on_song(current_song, songs)
                next_index = 1

            elif not shuffle: # shuffle was deactivated during the song
                shuffled_songs = None # delete previous shuffled playlist
                next_index = songs.index(current_song) + (next_index - song_index) # previous or next song

            # handle song index outside of playlist dimensions (prev on first, next on last)
            if next_index == len(songs):
                song_index = 0
            elif next_index < 0:
                song_index = len(songs)-1
            elif next_index == song_index:
                # user pressed quit -> leaves playlist
                break
            else: song_index = next_index # set index for next song to be played


#########################
# AI Playlist generator #
#########################

def build_playlist(songs):
    """ 
    LLM will return a list of songs, each song being a list [artist, title]
    This function gets the metadata of those songs using YT Music API

    returns a list with the metadata of all songs
    """
    playlist = []
    for song in songs:
        query = f"{song[0]} - {song[1]}"
        metadata = search_music(query, 1)
        playlist.append(metadata[0])
    return playlist


def ai_playlist():
    """
    Uses an LLM to create playlists
    """
    clear()

    generated_playlist = new_playlist(ai_header)
    if generated_playlist == None:
        return

    songs = None

    # keep trying untill it succeeds
    while True:
        prompt = user_input("[AI] Please describe your playlist. I'll try my best... ([q] to go back) : ")
        
        llm_return = playlist_generator(prompt)

        if llm_return != [] and llm_return is not None:
            songs = llm_return
            break
    
    playlist_songs = build_playlist(songs)

    # add song to selectef playlist and store results
    for song in playlist_songs: 
        add_song_to_playlist(song, generated_playlist['name']) 
    store_playlist(generated_playlist)

    print(f"""Playlist {generated_playlist['name']} was added to 'Your Playlists' !!!""")

    index = menu(["< Back"])

    if index == 0: # go back
        clear()


########################
# Core functionalities #
########################

## Song searching

def search():
    """
    Search for songs functionality
    """

    # search box
    query = user_input("search ([q] to go back) : ")

    if query == None:
        return
    
    # searches and gets metadata from obtained results
    metadata = search_music(query, MAX_SEARCH_RESULTS)

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
        if index == len(results_options)-1:
            break

        # play selected song
        selected_song = metadata[index]

        while True:

            next_index, _ = music_player(selected_song)
            # replay same song if user selected next/prev or song ended
            if next_index != 0:
                continue
            else:
                break

        # user pressed quit
        # when leaving the song ask if add to playlist
        index = menu(["Add to playlist", "< Back"])

        if index == 0: # add to playlist
            playlist = select_playlist()
            if playlist is not None:
                add_song_to_playlist(selected_song, playlist)
        elif index == 1: # go back
            clear()


## Playlists

def playlist():
    """
    Playlists feature
    """
    while True:
        # simple menu
        index = menu(["Your Playlists", "New Playlist", "AI playlists", "< Back"])

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
            
            if playlist_index == 1:
                playlist_player("LIKED_SONGS")
            else:
                playlist_player(playlists[playlist_index-1])

        
        # New Playlist
        if index == 1:
            new_playlist()
            clear()

        if index == 2:
            ai_playlist()

        # go back
        if index == 3:
            break


# like songs

def check_liked_song(song_info):
    with open("playlists/LIKED_SONGS.json", "r") as f:
        liked_songs = json.load(f)

    for song in liked_songs['songs']:
        if song_info == song:
            return True
    return False

def unlike_song(song_info):
    with open("playlists/LIKED_SONGS.json", "r") as f:
        liked_songs = json.load(f)

    liked_songs['songs'].remove(song_info)
    store_playlist(liked_songs)


########################
########################


def main():

    os.makedirs("playlists", exist_ok=True)
    if not os.path.isfile("playlists/LIKED_SONGS.json"):
        liked = open("playlists/LIKED_SONGS.json", "w+")
        liked.write("{\"name\": \"LIKED_SONGS\", \"description\": \"\", \"songs\": []}")
    
    while True:
        clear()
        menu_selection = menu(["Liked Songs 🤍", "Search", "Playlists", "Exit"])
        if menu_selection == 0:
            playlist_player("LIKED_SONGS")
        elif menu_selection == 1:
            search()
        elif menu_selection == 2:
            playlist()
        elif menu_selection == 3:
            os.system('clear')
            os.system('stty sane')
            return
        

if __name__ == "__main__":
    main()
