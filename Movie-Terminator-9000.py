import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tqdm import tqdm
from pymediainfo import MediaInfo
import threading
import time

# 🚀 Video file extensions (Bina inke zindagi adhoori hai 😭)
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm", ".mpeg", ".mpg"}

# 🎬 Minimum file size to consider as a movie (700MB se kam? Chhoti clip hogi 😆)
MOVIE_SIZE_THRESHOLD_MB = 700

# 👑 Create the main application window
root = tk.Tk()
root.title("🎥 Movie Sorter - King Pranav Edition 👑")
root.geometry("500x300")
root.resizable(False, False)

progress_label = tk.Label(root, text="🔍 Ready to Scan...", font=("Arial", 12))
progress_label.pack(pady=10)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="📂 Select a folder to begin!", font=("Arial", 10))
status_label.pack(pady=5)

spinner_label = tk.Label(root, text="", font=("Arial", 14))
spinner_label.pack()

start_button = tk.Button(root, text="🚀 Start Sorting", font=("Arial", 12), command=lambda: threading.Thread(target=main).start())
start_button.pack(pady=10)

spinner_running = False
def animate_spinner():
    spinner_frames = ['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽']
    i = 0
    while spinner_running:
        spinner_label.config(text=spinner_frames[i % len(spinner_frames)])
        i += 1
        time.sleep(0.1)
        root.update_idletasks()
    spinner_label.config(text="")

def find_video_files(start_dir):
    # 📂 Dhoondh rahe hain aapke videos...
    video_files = []
    for root, _, files in os.walk(start_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                video_files.append(os.path.join(root, file))
    return video_files

def is_movie(file_path):
    # 🎬 Yeh movie hai ya chhoti clip? Dekhte hain...
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb < MOVIE_SIZE_THRESHOLD_MB:
            return False

        media_info = MediaInfo.parse(file_path)
        for track in media_info.tracks:
            if track.track_type == "Video" and track.duration:
                try:
                    duration_ms = int(float(track.duration))
                    duration_minutes = (duration_ms / 1000) / 60
                    if duration_minutes > 60:
                        return True
                except ValueError:
                    pass
    except Exception as e:
        print(f"⚠️ Skipping {file_path}: {e}")
    return False

def move_files(files, destination_folder):
    global spinner_running
    progress_label.config(text="📂 -> 🗃️ Moving Movies....") 
    progress_bar["maximum"] = len(files)
    start_time = time.time()
    
    spinner_running = True
    threading.Thread(target=animate_spinner, daemon=True).start()
    
    for i, file in enumerate(files, 1):
        try:
            target_path = os.path.join(destination_folder, os.path.basename(file))
            if os.path.exists(target_path):
                continue
            
            for j in range(5):  # Smooth progress effect
                progress_bar["value"] = i - 1 + (j / 5)
                root.update_idletasks()
                time.sleep(0.1)
            
            shutil.move(file, target_path)  # Actual file move
        
        except Exception as e:
            print(f"⚠️ Error moving {file}: {e}")
        
        progress_bar["value"] = i
        elapsed_time = time.time() - start_time
        speed = i / elapsed_time if elapsed_time > 0 else 0
        status_label.config(text=f"📂 Moving {i}/{len(files)} movies... ({speed:.2f} files/sec)")
        root.update_idletasks()
    
    spinner_running = False
    messagebox.showinfo("✅ Done", "🎉 Movies have been sorted successfully!")
    progress_label.config(text="✅ Done!")
    status_label.config(text="All movies moved! 🎬")

def main():
    global spinner_running
    start_button.config(state=tk.DISABLED)
    progress_label.config(text="🔍 Scanning in progress...")
    status_label.config(text="Please wait... 📂")
    
    spinner_running = True
    threading.Thread(target=animate_spinner, daemon=True).start()
    
    selected_drive = filedialog.askdirectory(title="Select a drive or folder to scan")
    if not selected_drive:
        messagebox.showwarning("⚠️ Error", "No folder selected!")
        start_button.config(state=tk.NORMAL)
        spinner_running = False
        return

    all_video_files = find_video_files(selected_drive)
    progress_bar["maximum"] = len(all_video_files)
    print(f"🔍 Total video files found: {len(all_video_files)}")
    
    movie_files = []
    for i, file in enumerate(all_video_files, 1):
        if is_movie(file):
            movie_files.append(file)
        progress_bar["value"] = i
        status_label.config(text=f"📂 Scanning {i}/{len(all_video_files)} files...")
        root.update_idletasks()
    
    spinner_running = False
    
    print(f"✅ Total movies identified: {len(movie_files)}")
    if not movie_files:
        messagebox.showinfo("No Movies", "❌ No movies found!")
        start_button.config(state=tk.NORMAL)
        return
    
    destination_folder = filedialog.askdirectory(title="Select Destination Folder for Movies")
    if not destination_folder:
        messagebox.showwarning("⚠️ Error", "No destination folder selected!")
        start_button.config(state=tk.NORMAL)
        return
    
    if not messagebox.askyesno("Confirm", f"Move {len(movie_files)} movies to {destination_folder}?"):
        start_button.config(state=tk.NORMAL)
        return
    
    move_files(movie_files, destination_folder)
    start_button.config(state=tk.NORMAL)

root.mainloop()
