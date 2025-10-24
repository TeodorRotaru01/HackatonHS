import os
import re


def get_sorted_audio_files(folder_name: str = "voice_commands"):
    """
    Return a numerically sorted list of .wav files from a given folder
    in the current working directory.
    """
    files = [f for f in os.listdir(folder_name) if f.endswith(".wav")]
    files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    return [os.path.join(folder_name, f) for f in files]
