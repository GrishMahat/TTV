import re
from typing import List, Dict
from video.video_segment import VideoSegment


class TextProcessor:
    TEXT_TEMPLATES = {
        "image": r"\[IMAGE:\s*(.+?)(\d*?)]",
        "split_image": r"\[IMAGE:\s*.+?\d*?]",
        "search_voice": r"\[VOICE:\s*(.+?)](.+?)\[\/VOICE]",
        "split_voice": r"\[VOICE:\s*.+?](.+?)\[\/VOICE]",
    }

    def __init__(self, text: str):
        self.text = text
        self.video_segments = []
        self.sentences = []
        self._process_text_for_images()

    def _process_text_for_images(self) -> None:
        matches = re.finditer(TextProcessor.TEXT_TEMPLATES["image"], self.text, re.DOTALL)
        groups = [(match.group(1), int(match.group(2)) or 5) for match in matches]

        sentences = re.split(TextProcessor.TEXT_TEMPLATES["split_image"], self.text)
        num_sentences = len(sentences)
        num_groups = len(groups)
        num_segments = min(num_sentences, num_groups)

        for i in range(num_segments):
            sentence = sentences[i].strip()
            voiceover_segments = self._process_voices(sentence)
            image_keyword, images_number = groups[i]
            video_segment = VideoSegment(sentence, voiceover_segments, image_keyword, i + 1, images_number)
            self.video_segments.append(video_segment)
            self.sentences.append((sentence, image_keyword))
        
        remaining_sentences = sentences[num_segments:]
        # Handle the remaining sentences as needed (e.g., skip or process differently)

    def _process_voices(self, text: str) -> List[Dict]:
        voiceover_segments = []
        for sentence in re.split(TextProcessor.TEXT_TEMPLATES["split_voice"], text):
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
