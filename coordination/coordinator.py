from openai_integration.whisper_client import WhisperService
from agents.decision_maker_agent import DecisionMaker
from agents.executor_agent import ExecutorAgent
import json
from selenium_web_interaction.selenium_executor_driver import SeleniumExecutorDriver
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class Coordinator:
    """
    Whisper -> DecisionMaker -> ChromeController -> ExecutorAgent
    """

    def __init__(self, start_url: str):
        """
        Initialize browser session and AI agents.
        """
        self.start_url = start_url

        # Initialize Selenium + PyAutoGUI controller
        self.execution_driver = SeleniumExecutorDriver(
            chromedriver_path="./chromedriver-win32/chromedriver.exe",
            chrome_binary_path="./chrome-win32/chrome.exe",
            start_url=self.start_url
        )

        # Initialize agents
        self.whisper_agent = WhisperService()
        self.decision_maker = DecisionMaker()
        self.executor_agent = ExecutorAgent(self.execution_driver)

        # Keep a full flow log for session summary
        self.session_actions = []
        self.session_start_time = None

    # --------------------------------------------------------
    # 🔁 Multi-command voice flow
    # --------------------------------------------------------
    def run_voice_flow(self, audio_commands: list[str]):
        """
        Run a sequence of voice commands (audio files) within the same browser session.
        Each audio file is transcribed, parsed, and executed sequentially.
        """

        self.session_start_time = time.time()
        logger.info("🎬 Starting multi-command voice flow...")

        for i, audio_path in enumerate(audio_commands, start=1):
            logger.info(f"\n=== 🗣Executing voice command {i}/{len(audio_commands)} ===")

            # Step 1: Transcribe voice
            text = self.whisper_agent.transcribe_audio(audio_path)
            logger.info(f"Command text: {text}")

            # Step 2: Parse command into actions
            actions = self.decision_maker.decide(text)
            logger.info(f"Parsed actions:\n{json.dumps(actions, indent=2)}")

            # Step 3: Execute actions
            results = self.executor_agent.execute(actions)

            # Log result
            self.session_actions.append({
                "audio_file": audio_path,
                "command_text": text,
                "actions": actions,
                "results": results
            })

        total_time = time.time() - self.session_start_time
        logger.info(f"Completed {len(audio_commands)} voice commands in {total_time:.2f}s.")

        return {
            "total_commands": len(audio_commands),
            "session_duration_sec": total_time,
            "executed": self.session_actions
        }

        # --------------------------------------------------------
        # Shutdown
        # --------------------------------------------------------

    def shutdown(self):
        """Close the browser session and clean up resources."""
        logger.info("Shutting down browser session...")
        self.execution_driver.quit()
        logger.info("Coordinator shutdown complete.")