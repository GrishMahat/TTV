import sys
import os
import logging
from pathlib import Path
from typing import List, Dict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from moviepy.editor import concatenate_videoclips, VideoClip
from src.image.image_grabber import ImageGrabber
from src.text.text_processor import TextProcessor
from src.audio.audio import WaveNetTTS
from src.video.video_segment import VideoSegment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class TextToVideo:
    def __init__(self, text: str, output_file: str, segment_length: int = 100, image_size: tuple = (1920, 1080)):
        self.text = text
        self.output_file = output_file
        self.video_segments: List[VideoClip] = []
        self.segment_number = 1
        self.segment_length = segment_length
        self.image_size = image_size
        self.image_grabber = ImageGrabber(resize=True, size=image_size)
        self.tts = WaveNetTTS()
        self.text_processor = TextProcessor()

    def _extract_keywords(self, text: str, num_keywords: int = 3) -> List[str]:
        # Tokenize and remove stopwords
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text.lower())
        filtered_tokens = [w for w in word_tokens if w.isalnum() and w not in stop_words]

        # Get the most common words as keywords
        freq_dist = nltk.FreqDist(filtered_tokens)
        keywords = [word for word, _ in freq_dist.most_common(num_keywords)]
        return keywords

    def _create_segments(self) -> List[Dict]:
        segments = self.text_processor.split_into_segments(self.text, self.segment_length)
        processed_segments = []

        for i, segment_text in enumerate(segments, start=1):
            keywords = self._extract_keywords(segment_text)
            processed_segments.append({
                "text": segment_text,
                "voiceover_text": [{"text": segment_text, "voice": "default"}],
                "image_keyword": " ".join(keywords),
                "segment_number": i
            })

        return processed_segments

    def process_video_elements(self):
        segments = self._create_segments()
        download_folder = Path("downloads")
        download_folder.mkdir(exist_ok=True)

        for segment in segments:
            try:
                video_segment = VideoSegment(**segment)
                video_clip = video_segment.generate_segment(
                    self.tts, 
                    self.image_grabber, 
                    str(download_folder), 
                    self.image_size
                )
                self.video_segments.append(video_clip)
                logger.info(f"Processed segment {segment['segment_number']}")
            except Exception as e:
                logger.error(f"Error generating video segment {segment['segment_number']}: {e}")
                raise

    def save_video(self):
        if not self.video_segments:
            raise ValueError("No video elements to save.")

        final_clip = concatenate_videoclips(self.video_segments, method="compose")
        final_clip.write_videofile(self.output_file, codec='libx264')
        logger.info(f"Video saved as {self.output_file}")

    def generate_video(self):
        logger.info("Starting video generation process")
        self.process_video_elements()
        self.save_video()
        logger.info("Video generation completed")