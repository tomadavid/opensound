from ytmusicapi import YTMusic

ytmusic = YTMusic()

def search_music(query, num_results):
    """
    Fetches metadata from songs using Youtube Music API 

    :param query -> search query
    : num_results -> number of songs returned
    """

    # search
    results = ytmusic.search(query, filter="songs")
    
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