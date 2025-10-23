from coordination.coordinator import Coordinator
import json
from utils.file_utils import get_sorted_audio_files

if __name__ == "__main__":
    coordinator = Coordinator(
        start_url="https://www.saucedemo.com/v1/index.html")

    commands = get_sorted_audio_files()

    result = coordinator.run_voice_flow(commands)

    print(json.dumps(result, indent=2))

    coordinator.shutdown()
