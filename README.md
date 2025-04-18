# 🎵 Spotify to MP3 Converter (GUI)

A Python-based desktop app that converts Spotify playlists and tracks to high-quality MP3 files by searching and downloading the corresponding audio from YouTube.

---

## ✨ Features

- 🎧 Convert **Spotify tracks and playlists** to MP3
- 🔍 Automatically searches for matching **YouTube videos**
- 📥 Downloads and converts to **MP3** format using `yt-dlp` and `ffmpeg`
- 🏷️ Adds **ID3 metadata** (title, artist, album)
- 🖥️ User-friendly **Tkinter GUI** with a modern theme
- ⚡ Supports **concurrent downloads** (multi-threaded)
- 🧩 Loads credentials from a `.env` file for easy configuration

---

## 🛠 Requirements

- Python 3.7+
- A [Spotify Developer Account](https://developer.spotify.com/)
- A [YouTube Data API Key](https://console.developers.google.com/)
- [FFmpeg](https://ffmpeg.org/download.html) installed and accessible

---

## 🔧 Installation

1. **Clone the repo:**

```bash
git clone https://github.com/LeeDragonNL/spotify-to-mp3-gui.git
cd SpotifyToMP3Converter 
```

## ▶️ Usage

1. Run UpdatedConverter.py
2. Paste a Spotify track or playlist URL
3. Select a download folder
4. Sit back and enjoy your MP3s! 🎶

## 📂 Output Format

YourMusicFolder/
├── Song Title - Artist.mp3

## 🧪 Technologies Used
tkinter + ttkthemes — GUI framework

spotipy — Spotify Web API

googleapiclient — YouTube Data API

yt-dlp — YouTube downloader

mutagen — MP3 metadata editing

concurrent.futures — Multi-threading for downloads

## ⚠️ Disclaimer
This tool is intended for personal use only. Ensure you have the legal rights to download and use any content retrieved with this application. The developer is not responsible for misuse.

## ❤️ Credits
Built with love by Lirandy — Inspired by the desire to save good playlists offline, easily.
