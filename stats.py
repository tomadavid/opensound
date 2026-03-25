import json
from ytmusic import *
from mpv_socket import *
from graphics import *
import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter
from playlists import playlist_player

########################
# Statistics
########################

def statistics():
    while True:

        index = menu(["[q] < Back", 'Top Tracks', 'Top Artists'])

        if index == 1:
            top_tracks()
        elif index == 2:
            top_artists()
        elif index == 0:
            clear()
            break


############# Most Played Tracks #############

def top_tracks():
    while True:
        print()
        index = menu(["[q] < Back", 'Last Month', 'Last 6 Months', 'Last Year', 'All Time'])

        if index == 1:
            display_most_played_tracks(1)
        elif index == 2:
            display_most_played_tracks(6)
        elif index == 3:
            display_most_played_tracks(12)
        elif index == 4:
            display_most_played_tracks(None)
        elif index == 0:
            clear()
            break


def display_most_played_tracks(interval):
    """
    Displays a playlist with the 20 most played songs given an interval (in months)
    """

    tracks = get_most_played_songs(interval)

    songs = [track[0] for track in tracks]

    if interval == 1:
        print("** Most Played Tracks - Last Month **\n")
    if interval == 6:
        print("** Most Played Tracks - Last 6 Months **\n")
    if interval == 12:
        print("** Most Played Tracks - Last Year **\n")
    if interval == None:
        print("** Most Played Tracks - All Time **\n")

    display_most_played_song(interval, tracks[0])

    playlist_player(None, songs)


def get_most_played_songs(interval):
    """
    Gets a list of the 20 most played songs given an interval (in months)
    """
    
    with open("stats/songs.json", "r") as f:
        songs = json.load(f)
    
    counter = None

    if interval is None:
        # all time stats
        counter = Counter(normalize_song_key(song["song"]) for song in songs)
    else:
        # last 1, 6 or 12 months stats
        cutoff = datetime.datetime.now() - relativedelta(months=interval)

        counter = Counter(
            normalize_song_key(song["song"]) for song in songs
            if datetime.datetime.strptime(song['timestamp'], "%Y-%m-%d %H:%M:%S.%f") > cutoff
        )

    return [(song, count) for song, count in counter.most_common(20)]


############# Most Played Artists #############

def top_artists():

    while True:
        print()
        index = menu(["[q] < Back", 'Last Month', 'Last 6 Months', 'Last Year', 'All Time'])

        if index == 1:
            display_most_played_artists(1)
        elif index == 2:
            display_most_played_artists(6)
        elif index == 3:
            display_most_played_artists(12)
        elif index == 4:
            display_most_played_artists(None)
        elif index == 0:
            clear()
            break

def display_most_played_artists(interval):

    artists = get_most_played_artists(interval)

    names = []

    for i in range(len(artists)):

        names.append(f"{str(i+1)} " + " "*(i<9) + f"{artists[i][0]}")

    while True:
        if interval == 1:
            print("** Most Played Artists - Last Month **\n")
        elif interval == 6:
            print("** Most Played Artists - Last 6 Months **\n")
        elif interval == 12:
            print("** Most Played Artists - Last Year **\n")
        elif interval is None:
            print("** Most Played Artists - All Time **\n")

        display_top_artist(interval, artists[0])

        index = menu(["[q] < Back"] + names)

        if index == 0:
            clear()
            break
        else:
            selected_artist = artists[index-1]
            artist_page((selected_artist[0], selected_artist[1]))


def get_most_played_artists(interval):
    
    with open("stats/songs.json", "r") as f:
        songs = json.load(f)
    
    counter = None

    if interval is None:
        # all time stats
        counter = Counter(normalize_song_key(song["song"])[1] for song in songs)
    else:
        # last 1, 6 or 12 months stats
        cutoff = datetime.datetime.now() - relativedelta(months=interval)

        counter = Counter(
            normalize_song_key(song["song"])[1] for song in songs
            if datetime.datetime.strptime(song['timestamp'], "%Y-%m-%d %H:%M:%S.%f") > cutoff
        )

    return [(artist[0], artist[1], count) for artist, count in counter.most_common(20)]


########################################################################

def update_statistics(song):
    """
    Add song play to the stats file
    """

    with open("stats/songs.json", "r") as f:
        songs = json.load(f)

    playing_data = {"song": song, "timestamp": str(datetime.datetime.now())}

    songs.append(playing_data)

    songs = json.dumps(songs)
    with open("stats/songs.json", "w") as f:
        f.write(songs)


## auxiliary method for processing loaded json lists to tuples

def normalize_song_key(song_tuple):
    artist = song_tuple[1]
    if isinstance(artist, (list, set)):
        artist = tuple(artist)
    return (
        song_tuple[0],
        artist,
        song_tuple[2],
        song_tuple[3],
        song_tuple[4],
        song_tuple[5],
    )

