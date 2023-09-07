import os
import logging
from typing import Tuple
from google.cloud import texttospeech
from mutagen.mp3 import MP3
from src.utils.common import mkdir  

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

    def __init__(
        self,
        audio_config: texttospeech.AudioConfig = None,
        output_folder: str = "tts_output",
    ):
        self.client = texttospeech.TextToSpeechClient()
        self.audio_config = audio_config or texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=1
        )
        self.output_folder = output_folder
        mkdir(output_folder)

        # Initialize the logger
        self.logger = logging.getLogger(__name__)

    def generate_tts(
        self, text: str, filename: str, voice_name: str = None
    ) -> Tuple[str, float]:
        try:
            # Validate the provided voice_name or use the default
            if voice_name:
                voice_params = WaveNetTTS.VOICES.get(voice_name)
                if voice_params is None:
                    raise ValueError(f"Invalid voice_name: {voice_name}")
            else:
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
                out.write(response.audio_content)
                self.logger.info(f'Audio content written to file "{audio_file}"')

            mp3 = MP3(audio_file)
            return audio_file, mp3.info.length

        except Exception as e:
            self.logger.error(f"Error generating TTS: {str(e)}")
            raise


def generate_tts(
    self, text: str, filename: str, voice_name: str = None
) -> Tuple[str, float]:
   
    # Validate the provided voice_name or use the default
    if voice_name:
        voice_params = WaveNetTTS.VOICES.get(voice_name)
        if voice_params is None:
            raise ValueError(f"Invalid voice_name: {voice_name}")
    else:
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
