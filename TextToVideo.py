from pathlib import Path
import logging
from moviepy.editor import concatenate_videoclips
from image.image_grabber import ImageGrabber
from text.text_processor import TextProcessor
from audio.audio import WaveNetTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextToVideo:
    def __init__(self, text: str, output: str):
        self.text = text
        self.output = output
        self.gid = ImageGrabber(search_options="ift:jpg", resize=True)
        self.text_processor = TextProcessor(self.text)
        self.wnTTS = WaveNetTTS()
        self.output_folder = "output"
        self.video_clips = []
        self.output_path = self._get_output_path()

    def process_video_elements(self):
        for segment in self.text_processor.video_segments:
            try:
                final_clip = segment.generate_segment(self.wnTTS, self.gid)
                if final_clip is not None:
                    self.video_clips.append(final_clip)
            except Exception as e:
                logger.error(f"Error generating video segment: {e}")

    def save_video(self, fps: int = 24):
        if not self.video_clips:
            raise NoVideoElementsException("No video elements to save.")

        try:
            final_video = concatenate_videoclips(self.video_clips, method="compose")
            final_video = final_video.set_fps(fps)
            final_video.write_videofile(str(self.output_path))
            logger.info(f"Video saved to {self.output_path}")
        except Exception as e:
            logger.error(f"Error saving video: {e}")

    def _get_output_path(self) -> Path:
        output_dir = Path.cwd() / self.output_folder
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / self.output


class NoVideoElementsException(Exception):
    pass
