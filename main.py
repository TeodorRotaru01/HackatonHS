from coordination.coordinator import Coordinator
import json
import os

if __name__ == "__main__":
    coordinator = Coordinator(start_url="https://www.saucedemo.com/v1/index.html")

    # Define the ordered voice commands (recorded files)
    # Path către folderul unde ai fișierele .wav
    voice_dir = "voice_commands"

    # Citește toate fișierele .wav din folder, sortate alfabetic
    commands = sorted([
        os.path.join(voice_dir, f)
        for f in os.listdir(voice_dir)
        if f.lower().endswith(".wav")
    ])

    result = coordinator.run_voice_flow(commands)

    print("=== SESSION SUMMARY ===")
    print(json.dumps(result, indent=2))

    coordinator.shutdown()
