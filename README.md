# Opensound — Adless Linux Music Player

I needed to play my playlists without adds for my late night coding sessions and I have so many principles that I refuse to spend money on adds.
Had no choice than building a solution myself...

---

## Tools used:
- **Youtube Music API** (search songs)
- **mpv** (play songs)
- **Huggingface Inference Providers *meta-llama/Llama-3.1-70B-Instruct*** (for playlist generation) 

---

## Features
- Search for songs and listen to them with a link to the Youtube Music API
- Create playlists manually and add searched songs to them
- Create playlists with AI (you provide a description of the playlist)
- Listen to your playlists with **no adds**
- Shuffle playing order

---

## Project Structure

```
opensound/
│
├── ai_playlist_generator/
│         ├── output_parser.py          # LLM output parsing
│         └── playlist_generator.py     # LLM logic for generating playlists
│  
├── playlists/                          # created playlists are stored here 
│ 
├── graphics.py                         # Display variables and functions
├── mpv_socket.py                       # mpv commands for interaction with mpv player via a socket
├── opensound.py                        # main program
└── ytmusic.py                          # song searching using Youtube Music API

```

---

## Demo
**Music Player**
---
<img width="678" height="805" alt="Screenshot from 2025-11-04 16-40-58" src="https://github.com/user-attachments/assets/9721b821-d7ec-40fc-954c-fa951866f895" />

**AI Playlist Generator**
---
<img width="840" height="564" alt="Screenshot from 2025-11-04 16-50-59" src="https://github.com/user-attachments/assets/eaf463da-9ec6-4b39-8d5a-d215d99ae5b2" />

**Playlists**
---
<img width="840" height="564" alt="image" src="https://github.com/user-attachments/assets/5b2cd61f-12be-4d7b-9dc4-a39325036c55" />

  
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
pip install -r requirements.txt
```

### 4. Add required file

#### `cookies.txt`
- Go to Youtube and get a cookies file `coockies.txt` using a browser extention. Add the file to the repository. It is used to pass the autenticity test from yt-dlp.


## Running the Program
```bash
python opensound.py
```

---

## Author
Developed by **David Toma**  
