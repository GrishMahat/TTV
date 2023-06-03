import random
from typing import List, Dict
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    VideoClip,
    concatenate_videoclips,
    concatenate_audioclips,
)
from audio_utils.audio import WaveNetTTS
from images_utils.image_grabber import ImageGrabber


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

    def generate_segment(self, tts: WaveNetTTS, gid: ImageGrabber) -> VideoClip:
        print(f"[INFO] Generating video segment #{self.segment_number}")
        image_clips = []
        audio_clips = []

        segment_duration = 0

        for idx, voiceover in enumerate(self.voiceover_text):
            audio_file, duration = tts.generate_tts(
                voiceover["text"],
                f"video-segment{self.segment_number}-{idx+1}.mp3",
                voiceover["voice"],
            )
            segment_duration += duration
            audio_clips.append(AudioFileClip(audio_file))

        image_duration = segment_duration / self.images_number
        images = gid.search_image(self.image_keyword)
        random_images = random.sample(images, self.images_number)

        for video_image in random_images:
            image_clips.append(ImageClip(video_image, duration=image_duration))

        audio_clip = concatenate_audioclips(audio_clips)
        final_clip = concatenate_videoclips(image_clips, method="compose")
        final_clip = final_clip.set_audio(audio_clip)
        final_clip = final_clip.set_duration(segment_duration)
        final_clip.fps = 24

        return final_clip
