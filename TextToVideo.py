import os
from pathlib import Path
from moviepy.editor import concatenate_videoclips
from image.image_grabber import ImageGrabber
from text.text_processor import TextProcessor
from audio.audio import WaveNetTTS


class TextToVideo:
    def __init__(self, text: str, output: str):
        """This class processes the images and audio then generates the required video

        Args:
            text (str): Text to turn into images/audio
            output (str): Output file name
        """
        self.text = text
        self.output = output
        self.gid = ImageGrabber(search_options="ift:jpg", resize=True)
        self.text_processor = TextProcessor(self.text)
        self.wnTTS = WaveNetTTS()
        self.output_folder = "output"
        self.video_clips = []
        self.output_path = self.get_output_path()

    def process_video_elements(self):
        """Processes the video elements to generate video clips/segments"""
        video_segments = self.text_processor.video_segments
        for segment in video_segments:
            final_clip = segment.generate_segment(self.wnTTS, self.gid)
            self.video_clips.append(final_clip)

    def save_video(self, fps: int = 24):
        """Saves the processed video

        Args:
            fps (int, optional): Desired video FPS. Defaults to 24.
        """
        if not self.video_clips:
            raise VideoElementsNotProcessed("No video elements to save.")

        final_video = concatenate_videoclips(self.video_clips, method="compose")
        final_video = final_video.set_fps(fps)
        final_video.write_videofile(str(self.output_path))

    def get_output_path(self) -> Path:
        """Returns the output file path"""
        output_dir = Path(os.getcwd()) / self.output_folder
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / self.output


class VideoElementsNotProcessed(Exception):
    pass
