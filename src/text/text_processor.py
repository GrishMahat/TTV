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
        matches = re.finditer(TextProcessor.TEXT_TEMPLATES["image"], self.text, re.DOTALL)
        sentences = re.split(TextProcessor.TEXT_TEMPLATES["search_voice"], self.text)

        for i, match in enumerate(matches):
            image_keyword = match.group(1)
            images_number = int(match.group(2) or 5)

            if i < len(sentences):
                sentence = sentences[i].strip()
                voiceover_segments = self._process_voices(sentence)
                video_segment = VideoSegment(sentence, voiceover_segments, image_keyword, i + 1, images_number)
                self.video_segments.append(video_segment)
                self.sentences.append((sentence, image_keyword))

        # Handle remaining sentences here (e.g., log or skip)

    def _process_voices(self, text: str) -> List[Dict]:
        voiceover_segments = []
        for sentence in re.split(TextProcessor.TEXT_TEMPLATES["search_voice"], text):
            sentence = sentence.strip()
            if sentence:
                voiceover_segments.append({"voice": "DEFAULT", "text": sentence})

        for sentence in re.finditer(TextProcessor.TEXT_TEMPLATES["search_voice"], text):
            voice_tag = sentence.group(1)
            voice_text = sentence.group(2).strip()
            for segment in voiceover_segments:
                if segment["text"] == voice_text:
                    segment["voice"] = voice_tag

        return voiceover_segments
