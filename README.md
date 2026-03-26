<img width="825" height="461" alt="image" src="https://github.com/user-attachments/assets/b929b299-419d-4803-81ea-7b690b9d4146" />

# Opensound - Linux Terminal Music Player — No more adds

I needed to play my playlists without adds for my late night coding sessions and I have so many principles that I refuse to spend money on music without adds.
Had no choice than building a solution myself... btw spotify sucks

---

## Tools used:
- **ytmusicapi** (https://github.com/sigma67/ytmusicapi) (search songs)
- **mpv** (play songs)
- ***Huggingface Inference Providers *meta-llama/Llama-3.1-70B-Instruct*** (for playlist generation) - 🚧 WORK IN PROGRESS 🚧*

---

## Features
- 🔍 Search for songs and listen to them 
- 📋 Create playlists manually and add searched songs to them
- 🤖 Create playlists with AI (you provide a description of the playlist) - 🚧 WORK IN PROGRESS 🚧
- 🔊 Listen to your playlists with **no adds**
- 🔀 Shuffle playing order
- 📊 Statistics for most played songs and artists
- 💚 Like songs and listen to them on your liked songs list

---
## Demo
**Music Player**
---
<img width="826" height="995" alt="image" src="https://github.com/user-attachments/assets/b15b4a03-3a1a-48ec-a44f-23945d4b8403" />

**Playlists**
---
<img width="866" height="856" alt="image" src="https://github.com/user-attachments/assets/4d59b73a-4d17-44ee-a591-983a1beb1d76" />

---

## Project Structure

```
opensound/
│
├── graphics.py                         # Display variables and functions
├── mpv_socket.py                       # mpv commands for interaction with mpv player via a socket
├── music_player.py                     # music playing process handling with mpv
├── opensound.py                        # main program
├── playlists.py                        # playlist handling logic
├── search.py                           # functions for searching tracks, albums and artists
├── stats.py                            # functions for statistic making about played songs and artists
└── ytmusic.py                          # searching using ytmusicapi

```
---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/tomadavid/opensound.git
cd opensound
```

### 2. Create a virtual environment
```bash
python -m venv .env
source .env/bin/activate      # macOS/Linux
.env\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
sudo apt install mpv
sudo apt install jp2a # for album cover ascii art
pip install -r requirements.txt
```

### 4. Add required file

#### `cookies.txt`
- Go to Youtube and get a cookies file `cookies.txt` using a browser extention. Add the file to the repository. It is used to pass the autenticity test from yt-dlp.

### 5. Set the project path on `opensound_run.sh`

```bash
chmod +x opensound_run.sh
```

## Running the Program
```bash
./opensound_run.sh
```

---
## Acknowledgements

This project uses the ytmusicapi library by sigma67.

Repository: https://github.com/sigma67/ytmusicapi

ytmusicapi is licensed under the MIT License.

Copyright (c) 2024 sigma67

## Author
Developed by **David Toma**  
