import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
import time

SAMPLE_RATE = 44100
OUTPUT_DIR = "voice_commands"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🎤 Voice Recorder Ready!")
print("Press ENTER to start recording.")
print("Speak your command, then press CTRL+C to stop recording.")
print("Type 'exit' and press ENTER to quit.\n")

counter = 3

while True:
    cmd = input(f"▶️ Press ENTER to record command #{counter}, or type 'exit' to quit: ").strip().lower()
    if cmd == "exit":
        print("👋 Exiting recorder.")
        break

    print("🎙️ Recording... Speak now (press Ctrl+C to stop).")

    try:
        # Start recording
        recording = []
        sd.default.samplerate = SAMPLE_RATE
        sd.default.channels = 1

        def callback(indata, frames, time_info, status):
            recording.append(indata.copy())

        with sd.InputStream(callback=callback):
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("🛑 Stopped recording.")

        # Combine all recorded chunks
        if len(recording) > 0:
            audio = np.concatenate(recording, axis=0)
            filename = os.path.join(OUTPUT_DIR, f"{counter}.wav")
            write(filename, SAMPLE_RATE, audio)
            print(f"✅ Saved: {filename}\n")
            counter += 1
        else:
            print("⚠️ No audio captured, skipping.\n")

    except Exception as e:
        print(f"❌ Recording failed: {e}\n")
        continue