import random
import os
import logging
from typing import List, Dict, Tuple
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    VideoClip,
    concatenate_videoclips,
)
from pydub import AudioSegment
from PIL import Image
from image.image_grabber import ImageGrabber

# Create a logger
logger = logging.getLogger(__name__)

class VideoSegment:
    # Constants
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

    def _download_from_url(self, url: str, keyword: str) -> str:
        try:
            # Your existing download code here
            self.images_count += 1
            mkdir(os.path.join(self.download_folder, keyword))
            print(f"[INFO] Downloading from URL: {url}")
            download_path = os.path.join(
                self.download_folder,
                keyword,
                f"image_{self.images_count}.jpg"
            )
            print(f"[INFO] Downloading to: {download_path}")
            res = requests.get(url)
            if res.status_code != 200:
                print(f"[INFO] Skipping downloading image, got status {res.status_code}")
                self.images_count -= 1
                return None
            with open(download_path, "wb") as handler:
                handler.write(res.content)
            return download_path
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            return None

    def _resize_images(self, size: Tuple[int, int], directory: str) -> None:
        try:
            files = [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))
            ]
            for file in files:
                background = Image.new("RGB", size)
                im = Image.open(file)
                if im.mode != self.IMAGE_FORMAT_RGB:
                    im = im.convert(self.IMAGE_FORMAT_RGB)
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
                    save_path = file + "." + self.IMAGE_FORMAT_JPEG
                else:
                    save_path = file
                background.save(save_path, self.IMAGE_FORMAT_JPEG)
        except Exception as e:
            logger.error(f"Error resizing images: {e}")

    def generate_segment(self, tts, gid: ImageGrabber) -> VideoClip:
        print(f"[INFO] Generating video segment #{self.segment_number}")
        image_clips = []
        audio_clips = []

        segment_duration = 0

        for idx, voiceover in enumerate(self.voiceover_text):
            try:
                audio = tts.generate_tts(voiceover["text"], voiceover["voice"])
                audio_clip = AudioSegment.from_wav(audio)
                duration = len(audio_clip) / 1000  # Convert from milliseconds to seconds
                segment_duration += duration
                audio_clips.append(audio_clip)
            except Exception as e:
                logger.error(f"Error generating audio for voiceover: {e}")

        image_duration = segment_duration / self.images_number
        images = gid.search_images(self.image_keyword)
        random_images = random.sample(images, self.images_number)

        for video_image in random_images:
            try:
                image_clip = ImageClip(video_image, duration=image_duration)
                image_clips.append(image_clip)
            except Exception as e:
                logger.error(f"Error creating image clip: {e}")

        audio_clip = sum(audio_clips)
        final_clip = concatenate_videoclips(image_clips, method="compose")
        final_clip = final_clip.set_audio(audio_clip)
        final_clip = final_clip.set_duration(segment_duration)
        final_clip = final_clip.set_fps(24)

        return final_clip

