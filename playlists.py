import os
import json
from ytmusic import *
from mpv_socket import *
from graphics import *
import random
from copy import deepcopy

#############################
# Playlist managing methods #
#############################

# playlists are seen by the program as dict objects and stored in JSON files

def playlist():
    """
    Playlists feature
    """
    while True:
        # simple menu
        index = menu(["[q] < Back", "Your Playlists", "New Playlist"])

        # Your Playlists
        if index == 1:

            # get stored playlists
            playlists = get_stored_playlists()

            if playlists == []: # if no playlists
                print("You have no created playlists!")

            # menu with playlists
            menu_options = ["[q] < Back"] + playlists
            playlist_index = menu(menu_options)

            # go back
            if playlist_index == 0:
                return
            
            if playlist_index == 1:
                playlist_player("LIKED_SONGS")
            else:
                playlist_player(playlists[playlist_index-1])

        
        # New Playlist
        if index == 2:
            new_playlist()
            clear()

        # go back
        if index == 0:
            break

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
    menu_options = ["[q] < Back"] + get_stored_playlists()
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


def playlist_player(playlist_name=None, songs=None, album=None):
    """
    Playlist playing logic

    Plays songs from playlist handling Shuffling
    """
    from music_player import music_player

    if playlist_name is not None:
        print_playlist_data(get_playlist(playlist_name))

        # get songs from selected playlist
        songs = get_songs_from_playlist(playlist_name)

    # shuffle deactivated
    shuffle = False
    shuffled_songs = None # shuffled playlist

    while True:
        if album:
            display_album(album)
        
        # shuffle on/off display
        shuffle_string = shuffle_switch(shuffle)

        # display songs from selected playlist in a menu
        if playlist_name is not None:      
            menu_options = ["[q] < Back", "[p] Play ▶", f"[s] {shuffle_string}"] + [song_to_str(song) for song in songs]
        
        # used on top tracks statistics
        else:
            song_str = []
            for i in range(len(songs)):
                song_str.append(f"{str(i+1)}" + " "*(2-len(str(i+1))) + f" {song_to_str(songs[i])}")
            
            menu_options = ["[q] < Back", "[p] Play ▶", f"[s] {shuffle_string}"] + song_str
        
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
