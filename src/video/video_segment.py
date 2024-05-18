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

    """
    Class to generate video segments with images and voice-over.

    Attributes:
        text (str): The main text content for the segment.
        voiceover_text (List[Dict]): List of dictionaries containing voiceover text and voice.
        image_keyword (str): Keyword for image search.
        segment_number (int): Segment identifier number.
        images_number (int): Number of images to include in the segment.
    """

    def __init__(self, text: str, voiceover_text: List[Dict], image_keyword: str, segment_number: int, images_number: int = 5):
        self.segment_number = segment_number
        self.text = text
        self.voiceover_text = voiceover_text
        self.image_keyword = image_keyword
        self.images_number = images_number

    def _download_images(self, urls: List[str], keyword: str, download_folder: str) -> List[str]:
        """
        Download images from the provided URLs and save them to the specified folder.

        Args:
            urls (List[str]): List of image URLs to download.
            keyword (str): Keyword associated with the image search.
            download_folder (str): Folder where images will be saved.

        Returns:
            List[str]: List of file paths to the downloaded images.
        """
        images = []
        os.makedirs(os.path.join(download_folder, keyword), exist_ok=True)
        for url in urls:
            try:
                download_path = os.path.join(download_folder, keyword, f"image_{len(images) + 1}.jpg")
                if not os.path.exists(download_path):
                    response = requests.get(url)
                    response.raise_for_status()  # Raises HTTPError for bad responses
                    with open(download_path, "wb") as file:
                        file.write(response.content)
                images.append(download_path)
            except requests.exceptions.RequestException as e:
                logger.error(f"Error downloading image from {url}: {e}")
            except OSError as e:
                logger.error(f"Filesystem error while saving image: {e}")
        return images

    def _resize_images(self, images: List[str], size: Tuple[int, int]) -> List[str]:
        """
        Resize a list of images to the specified size.

        Args:
            images (List[str]): List of file paths to the images to be resized.
            size (Tuple[int, int]): The target size (width, height) for resizing images.

        Returns:
            List[str]: List of file paths to the resized images.
        """
        resized_images = []
        for image_path in images:
            try:
                with Image.open(image_path) as img:
                    img = img.convert(self.IMAGE_FORMAT_RGB)
                    img = self._resize_image(img, size)
                    save_path = self._get_save_path(image_path)
                    img.save(save_path, self.IMAGE_FORMAT_JPEG)
                    resized_images.append(save_path)
            except (OSError, IOError) as e:
                logger.error(f"Error resizing image {image_path}: {e}")
        return resized_images

    def _resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Resize a single image to the specified size.

        Args:
            image (Image.Image): The image to be resized.
            size (Tuple[int, int]): The target size (width, height) for resizing the image.

        Returns:
            Image.Image: The resized image.
        """
        return image.resize(size, Image.ANTIALIAS)

    def _get_save_path(self, image_path: str) -> str:
        """
        Generate the file path for saving a resized image.

        Args:
            image_path (str): The original file path of the image.

        Returns:
            str: The file path to save the resized image.
        """
        return os.path.splitext(image_path)[0] + "_resized.jpg"

    def generate_segment(self, tts, gid: ImageGrabber, download_folder: str, size: Tuple[int, int]) -> VideoClip:
        """
        Generate a video segment with images and voiceovers.

        Args:
            tts: Text-to-speech generator object.
            gid: ImageGrabber object for searching and downloading images.
            download_folder (str): Folder to download images.
            size (Tuple[int, int]): Desired size (width, height) for the images.

        Returns:
            VideoClip: The final video clip with images and audio.
        """
        image_urls = gid.search_images(self.image_keyword)
        random_image_urls = random.sample(image_urls, self.images_number)

        # Download and resize images
        images = self._download_images(random_image_urls, self.image_keyword, download_folder)
        resized_images = self._resize_images(images, size)

        # Create image clips with initial duration of 0
        image_clips = [ImageClip(image).set_duration(0) for image in resized_images]

        audio_clips = []
        segment_duration = 0

        # Generate audio clips from the voiceover text
        for voiceover in self.voiceover_text:
            try:
                audio_path = tts.generate_tts(voiceover["text"], voiceover["voice"])
                audio_clip = AudioSegment.from_wav(audio_path)
                duration = len(audio_clip) / 1000  # Convert from milliseconds to seconds
                segment_duration += duration
                audio_clips.append(audio_clip)
            except Exception as e:
                logger.error(f"Error generating audio for voiceover: {e}")

        # Concatenate all audio clips into one
        if audio_clips:
            audio_clip = sum(audio_clips)
        else:
            audio_clip = AudioSegment.silent(duration=segment_duration * 1000)  # Create silent audio if no clips

        # Set the duration of each image clip to match the total audio duration
        for clip in image_clips:
            clip.set_duration(segment_duration)

        # Concatenate image clips into one final video clip
        final_clip = concatenate_videoclips(image_clips, method="compose")
        final_clip = final_clip.set_audio(audio_clip)
        final_clip = final_clip.set_duration(segment_duration)
        final_clip = final_clip.set_fps(24)

        return final_clip
