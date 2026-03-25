from ytmusicapi import YTMusic

ytmusic = YTMusic()

def yt_search_music(query, num_results):
    """
    Fetches metadata from songs using Youtube Music API 

    :param query -> search query
    : num_results -> number of songs returned
    """

    # search
    results = ytmusic.search(query, filter="songs")[:num_results]
    
    # extract selected information from songs
    music_results = []
    for song in results:
        if "videoId" in song:
            music_results.append({
                "title": song["title"],
                "artist": song["artists"][0]["name"] if song.get("artists") else "Unknown",
                "album": song["album"]["name"] if song.get("album") else "Unknown",
                "videoId": song["videoId"],
                "cover": song["thumbnails"][-1]["url"] if song.get("thumbnails") else None,
                "duration": song["duration"]
            })

        # get metadata from selected number of songs
        metadata = [(result['title'],
                     result['artist'],
                     result['album'],
                     result['duration'], 
                     f"https://music.youtube.com/watch?v={result['videoId']}",
                     result['cover'])
                     for result in music_results[:num_results]]

    return metadata

def yt_get_ytmusic_link(track, artist, album):
    search = yt_search_music(f"{track} {artist} {album}", 1)
    return (search[0][-2], search[0][-3])

def yt_search_album(query, num_results):
    """
    Fetches metadata from songs using Youtube Music API 

    :param query -> search query
    : num_results -> number of songs returned
    """

    # search
    results = ytmusic.search(query, filter="albums")
    
    album_list = []

    for album in results:

        if 'year' in album.keys():
            year = album['year']
        else:
            year = album['type']

        album_list.append((album['title'], 
                           ", ".join([artist["name"] for artist in album.get("artists", [])]),
                           year, 
                           album['browseId'], 
                           album["thumbnails"][-1]["url"]))

    return album_list[:num_results]

def yt_search_artist(query, num_results):
    """
    Fetches metadata from songs using Youtube Music API 

    :param query -> search query
    : num_results -> number of artists returned
    """

    results = ytmusic.search(query, filter="artists")
    

    # extract selected information from songs
    artist_results = []
    for artist in results:
        if "browseId" in artist:
            artist_results.append({
                "artist": artist["artist"],
                "id": artist["browseId"],
                "photo": artist["thumbnails"][-1]["url"] if artist.get("thumbnails") else None
            })

        # get metadata from selected number of songs
        metadata = [(result['artist'],
                     result['id'],
                     result['photo'])
                     for result in artist_results[:num_results]]
        
    return metadata


def yt_get_artist_albums(artist):

    artist_data = ytmusic.get_artist(artist[1])

    albums_section = artist_data.get("albums", {})

    albums_browse_id = albums_section.get("browseId")
    params = albums_section.get("params")

    if albums_browse_id and params:
        all_albums = ytmusic.get_artist_albums(albums_browse_id, params)
    else:
        all_albums = albums_section.get("results", [])

    album_list = []

    for album in all_albums:

        if 'year' in album.keys():
            year = album['year']
        else:
            year = album['type']

        album_list.append((album['title'], 
                           artist_data['name'],
                           year, 
                           album['browseId'], 
                           album["thumbnails"][-1]["url"]))

    return album_list

def yt_artist_description(artist_id):
    songs = ytmusic.get_artist(artist_id)
    return songs["description"]

def yt_get_album_tracks(album_id):

    album_data = ytmusic.get_album(album_id)

    # Extract songs
    tracks = album_data.get("tracks", [])

    metadata = []
    
    for track in tracks:
        artist = ", ".join([artist["name"] for artist in track.get("artists", [])])
        duration = None

        if track["videoType"] == "MUSIC_VIDEO_TYPE_OMV":
            link, duration = yt_get_ytmusic_link(track["title"], artist, album_data["title"])
        else:
            link = f"https://music.youtube.com/watch?v={track['videoId']}"
            duration = track["duration"]

        metadata.append((track['title'],
                          artist,
                          track['album'],
                          duration, 
                          link,
                          album_data['thumbnails'][-1]['url']))
        
    return metadata
