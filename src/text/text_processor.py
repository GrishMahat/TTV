import re
from typing import List, Dict
from src.video.video_segment import VideoSegment

class TextProcessor:
    TEXT_TEMPLATES = {
        "image": r"\[IMAGE:\s*(.+?)(\d*?)]",
        "search_voice": r"\[VOICE:\s*(.+?)](.+?)\[\/VOICE]",
    }

    def __init__(self, text: str):
        self.text = text
        self.video_segments = []
        self.sentences = []
        self._process_text_for_images()

    def _process_text_for_images(self) -> None:
        """
        Processes the text to extract image keywords and create video segments.
        """
        image_matches = list(re.finditer(TextProcessor.TEXT_TEMPLATES["image"], self.text))
        sentences = re.split(TextProcessor.TEXT_TEMPLATES["image"], self.text)

        for i, match in enumerate(image_matches):
            image_keyword = match.group(1).strip()
            images_number = int(match.group(2) or 5)

            if i < len(sentences):
                sentence = sentences[i].strip()
                voiceover_segments = self._process_voices(sentence)
                video_segment = VideoSegment(sentence, voiceover_segments, image_keyword, i + 1, images_number)
                self.video_segments.append(video_segment)
                self.sentences.append((sentence, image_keyword))

        # Process remaining sentences without image tags
        for sentence in sentences[len(image_matches):]:
            sentence = sentence.strip()
            if sentence:
                voiceover_segments = self._process_voices(sentence)
                video_segment = VideoSegment(sentence, voiceover_segments, "", len(self.video_segments) + 1, 0)
                self.video_segments.append(video_segment)
                self.sentences.append((sentence, ""))

    def _process_voices(self, text: str) -> List[Dict]:
        """
        Processes the text to extract voice segments.

        Args:
            text (str): The text to process for voice segments.

        Returns:
            List[Dict]: A list of dictionaries with voice and text pairs.
        """
        voiceover_segments = []
        text_segments = re.split(TextProcessor.TEXT_TEMPLATES["search_voice"], text)
        voice_segments = list(re.finditer(TextProcessor.TEXT_TEMPLATES["search_voice"], text))

        # Add segments without voice tags with default voice
        for segment in text_segments:
            segment = segment.strip()
            if segment:
                voiceover_segments.append({"voice": "DEFAULT", "text": segment})

        # Add segments with specific voice tags
        for voice_segment in voice_segments:
            voice_tag = voice_segment.group(1).strip()
            voice_text = voice_segment.group(2).strip()
            for segment in voiceover_segments:
                if segment["text"] == voice_text:
                    segment["voice"] = voice_tag
                    break

        return voiceover_segments
