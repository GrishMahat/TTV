import os
from typing import Tuple, List
from PIL import Image
from .google_crawl import run_search
import requests
from utils.common import mkdir


class ImageGrabber:
    def __init__(
        self,
        search_options: str = "",
        resize: bool = False,
        size: Tuple[int, int] = (1920, 1080),
        to_download: int = 20,
    ):
        self._search_options = search_options
        self._resize = resize
        self._size = size
        self.download_folder = os.path.join(os.getcwd(), "downloads")
        self.images_count = 0
        self.to_download = to_download
        self._memory = {}

        # Create downloads folder if it doesn't exist and load local images
        mkdir("downloads")
        self._load_images()

    def _load_images(self) -> None:
        local_files = {}
        directory = os.path.join(os.getcwd(), "downloads")
        for root, _, files in os.walk(directory):
            if root == directory:
                continue
            local_files[os.path.basename(root).lower()] = []
            for file in files:
                local_files[os.path.basename(root).lower()].append(
                    os.path.abspath(os.path.join(root, file))
                )
        self._memory = local_files

    def _download_from_url(self, url: str, keyword: str) -> str:
        self.images_count += 1
        mkdir(f"{self.download_folder}/{keyword}")
        print(f"[INFO] Downloading from URL: {url}")
        print(
            "[INFO] Downloading to: "
            + f"{self.download_folder}/"
            + f"{keyword}/image_{self.images_count}.jpg"
        )
        res = requests.get(url)
        if res.status_code != 200:
            print(f"[INFO] Skipping downloading image, got status {res.status_code}")
            self.images_count -= 1
            return None
        img_data = res.content
        with open(
            f"{self.download_folder}/{keyword}/image_{self.images_count}.jpg",
            "wb",
        ) as handler:
            handler.write(img_data)
        return f"{self.download_folder}/{keyword}/image_{self.images_count}.jpg"

    def search_image(self, keyword: str) -> List[str]:
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
        self._memory[word] = paths
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
                nw = (im.width) * hr
                im = im.resize((int(nw), size[1]), Image.ANTIALIAS)
            else:
                nh = (im.height) * wr
                im = im.resize((size[0], int(nh)), Image.ANTIALIAS)
            x = (size[0] - im.width) // 2
            y = (size[1] - im.height) // 2
            background.paste(im, (x, y))
            if im.format == "WEBP":
                background.save(file + ".jpg", "JPEG")
            else:
                background.save(file, "JPEG")


def main():
    ig = ImageGrabber(resize=True)
    ig.search_image("test")


if __name__ == "__main__":
    main()
