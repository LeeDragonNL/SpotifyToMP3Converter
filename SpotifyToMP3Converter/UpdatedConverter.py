import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import yt_dlp
from mutagen.easyid3 import EasyID3
import re
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from .env or defaults
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "9f1c4ef0cd2a4ed0bf84be06a310cba3")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "c3f88a07b9024d069d26dcc851fae763")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyDh4u8E7k8hkQAUit1OY2f5_nXdEIWS9T0")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "C:/ffmpeg/bin")

# Initialize APIs
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Helper Functions
def sanitize_filename(filename):
    """Remove invalid characters from filenames."""
    return re.sub(r'[\/:*?"<>|]', '', filename)

def search_youtube(title, artist, album):
    """Search YouTube for the best matching video."""
    query = f"{title} {artist} {album}"
    update_status(f"🔍 Searching YouTube: {query}")

    try:
        request = youtube.search().list(q=query, part="snippet", maxResults=3, type="video")
        response = request.execute()
        
        if not response["items"]:
            update_status(f"⚠️ No YouTube video found for {title} by {artist}.")
            return None
        
        video_id = response["items"][0]["id"]["videoId"]
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        update_status(f"✅ Found: {youtube_url}")
        return youtube_url
    except Exception as e:
        update_status(f"❌ YouTube search failed: {str(e)}")
        return None

def download_audio(youtube_url, title, artist, output_folder):
    """Download YouTube audio and convert to MP3."""
    try:
        safe_title = sanitize_filename(title)
        safe_artist = sanitize_filename(artist)
        output_path = os.path.join(output_folder, f"{safe_title} - {safe_artist}.mp3")
        
        if os.path.exists(output_path):
            update_status(f"ℹ️ File already exists: {output_path}, skipping download.")
            return output_path

        update_status(f"🎵 Downloading: {title} - {artist}")
        ydl_opts = {
            'format': 'bestaudio/best',
            'ffmpeg_location': FFMPEG_PATH,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'outtmpl': output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        update_status(f"✅ Downloaded: {output_path}")
        return output_path
    except Exception as e:
        update_status(f"❌ Download failed: {str(e)}")
        return None

def set_mp3_metadata(file_path, title, artist, album):
    """Embed metadata (ID3 tags) into the MP3 file."""
    try:
        if os.path.exists(file_path):
            audio = EasyID3(file_path)
            audio['title'] = title
            audio['artist'] = artist
            audio['album'] = album
            audio.save()
            update_status(f"✅ Metadata added: {file_path}")
    except Exception as e:
        update_status(f"❌ Metadata update failed: {str(e)}")

def get_spotify_track_info(spotify_url):
    """Fetch metadata for a single Spotify track."""
    try:
        track_id = spotify_url.split("/")[-1].split("?")[0]
        track_data = sp.track(track_id)
        if not track_data:
            raise ValueError("No track data returned from Spotify.")
        return [(track_data['name'], track_data['artists'][0]['name'], track_data['album']['name'])]
    except Exception as e:
        update_status(f"❌ Spotify track fetch failed: {str(e)}")
        return []

def get_spotify_playlist_tracks(playlist_url):
    """Fetch all track metadata from a Spotify playlist."""
    try:
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        results = sp.playlist_tracks(playlist_id)
        return [(item['track']['name'], item['track']['artists'][0]['name'], item['track']['album']['name']) 
                for item in results['items']]
    except Exception as e:
        update_status(f"❌ Spotify playlist fetch failed: {str(e)}")
        return []

# Core Logic
def process_spotify_url(spotify_url):
    """Determine if the URL is a track or playlist and fetch metadata."""
    if "track" in spotify_url:
        update_status("🎵 Detected a **single song**.")
        return get_spotify_track_info(spotify_url), "Single Songs"
    elif "playlist" in spotify_url:
        update_status("📀 Detected a **playlist**.")
        playlist_id = spotify_url.split("/")[-1].split("?")[0]
        return get_spotify_playlist_tracks(spotify_url), sanitize_filename(sp.playlist(playlist_id)['name'])
    else:
        update_status("❌ Invalid Spotify URL.")
        return [], None

def download_track(args):
    """Download a single track (used in ThreadPoolExecutor)."""
    title, artist, album, output_folder = args
    youtube_url = search_youtube(title, artist, album)
    if youtube_url:
        output_path = download_audio(youtube_url, title, artist, output_folder)
        if output_path:
            set_mp3_metadata(output_path, title, artist, album)

def download_tracks(tracks, playlist_name, output_folder):
    """Download all tracks concurrently."""
    if not tracks:
        update_status("❌ No tracks found.")
        return
    
    os.makedirs(output_folder, exist_ok=True)
    update_status(f"🎶 Downloading {len(tracks)} songs from '{playlist_name}'...")
    
    with ThreadPoolExecutor(max_workers=3) as executor:  # Limit to 3 concurrent downloads
        executor.map(download_track, [(t, a, al, output_folder) for t, a, al in tracks])
    
    update_status(f"🎉 ✅ Download complete! Files saved in: {output_folder}")

def spotify_to_mp3(spotify_url):
    """Main function to process Spotify URL and initiate downloads."""
    tracks, playlist_name = process_spotify_url(spotify_url)
    if not tracks or not playlist_name:
        return
    
    output_folder = filedialog.askdirectory(title="Select Download Folder")
    if not output_folder:
        update_status("❌ No folder selected.")
        return
    
    download_tracks(tracks, playlist_name, output_folder)

# GUI Functions
def update_status(message):
    """Thread-safe status update for the GUI."""
    root.after(0, lambda: status_text.insert(tk.END, message + "\n"))
    root.after(0, lambda: status_text.yview(tk.END))

def start_download():
    """Start the download process with progress bar."""
    spotify_url = url_entry.get().strip()
    if not spotify_url:
        messagebox.showerror("Error", "Please enter a Spotify URL.")
        return
    
    progress = ttk.Progressbar(main_frame, maximum=100, length=300)
    progress.pack(pady=5)
    
    def download_thread():
        tracks, playlist_name = process_spotify_url(spotify_url)
        if tracks:
            total_tracks = len(tracks)
            download_tracks(tracks, playlist_name, output_folder=filedialog.askdirectory(title="Select Download Folder"))
            for i in range(total_tracks):
                progress['value'] = ((i + 1) / total_tracks) * 100
                root.update_idletasks()
        progress.destroy()
    
    threading.Thread(target=download_thread, daemon=True).start()

# GUI Setup
root = ThemedTk(theme="arc")  # Using a modern theme
root.title("Spotify to MP3 Converter")
root.geometry("600x500")

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text="Enter Spotify Song/Playlist URL:").pack(pady=5)
url_entry = ttk.Entry(main_frame, width=50)
url_entry.pack(pady=5)

ttk.Button(main_frame, text="Download", command=start_download).pack(pady=10)

status_text = tk.Text(main_frame, height=20, width=70)
status_text.pack(pady=10)

ttk.Button(main_frame, text="Clear Status", command=lambda: status_text.delete(1.0, tk.END)).pack(pady=5)

# Show disclaimer on startup
messagebox.showinfo("Disclaimer", "This tool is for personal use only. Ensure you have rights to download content.")

root.mainloop()