import tkinter as tk
from tkinter import ttk,messagebox, filedialog
from ttkthemes import ThemedTk
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import yt_dlp
from mutagen.easyid3 import EasyID3
import re
import os
import threading


# Spotify API Credentials
SPOTIFY_CLIENT_ID = "9f1c4ef0cd2a4ed0bf84be06a310cba3"
SPOTIFY_CLIENT_SECRET = "c3f88a07b9024d069d26dcc851fae763"

# YouTube API Key
YOUTUBE_API_KEY = "AIzaSyDh4u8E7k8hkQAUit1OY2f5_nXdEIWS9T0"

# Initialize APIs
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Helper Functions
def sanitize_filename(filename):
    """Remove invalid characters for filenames"""
    return re.sub(r'[\/:*?"<>|]', '', filename)

def search_youtube(title, artist, album):
    """Find the best YouTube match for a song"""
    query = f"{title} {artist} {album} official audio -cover -live -karaoke -remix"
    update_status(f"🔍 Searching YouTube: {query}")

    request = youtube.search().list(q=query, part="snippet", maxResults=1, type="video")
    response = request.execute()
    
    if not response["items"]:
        update_status(f"⚠️ No YouTube video found for {title} by {artist}.")
        return None

    video_id = response["items"][0]["id"]["videoId"]
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    update_status(f"✅ Found: {youtube_url}")
    return youtube_url

def download_audio(youtube_url, title, artist, output_folder):
    """Download YouTube audio and convert it to MP3"""
    safe_title = sanitize_filename(title)
    safe_artist = sanitize_filename(artist)
    output_path = os.path.join(output_folder, f"{safe_title} - {safe_artist}.mp3")

    update_status(f"🎵 Downloading: {title} - {artist}")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': "C:/ffmpeg/bin",
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': output_path,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        update_status(f"✅ Downloaded: {output_path}")
        return output_path
    except Exception as e:
        update_status(f"❌ Download failed: {str(e)}")
        return None

def set_mp3_metadata(file_path, title, artist, album):
    """Embed metadata (ID3 tags) into the MP3 file"""
    if os.path.exists(file_path):
        audio = EasyID3(file_path)
        audio['title'] = title
        audio['artist'] = artist
        audio['album'] = album
        audio.save()
        update_status(f"✅ Metadata added: {file_path}")

def get_spotify_track_info(spotify_url):
    """Fetch song metadata from Spotify"""
    track_id = spotify_url.split("/")[-1].split("?")[0]
    track_data = sp.track(track_id)
    title, artist, album = track_data['name'], track_data['artists'][0]['name'], track_data['album']['name']
    return [(title, artist, album)]

def get_spotify_playlist_tracks(playlist_url):
    """Fetch all track metadata from a Spotify playlist"""
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)
    return [(item['track']['name'], item['track']['artists'][0]['name'], item['track']['album']['name']) for item in results['items']]

def spotify_to_mp3(spotify_url):
    """Detect if it's a song or playlist and process accordingly"""
    global output_folder

    if "track" in spotify_url:
        update_status("🎵 Detected a **single song**.")
        tracks = get_spotify_track_info(spotify_url)
        playlist_name = "Single Songs"
    elif "playlist" in spotify_url:
        update_status("📀 Detected a **playlist**.")
        tracks = get_spotify_playlist_tracks(spotify_url)
        playlist_name = sanitize_filename(sp.playlist(spotify_url.split("/")[-1].split("?")[0])['name'])
    else:
        update_status("❌ Invalid Spotify URL.")
        return

    if not tracks:
        update_status("❌ No tracks found.")
        return

    output_folder = filedialog.askdirectory(title="Select Download Folder")
    if not output_folder:
        update_status("❌ No folder selected.")
        return
    
    os.makedirs(output_folder, exist_ok=True)

    update_status(f"🎶 Downloading {len(tracks)} songs from '{playlist_name}'...")

    for index, (title, artist, album) in enumerate(tracks, start=1):
        update_status(f"🔽 {index}/{len(tracks)}: {title} - {artist}")

        youtube_url = search_youtube(title, artist, album)
        if youtube_url is None:
            update_status(f"⚠️ Skipping {title} - {artist}")
            continue

        output_path = download_audio(youtube_url, title, artist, output_folder)
        if output_path:
            set_mp3_metadata(output_path, title, artist, album)
            update_status(f"✅ {title} - {artist} downloaded!")
        else:
            update_status(f"❌ Failed to download {title} - {artist}.")

    update_status(f"🎉 ✅ Download complete! Files saved in: {output_folder}")

# GUI Functions
def start_download():
    spotify_url = url_entry.get()
    if spotify_url.strip():
        threading.Thread(target=spotify_to_mp3, args=(spotify_url,), daemon=True).start()
    else:
        messagebox.showerror("Error", "Please enter a Spotify URL.")

def update_status(message):
    status_text.insert(tk.END, message + "\n")
    status_text.yview(tk.END)

# GUI Setup

root = tk.Tk()
root.title("Spotify to MP3 Converter")
root.geometry("500x400")

style = tk.Style(root)

tk.Label(root, text="Enter Spotify Song/Playlist URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

tk.Button(root, text="Download", command=start_download).pack(pady=10)

status_text = tk.Text(root, height=15, width=60)
status_text.pack(pady=10)

root.mainloop()
