import os
from ytmusic import *
from mpv_socket import *
from graphics import *
from playlists import playlist_player
from search import search
from playlists import playlist
from stats import statistics

def setup_directories():
    """
    Setup useful directories
    """
    os.makedirs("playlists", exist_ok=True)
    if not os.path.isfile("playlists/LIKED_SONGS.json"):
        liked = open("playlists/LIKED_SONGS.json", "w+")
        liked.write("{\"name\": \"LIKED_SONGS\", \"description\": \"\", \"songs\": []}")
    
    os.makedirs("stats", exist_ok=True)
    if not os.path.isfile("stats/songs.json"):
        liked = open("stats/songs.json", "w+")
        liked.write("[]")

def main():

    setup_directories()

    while True:
        clear()
        menu_selection = menu(["Liked Songs 🤍", "Search", "Playlists", "Statistics", "Exit"])
        if menu_selection == 0:
            playlist_player("LIKED_SONGS")
        elif menu_selection == 1:
            search()
        elif menu_selection == 2:
            playlist()
        elif menu_selection == 3:
            statistics()
        elif menu_selection == 4:
            os.system('clear')
            os.system('stty sane')
            return

if __name__ == "__main__":
    main()
    