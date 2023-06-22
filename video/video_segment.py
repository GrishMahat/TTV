import random
from typing import List, Dict
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    VideoClip,
    concatenate_videoclips,
)
from pydub import AudioSegment
from image.image_grabber import ImageGrabber


class VideoSegment:
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

    def generate_segment(self, tts, gid: ImageGrabber) -> VideoClip:
        print(f"[INFO] Generating video segment #{self.segment_number}")
        image_clips = []
        audio_clips = []

        segment_duration = 0

        for idx, voiceover in enumerate(self.voiceover_text):
            audio = tts.generate_tts(voiceover["text"], voiceover["voice"])
            audio_clip = AudioSegment.from_wav(audio)
            duration = len(audio_clip) / 1000  # Convert from milliseconds to seconds
            segment_duration += duration
            audio_clips.append(audio_clip)

        image_duration = segment_duration / self.images_number
        images = gid.search_images(self.image_keyword)
        random_images = random.sample(images, self.images_number)

        for video_image in random_images:
            image_clip = ImageClip(video_image, duration=image_duration)
            image_clips.append(image_clip)

        audio_clip = sum(audio_clips)
        final_clip = concatenate_videoclips(image_clips, method="compose")
        final_clip = final_clip.set_audio(audio_clip)
        final_clip = final_clip.set_duration(segment_duration)
        final_clip = final_clip.set_fps(24)

        return final_clip
