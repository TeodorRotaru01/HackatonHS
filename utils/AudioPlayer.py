import pygame

def play_audio(file_path: str):
    """
    Play a .wav or .mp3 file using pygame.
    This blocks until the sound finishes.
    """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print(f"🔊 Playing: {file_path}")

        # Wait until playback finishes
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        pygame.mixer.quit()

    except Exception as e:
        print(f"⚠️ Error playing {file_path}: {e}")