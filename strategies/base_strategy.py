from abc import ABC, abstractmethod

class DownloadStrategy(ABC):
    @abstractmethod
    def download(self, url: str, output_path: str):
        pass