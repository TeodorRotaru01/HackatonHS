import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
class DecisionMaker:
    """
    DecisionMaker interprets natural language (spoken or written)
    and decides what UI action should be performed.
    Example output:
        {"action": "click", "target": "username_input"}
    """

    def __init__(self):
        # Load environment variables
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is not defined in .env!")

        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)

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
        Return a single JSON object with two keys:
        {
          "action": "<detect | click | type | wait | none>",
          "target": "<name_of_ui_element_or_null>"
        }
        """
        )

        user_prompt = f"User command: \"{text}\""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )

            content = response.choices[0].message.content.strip()

            # Try to parse the JSON response
            return json.loads(content)

        except Exception as e:
            print(f"Error in DecisionMaker: {e}")
            return {"action": "none", "target": None}