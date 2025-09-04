import yt_dlp
import os
from .base_strategy import DownloadStrategy

class MP4DownloadStrategy(DownloadStrategy):
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def download(self, url: str, output_path: str):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'retries': 3,
            'fragment_retries': 3,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        if self.progress_callback:
            def hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', 'N/A')
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    self.progress_callback(percent, speed, eta)
            ydl_opts['progress_hooks'] = [hook]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])