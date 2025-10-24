import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class WhisperService:
    """
    Class for speech to text.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPEN_AI_KEY missing.")

        # initialize the client
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio from specific path
        """
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            print(f"Whisper: {transcript.text}")
            return transcript.text
        except Exception as e:
            print(f"Error while transcribing: {e}")
            return ""
