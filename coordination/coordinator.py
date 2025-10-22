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

    def __init__(self, start_url: str = "https://example.com/login"):
        """
               Initialize all components and open the browser session.
               """
        self.start_url = start_url

        print("Initializing Coordinator components...")

        # 1. Initialize Selenium + PyAutoGUI driver
        self.execution_driver = SeleniumExecutorDriver(
            chromedriver_path="./chromedriver-win32/chromedriver.exe",
            chrome_binary_path="./chrome-win32/chrome.exe",
            start_url=self.start_url
        )

        self.whisper_agent = WhisperService()
        self.decision_maker = DecisionMaker()
        self.executor_agent = ExecutorAgent()

        # Runtime state
        self.last_transcription = None
        self.last_actions = None
        self.execution_log = []

    def _log_prefix(self):
        return f"[Orchestrator][{datetime.now().strftime('%H:%M:%S')}]"

    def run_audio_command(self, audio_path: str):
        """
        Run a complete pipeline for one voice command:
        1. Transcribe voice using Whisper
        2. Interpret text into structured actions using GPT
        3. Execute those actions in the browser
        """

        start_time = time.time()
        logger.info("🎙Step 1: Transcribing audio with Whisper...")
        command_text = self.whisper_agent.transcribe_audio(audio_path)
        logger.info(f"Transcribed command: {command_text}")

        logger.info("Step 2: Interpreting command with DecisionMaker...")
        actions = self.decision_maker.decide(command_text)
        logger.info(f"Generated actions:\n{json.dumps(actions, indent=2)}")

        logger.info("🖱Step 3: Executing actions in browser...")
        results = self.executor_agent.execute(actions)

        elapsed = time.time() - start_time
        logger.info(f"Command executed successfully in {elapsed:.2f}s")

        return {
            "command_text": command_text,
            "actions": actions,
            "results": results,
            "elapsed_time_sec": elapsed
        }

        # --------------------------------------------------------
        # 🔚 Graceful shutdown
        # --------------------------------------------------------

    def shutdown(self):
        """Close the browser session and clean up resources."""
        logger.info("Shutting down browser session...")
        self.execution_driver.quit()
        logger.info("Coordinator shutdown complete.")