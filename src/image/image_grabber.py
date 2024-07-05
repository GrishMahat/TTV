import os
import requests
from typing import List, Tuple
from PIL import Image
from threading import Lock
import logging

# Ensure the src directory is in the sys.path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import run_search from google_crawl.py
from src.image.google_crawl import run_search

logger = logging.getLogger(__name__)

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
        for root, _, files in os.walk(self.download_folder):
            if root == self.download_folder:
                continue
            keyword = os.path.basename(root).lower()
            local_files[keyword] = [os.path.abspath(os.path.join(root, file)) for file in files]
        self._memory = local_files
        logger.info(f"Loaded {sum(len(files) for files in local_files.values())} images from {len(local_files)} keywords")

    def _initialize_folders(self):
        for folder in [self.download_folder, self.temp_folder]:
            os.makedirs(folder, exist_ok=True)
        logger.info(f"Initialized folders: {self.download_folder}, {self.temp_folder}")

    def _download_from_url(self, url: str, keyword: str) -> str:
        try:
            with self.lock:  # Lock to ensure thread safety
                self.images_count += 1
                download_path = os.path.join(self.download_folder, keyword, f"image_{self.images_count}.jpg")
            
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            with open(download_path, "wb") as handler:
                handler.write(res.content)
            
            logger.debug(f"Downloaded image from {url} to {download_path}")
            return download_path
        except requests.RequestException as e:
            logger.warning(f"Failed to download image from {url}: {e}")
        except IOError as e:
            logger.error(f"Failed to save image from {url}: {e}")
        return None

    def search_images(self, keyword: str) -> List[str]:
        word = keyword.strip().lower()
        if word in self._memory:
            logger.info(f"Using cached images for keyword: {word}")
            return self._memory[word]
        
        logger.info(f"Downloading images for keyword: {word}")
        urls = run_search(word, "off", self.to_download, self._search_options)
        paths = [path for path in (self._download_from_url(url, word) for url in urls) if path is not None]
        
        self._memory[word] = paths
        if self._resize and paths:
            directory = os.path.dirname(paths[0])
            self._resize_images(self._size, directory)
        
        logger.info(f"Downloaded {len(paths)} images for keyword: {word}")
        return paths

    def _resize_images(self, size: Tuple[int, int], directory: str) -> None:
        files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        for file in files:
            try:
                with Image.open(file) as im:
                    if im.mode != "RGB":
                        im = im.convert("RGB")
                    
                    background = Image.new("RGB", size)
                    
                    wr = size[0] / im.width
                    hr = size[1] / im.height
                    if wr > hr:
                        nw = int(im.width * hr)
                        im = im.resize((nw, size[1]), Image.LANCZOS)
                    else:
                        nh = int(im.height * wr)
                        im = im.resize((size[0], nh), Image.LANCZOS)
                    
                    x = (size[0] - im.width) // 2
                    y = (size[1] - im.height) // 2
                    background.paste(im, (x, y))
                    
                    save_path = file if im.format != "WEBP" else f"{file}.{self.IMAGE_FORMAT.lower()}"
                    background.save(save_path, self.IMAGE_FORMAT)
                    logger.debug(f"Resized image: {file}")
            except IOError as e:
                logger.error(f"Failed to resize image {file}: {e}")
