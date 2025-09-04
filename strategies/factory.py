from strategies.mp4_strategy import MP4DownloadStrategy
from strategies.mp3_strategy import MP3DownloadStrategy

class DownloadStrategyFactory:
    @staticmethod
    def get_strategy(download_type: str, progress_callback=None):
        if download_type == "mp4":
            return MP4DownloadStrategy(progress_callback)
        elif download_type == "mp3":
            return MP3DownloadStrategy(progress_callback)
        else:
            raise ValueError(f"未知的下载类型: {download_type}")