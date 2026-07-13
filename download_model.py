import os
import sys
import urllib.request
import tkinter as tk
from tkinter import ttk

def ensure_model_exists():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    model_dir = os.path.join(base_dir, "models")
    model_path = os.path.join(model_dir, "u2net.onnx")
    url = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    if not os.path.exists(model_path):
        # Create a tiny visual loading window since the terminal is hidden
        root = tk.Tk()
        root.title("Downloading Asset")
        root.geometry("350x120")
        root.resizable(False, False)
        
        # Center the popup on the screen
        root.eval('tk::PlaceWindow . center')

        label = tk.Label(root, text="Downloading background removal model...\nThis happens only on the first launch.", padx=10, pady=10)
        label.pack()

        progress = ttk.Progressbar(root, orient="horizontal", length=280, mode="determinate")
        progress.pack(pady=5)

        status_label = tk.Label(root, text="Starting download...", font=("Arial", 8))
        status_label.pack()

        def progress_hook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                if percent > 100: percent = 100
                progress['value'] = percent
                status_label.config(text=f"Downloaded: {percent}% ({(count * block_size) // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
                root.update()

        def start_download():
            try:
                urllib.request.urlretrieve(url, model_path, reporthook=progress_hook)
                root.destroy() # Close the popup when finished
            except Exception as e:
                status_label.config(text=f"Error: {e}", fg="red")
                root.update()

        # Run the download right after the window graphics initialize
        root.after(100, start_download)
        root.mainloop()
