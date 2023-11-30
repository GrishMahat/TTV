import logging
import os
import random
from typing import List, Dict, Tuple

import requests
from PIL import Image
from moviepy.editor import (
    ImageClip,
    VideoClip,
    concatenate_videoclips,
)
from pydub import AudioSegment

from src.image.image_grabber import ImageGrabber

logger = logging.getLogger(__name__)


class VideoSegment:
    IMAGE_FORMAT_RGB = "RGB"
    IMAGE_FORMAT_JPEG = "JPEG"

    def __init__(
        self,
        text: str,
        voiceover_text: List[Dict],
        image_keyword: str,
        segment_number: int,
        images_number: int = 5,
    ):
        self.segment_number = segment_number
        self.text = text
        self.voiceover_text = voiceover_text
        self.image_keyword = image_keyword
        self.images_number = images_number

    def _download_images(self, urls: List[str], keyword: str, download_folder: str):
        images = []
        for url in urls:
            try:
                download_path = os.path.join(download_folder, keyword, f"image_{len(images) + 1}.jpg")
                # Download the image if it doesn't exist in the cache
                if not os.path.exists(download_path):
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(download_path, "wb") as file:
                            file.write(response.content)
                images.append(download_path)
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
        return images

    def _resize_images(self, images: List[str], size: Tuple[int, int]):
        resized_images = []
        for image_path in images:
            try:
                with Image.open(image_path) as img:
                    img = img.convert(self.IMAGE_FORMAT_RGB)
                    img = self._resize_image(img, size)
                    save_path = self._get_save_path(image_path)
                    img.save(save_path, self.IMAGE_FORMAT_JPEG)
                    resized_images.append(save_path)
            except Exception as e:
                logger.error(f"Error resizing images: {e}")
        return resized_images




    def _resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        # Resize logic here
        resized_image = image.resize(size, Image.ANTIALIAS)
        return resized_image


    def _get_save_path(self, image_path: str):
        # Save path logic here
        save_path = os.path.splitext(image_path)[0] + "_resized.jpg"
        return save_path

    def generate_segment(self, tts, gid: ImageGrabber, download_folder: str, size: Tuple[int, int]) -> VideoClip:
        image_urls = gid.search_images(self.image_keyword)
        random_image_urls = random.sample(image_urls, self.images_number)

        # Download images (if not cached) and resize them
        images = self._download_images(random_image_urls, self.image_keyword, download_folder)
        resized_images = self._resize_images(images, size)

        image_clips = [ImageClip(image, duration=0) for image in resized_images]  # Initialize duration to 0

        audio_clips = []
        segment_duration = 0

        for voiceover in self.voiceover_text:
            try:
                audio = tts.generate_tts(voiceover["text"], voiceover["voice"])
                audio_clip = AudioSegment.from_wav(audio)
                duration = len(audio_clip) / 1000  # Convert from milliseconds to seconds
                segment_duration += duration
                audio_clips.append(audio_clip)
            except Exception as e:
                logger.error(f"Error generating audio for voiceover: {e}")

        audio_clip = sum(audio_clips)

        # Update the duration of each image clip
        for clip in image_clips:
            clip = clip.set_duration(segment_duration)

        final_clip = concatenate_videoclips(image_clips, method="compose")
        final_clip = final_clip.set_audio(audio_clip)
        final_clip = final_clip.set_duration(segment_duration)
        final_clip = final_clip.set_fps(24)

        return final_clip

