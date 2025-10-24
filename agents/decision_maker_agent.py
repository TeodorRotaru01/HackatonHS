import json
import logging
import re
from dotenv import load_dotenv

from openai_integration.openai_client import OpenAIClient

logger = logging.getLogger(__name__)

load_dotenv()


class DecisionMaker:
    """
    DecisionMaker interprets natural language (spoken or written)
    and decides what UI action should be performed.
    Example output:
        {"action": "click", "target": "username_input"}
    """

    def __init__(self, selenium_driver, model: str = "gpt-4o"):
        # Load environment variables
        self.SeleniumExecutorDriver = selenium_driver

        # Initialize OpenAI client
        self.client = OpenAIClient(model=model)

    def decide(self, text: str) -> dict:
        """
        Takes the transcribed text from the user and returns a structured JSON
        describing what action should be performed on the interface.
        """

        system_prompt = (
            """
        You are the DecisionMaker Agent in an automated UI control system.

        Your goal is to analyze a user's spoken instruction and decide the next UI action to perform.
        Your available atomic actions are strictly limited to:
        
        1. Detection — use YOLO-based object detection to locate a UI element (e.g., button, input field, icon).
        2. Click — perform a left-click on the detected element.
        3. Type — input text into a detected text field.
        4. Wait — wait for a short duration (used for loading or transitions).
        
        Constraints:
        - Always detect before clicking or typing (YOLO detection first).
        - Never perform actions not listed above.
        - Always return a single structured JSON object describing the action.
        - Do not include explanations, reasoning, or additional text outside the JSON.
        - Be deterministic and concise.
        - Base your reasoning only on the visual state (if provided) and the user instruction.
        
        OUTPUT FORMAT
        Return a JSON array of objects, each describing one action. For example:
        {
            {"action": "detect", "target": "username_field"},
            {"action": "click", "target": "username_field"}
        }
        """
        )

        user_prompt = f"User command: \"{text}\""

        try:
            # 🖼️ Capture current screen directly from SeleniumExecutorDriver
            screenshot = self.SeleniumExecutorDriver.screenshot(
                draw_cursor=True)

            # 🔍 Send the text + image to GPT
            response_text = self.client.send_message_with_images(
                message=user_prompt,
                images=screenshot,
                system_prompt=system_prompt
            ).strip()

            # Try parsing JSON output
            clean_response = re.sub(r"^```[a-zA-Z]*\n?", "", response_text.strip())
            clean_response = re.sub(r"```$", "", clean_response.strip())

            # ✅ Try to parse JSON
            try:
                parsed = json.loads(clean_response)

                # Normalize output (ensure it's always a list)
                if isinstance(parsed, dict):
                    parsed = [parsed]

            except json.JSONDecodeError:
                parsed = {"error": "Could not parse JSON",
                          "raw_response": response_text}

            return parsed
        except Exception as e:
            logger.error(f"❌ DecisionMaker failed: {e}")
            return {"action": "none", "target": None, "value": None}
