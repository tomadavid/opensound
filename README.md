# Opensound — Adless Linux Music Player

I needed to play my playlists without adds for my late night coding sessions and I have so many principles that I refuse to spend money on adds.
Had no choice than building a solution myself...

---

## ✨ Features
- 🔍 Search for songs and listen to them with a link to the Youtube Music API
- 📋 Create playlists manually and add searched songs to them
- 🤖 Create playlists with AI (you provide a description of the playlist)
- 🚫 Listen to your playlists with **no adds**
- 🔀 Shuffle playing order

---

## 📂 Project Structure

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
<img width="678" height="805" alt="Screenshot from 2025-11-04 16-40-58" src="https://github.com/user-attachments/assets/9721b821-d7ec-40fc-954c-fa951866f895" />
**AI Playlist Generator**
<img width="840" height="564" alt="Screenshot from 2025-11-04 16-50-59" src="https://github.com/user-attachments/assets/eaf463da-9ec6-4b39-8d5a-d215d99ae5b2" />
**Playlists**
<img width="840" height="564" alt="Screenshot from 2025-11-04 16-52-43" src="https://github.com/user-attachments/assets/a7c8cd3d-66f4-4062-9283-2a5a62248815" />

  
---

## ⚙️ Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/tomadavid/booking-bot.git
cd booking-bot
```

### 2️⃣ Create a virtual environment
```bash
python -m venv .env
source .env/bin/activate      # macOS/Linux
.env\Scripts\activate         # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Add required file

#### 🧩 `cookies.txt`
- Go to Youtube and get a cookies file `coockies.txt` using a browser extention. Add the file to the repository. It is used to pass the autenticity test from yt-dlp.


## 🚀 Running the Program
```bash
python opensound.py
```

---

## 👤 Author
Developed by **David Toma**  
