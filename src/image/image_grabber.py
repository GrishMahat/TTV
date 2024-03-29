import os
import requests
from typing import List, Tuple
from PIL import Image
from threading import Lock
import logging

from src.image.google_crawl import run_search # Import run_search from the same directory

class ImageGrabber:
    IMAGE_FORMAT = "JPEG"

    def __init__(self, search_options: str = "", resize: bool = False, size: Tuple[int, int] = (1920, 1080), to_download: int = 20, download_location: str = "downloads", temp_location: str = "temp"):
        self._search_options = search_options
        self._resize = resize
        self._size = size
        self.download_folder = download_location
        self.temp_folder = temp_location
        self.images_count = 0
        self.to_download = to_download
        self._memory = {}
        self.lock = Lock()  # For thread safety
        self._initialize_folders()
        self._load_images()

    def _load_images(self) -> None:
        local_files = {}
        directory = self.download_folder
        for root, _, files in os.walk(directory):
            if root == directory:
                continue
            local_files[os.path.basename(root).lower()] = [
                os.path.abspath(os.path.join(root, file)) for file in files
            ]
        self._memory = local_files

    def _initialize_folders(self):
        for folder in [self.download_folder, self.temp_folder]:
            os.makedirs(folder, exist_ok=True)

    def _download_from_url(self, url: str, keyword: str) -> str:
        try:
            with self.lock:  # Lock to ensure thread safety
                self.images_count += 1
                download_path = os.path.join(self.download_folder, keyword, f"image_{self.images_count}.jpg")
            res = requests.get(url)
            if res.status_code != 200:
                logging.warning(f"Skipping downloading image, got status {res.status_code}")
                return None
            with open(download_path, "wb") as handler:
                handler.write(res.content)
            return download_path
        except Exception as e:
            logging.error(f"Error downloading image: {e}")
            return None

    def search_images(self, keyword: str) -> List[str]:
        word = keyword.strip()
        if word.lower() in self._memory:
            return self._memory[word.lower()]
        print(f"[INFO] Downloading images for keyword: {word}")
        urls = run_search(word, "off", self.to_download, self._search_options)
        paths = []
        for url in urls:
            path = self._download_from_url(url, word)
            if path is not None:
                paths.append(path)
        self._memory[word.lower()] = paths
        if self._resize and len(paths) > 0:
            directory = os.path.dirname(os.path.abspath(paths[0]))
            self._resize_images(self._size, directory)
        return paths

    def _resize_images(self, size: Tuple[int, int], directory: str) -> None:
        files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]
        for file in files:
            background = Image.new("RGB", size)
            im = Image.open(file)
            if im.mode != "RGB":
                im = im.convert("RGB")
            wr = size[0] / im.width
            hr = size[1] / im.height
            if wr > hr:
                nw = int(im.width * hr)
                im = im.resize((nw, size[1]), Image.ANTIALIAS)
            else:
                nh = int(im.height * wr)
                im = im.resize((size[0], nh), Image.ANTIALIAS)
            x = (size[0] - im.width) // 2
            y = (size[1] - im.height) // 2
            background.paste(im, (x, y))
            if im.format == "WEBP":
                save_path = file + f".{ImageGrabber.IMAGE_FORMAT.lower()}"
            else:
                save_path = file
            background.save(save_path, ImageGrabber.IMAGE_FORMAT)

def main():
    ig = ImageGrabber(resize=True)
    ig.search_images("test")

if __name__ == "__main__":
    main()
