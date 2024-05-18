import logging
from pathlib import Path
from moviepy.editor import concatenate_videoclips, VideoClip
from src.image.image_grabber import ImageGrabber
from src.text.text_processor import TextProcessor
from src.audio.audio import WaveNetTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextToVideo:
    def __init__(self, text: str, output: str):
        """
        Initialize the TextToVideo object.

        Args:
            text (str): The input text to be processed.
            output (str): The filename for the output video.
        """
        self.text = text
        self.output = output
        self.image_grabber = ImageGrabber(search_options="ift:jpg", resize=True)
        self.text_processor = TextProcessor(self.text)
        self.tts = WaveNetTTS()
        self.output_folder = "output"
        self.video_clips = []
        self.output_path = self._get_output_path()

    def process_video_elements(self):
        """
        Process each segment in the text and generate video elements.
        """
        for segment in self.text_processor.video_segments:
            try:
                final_clip = segment.generate_segment(self.tts, self.image_grabber)
                if final_clip:
                    self.video_clips.append(final_clip)
            except Exception as e:
                logger.error(f"Error generating video segment: {e}")

    def save_video(self, fps: int = 24):
        """
        Save the concatenated video clips into a single video file.

        Args:
            fps (int, optional): Frames per second for the output video. Defaults to 24.

        Raises:
            NoVideoElementsException: If no video elements are available to save.
        """
        if not self.video_clips:
            raise NoVideoElementsException("No video elements to save.")

        try:
            final_video = concatenate_videoclips(self.video_clips, method="compose")
            final_video = final_video.set_fps(fps)
            final_video.write_videofile(str(self.output_path), codec="libx264", audio_codec="aac")
            logger.info(f"Video saved to {self.output_path}")
        except Exception as e:
            logger.error(f"Error saving video: {e}")

    def _get_output_path(self) -> Path:
        """
        Get the output path for the video file.

        Returns:
            Path: The path to save the output video.
        """
        output_dir = Path(self.output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / self.output

class NoVideoElementsException(Exception):
    """Exception raised when no video elements are available to save."""
    pass

