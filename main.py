from coordination.coordinator import Coordinator
import json
import os

if __name__ == "__main__":
    coordinator = Coordinator(start_url="https://www.saucedemo.com/v1/index.html")

    voice_dir = "voice_commands"

    commands = sorted([
        os.path.join(voice_dir, f)
        for f in os.listdir(voice_dir)
        if f.lower().endswith(".wav")
    ])
    #TODO De adaugat fisier in runs
    result = coordinator.run_voice_flow(commands)

    coordinator.shutdown()
