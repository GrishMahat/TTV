import os
from typing import Tuple
from google.cloud import texttospeech
from mutagen.mp3 import MP3
from utils.common import mkdir


class WaveNetTTS:
    VOICES = {
        "A": ("en-US-Wavenet-A", 1),
        "B": ("en-US-Wavenet-B", 1),
        "C": ("en-US-Wavenet-C", 2),
        "D": ("en-US-Wavenet-D", 1),
        "E": ("en-US-Wavenet-E", 2),
        "F": ("en-US-Wavenet-F", 2),
        "G": ("en-US-Wavenet-G", 2),
        "H": ("en-US-Wavenet-H", 2),
        "I": ("en-US-Wavenet-I", 1),
        "J": ("en-US-Wavenet-J", 1),
        "DEFAULT": ("en-US-Wavenet-J", 1),
    }

    @classmethod
    def get_voices(cls, gender):
        """Class method to return all voices by given gender

        Args:
            gender (str): gender to filter by

        Returns:
            List[Tuple[str, int]]: List of Tuples of (voice_name, gender)
        """
        if gender.lower() == "male":
            gender = 1
        elif gender.lower() == "female":
            gender = 2
        else:
            return None
        return [v for _, v in WaveNetTTS.VOICES.items() if v[1] == gender]

    def __init__(
        self,
        audio_config: texttospeech.AudioConfig = None,
        output_folder: str = "tts_output",
    ):
        """Initializes client to Google's TTS

        Args:
            audio_config (texttospeech.AudioConfig, optional): Audio configs like pitch, speed, more info on Google TTS
                documentation. Defaults to None.
            output_folder (str, optional): Folder to save output audio files. Defaults to "tts_output".
        """
        self.client = texttospeech.TextToSpeechClient()
        self.audio_config = audio_config
        if self.audio_config is None:
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=1
            )
        self.output_folder = output_folder
        mkdir(output_folder)

    def generate_tts(
        self, text: str, filename: str, voice_name: str = None
    ) -> Tuple[str, float]:
        """Synthesizes speech and generates the audio file for a given text

        Args:
            text (str): text to turn into speech
            filename (str): filename to save output
            voice_name (str, optional): Voice name for WaveNet. Defaults to None.

        Returns:
            Tuple[str, float]: output audio file path, audio file duration in seconds
        """
        if voice_name is None:
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
        else:
            voice_params = WaveNetTTS.VOICES.get(voice_name)
            if voice_params is None:
                voice_params = WaveNetTTS.VOICES["DEFAULT"]
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=voice_params[0],
                ssml_gender=voice_params[1],
            )
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=self.audio_config
        )

        audio_file = os.path.join(self.output_folder, filename)
        with open(audio_file, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print(f'[INFO] Audio content written to file "{audio_file}"')

        mp3 = MP3(audio_file)
        return audio_file, mp3.info.length
