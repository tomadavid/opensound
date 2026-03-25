from ytmusic import *
from mpv_socket import *
from graphics import *
from music_player import music_player
from playlists import select_playlist, add_song_to_playlist, playlist_player


# number of results apearing when searching
MAX_SEARCH_RESULTS = 10
MAX_ARTISTS_SEARCH = 5
MAX_ALBUMS_SEARCH = 5


#########################
#######   Search  #######
#########################

def search():

    while True:
        index = menu(["[q] < Back", 'Tracks', 'Albums', 'Artists'])

        if index == 1:
            search_song()
        elif index == 2:
            search_album()
        elif index == 3:
            # TODO
            search_artist()
        elif index == 0:
            clear()
            break


## Song searching

def search_song(artist = None):
    """
    Search for songs functionality
    """

    if artist == None:
        # search box
        query = user_input("search ([q] to go back) : ")

        if query == None:
            clear()
            return
        
    if artist is None:
        # searches and gets metadata from obtained results
        metadata = yt_search_music(query, MAX_SEARCH_RESULTS)
    else:
        metadata = yt_get_artist_popular_tracks(artist)

    # creates visual representations of obtained songs on a list
    results_options = []
    for song in metadata:
        results_options.append(song_to_str(song))

    # last item of the menu (go back)
    results_options.append("[q] < Back")

    while True:

        # displays search results on a menu
        index = menu(results_options)

        # go back
        if index == len(results_options)-1:
            clear()
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
        index = menu(["Add to playlist", "[q] < Back"])

        if index == 0: # add to playlist
            playlist = select_playlist()
            if playlist is not None:
                add_song_to_playlist(selected_song, playlist)
        elif index == 1: # go back
            clear()

            if artist is not None:
                display_artist(artist)
                print("*** Popular Tracks ***")

# artist searching

def search_artist():
    """
    Search for artists functionality
    """

    # search box
    query = user_input("search ([q] to go back) : ")

    if query == None:
        clear()
        return

    # searches and gets metadata from obtained results
    metadata = yt_search_artist(query, MAX_ARTISTS_SEARCH)

    # creates visual representations of obtained songs on a list
    results_options = []
    for artist in metadata:
        results_options.append(artist[0])

    # last item of the menu (go back)
    results_options.append("[q] < Back")

    while True:
        # displays search results on a menu
        clear()
        index = menu(results_options)

        # go back
        if index == len(results_options)-1:
            clear()
            break

        # play selected song
        selected_artist = metadata[index]

        artist_page(selected_artist)

# album search

def search_album():
    """
    Search for artists functionality
    """

    # search box
    query = user_input("search ([q] to go back) : ")

    if query == None:
        clear()
        return

    # searches and gets metadata from obtained results
    albums_searched = yt_search_album(query, MAX_ARTISTS_SEARCH)

    # creates visual representations of obtained songs on a list
    results_options = []
    for album in albums_searched:
        results_options.append(album_to_str_artist(album))

    # last item of the menu (go back)
    results_options.append("[q] < Back")

    while True:
        # displays search results on a menu
        clear()
        index = menu(results_options)

        # go back
        if index == len(results_options)-1:
            clear()
            break

        # play selected song
        selected_album = albums_searched[index]

        album_page(selected_album)


def album_page(album):
    clear()
    tracks = yt_get_album_tracks(album[-2])
    playlist_player(None, tracks, album)


def artist_albums(artist):

    albums = yt_get_artist_albums(artist)

    menu_options = ["[q] < Back"] + [album_to_str(album) for album in albums]

    while True:

        clear()
        display_artist(artist)

        index = menu(menu_options)

        if index == 0:
            clear()
            break
        else:
            selected_album = albums[index-1]
            album_page(selected_album)


# artist tracks

def artist_tracks(artist):
    search_song(artist)


# artist page

def artist_page(artist):

    while True:
        clear()
        display_artist(artist)

        index = menu(["[q] < Back", 'Popular Tracks', 'Albums'])

        if index == 1:
            artist_tracks(artist)
        elif index == 2:
            artist_albums(artist)
        if index == 0:
            clear()
            break