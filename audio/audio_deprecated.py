import os
from typing import Tuple
from gtts import gTTS
from mutagen.mp3 import MP3
from utils.common import mkdir


class TTS:
    def __init__(self, download_location: str = "audio"):
        """
        Args:
            download_location (str, optional): Folder to download audio to. Defaults to "audio".
        """
        self._memory = {}
        self.download_location = download_location
        mkdir(download_location)
        self._load_audio()

    def _load_audio(self):
        local_files = {}
        for file in os.listdir(self.download_location):
            audio_file = os.path.join(self.download_location, file)
            if os.path.isfile(audio_file):
                mp3 = MP3(audio_file)
                local_files[file.strip(".mp3")] = (audio_file, mp3.info.length)
        self._memory = local_files

    def getTTS(self, text: str) -> Tuple[str, float]:
        """
        Gets TTS for a given string and downloads it to download_location.

        Args:
            text(str): Text to turn into speech
        Returns:
            Tuple[str, float]: Path to saved file and audio length
        """
        if text in self._memory:
            return self._memory[text]

        tts = gTTS(text)
        audio_file = os.path.join(self.download_location, f"{text}.mp3")
        tts.save(audio_file)

        # Get audio length for video duration
        mp3 = MP3(audio_file)
        self._memory[text] = (audio_file, mp3.info.length)
        return self._memory[text]
