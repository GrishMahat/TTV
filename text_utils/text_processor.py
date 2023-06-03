import re
from typing import List, Dict
from video_utils.video_segment import VideoSegment


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
        print("[INFO] Processing text...")
        self._process_text_for_images()
        print("[INFO] Processed text.")

    def _process_text_for_images(self) -> None:
        matches = re.finditer(TextProcessor.TEXT_TEMPLATES["image"], self.text, re.DOTALL)

        groups = []
        for _, match in enumerate(matches):
            try:
                images_number = int(match.group(2))
            except ValueError:
                images_number = 5
            groups.append((match.group(1), images_number))

        i = 0
        for sentence in re.split(
            TextProcessor.TEXT_TEMPLATES["split_image"], self.text, re.DOTALL
        ):
            if len(sentence) > 0:
                self.video_segments.append(
                    VideoSegment(
                        sentence.strip(),
                        self._process_voices(sentence.strip()),
                        groups[i][0],
                        i + 1,
                        groups[i][1],
                    )
                )
                self.sentences.append((sentence.strip(), groups[i][0]))
                i += 1

    def _process_voices(self, text: str) -> List[Dict]:
        voiceover_segment = []
        for sentence in re.split(
            TextProcessor.TEXT_TEMPLATES["split_voice"], text, re.DOTALL | re.MULTILINE
        ):
            if len(sentence.strip()) > 0:
                voiceover_segment.append({"voice": "DEFAULT", "text": sentence.strip()})

        for sentence in re.finditer(
            TextProcessor.TEXT_TEMPLATES["search_voice"], text, re.DOTALL | re.MULTILINE
        ):
            for idx, t in enumerate(voiceover_segment):
                if t["text"] == sentence.group(2).strip():
                    voiceover_segment[idx]["voice"] = sentence.group(1)

        return voiceover_segment


def main():
    text = "Your text with [IMAGE: keyword1] and [IMAGE: keyword2] tags."
    tp = TextProcessor(text)
    print(tp.sentences)


if __name__ == "__main__":
    main()
