from models.widget_detector import WidgetDetector
from openai_integration.openai_client import OpenAIClient
from selenium_web_interaction.selenium_executor_driver import \
    SeleniumExecutorDriver
from utils.BoundingBox import BoundingBox

import logging

logger = logging.getLogger(__name__)

class ExecutorAgent:
    def __init__(self,
                 execution_driver: SeleniumExecutorDriver):
        self.execution_driver = execution_driver
        self.open_ai_agent = OpenAIClient()
        self.YOLO_detector = WidgetDetector()
        system_prompt = """
        You are an Executor Agent that will be responsible of doing and completing actions that are provided in the plan.
        You have to be simple and concise regarding the future prompts that will be provided in order to complete the actions.
        You do not plan sequence of  actions or reflect/verify the correctitude of the actions.
        You will be working in collaboration with a decision maker agent that will provide the needed action information.
        Constraints:
        - Respond only with valid outputs expected for current action.
        - Do not explain or repeat prompts
        - Do not explain outputs
        """
        self.open_ai_agent.send_message(system_prompt)
        self.last_bounding_box = None
        self.action_type = None
        self.target = None
        self.value = None
        self._init_action_set()

    def execute(self, actions):
        for action in actions:
            self.action_type = action.get('action')
            self.target = action.get('target')
            self.value = action.get('value', action.get('text', ''))

            print(
                f"\n Executing action: {self.action_type.upper()} on {self.target} | value='{self.value}'")

            if self.action_type not in self.action_list:
                print(f"Unknown action: {self.action_type}")
                continue

            functions = self.action_list[self.action_type]

            for func in functions:
                print(f"➡️ Running: {func.__name__}")
                try:
                    func()
                except Exception as e:
                    print(f"Error while executing {func.__name__}: {e}")
                    continue

                # validation excluded for wait action
                if func != self.wait:
                    val_response = self.validation()
                    print(f"Validation response: {val_response}")
                    if "yes" not in val_response.lower():
                        print(
                            f"Action {self.action_type} may not have completed properly.")

    def move_cursor_to(self):
        print(f"🖱️ Moving cursor to: {self.last_bounding_box}")
        self.execution_driver.move_cursor_to(self.last_bounding_box)

    def type_string_into(self):
        print(f"⌨️ Typing: '{self.value}'")
        self.execution_driver.type_string(self.value)

    def click(self):
        print(f"🖱️ Clicking current position")
        self.execution_driver.click()

    def wait(self):
        self.execution_driver.wait(1.5)

    def validation(self):
        valid_screenshot = self.execution_driver.screenshot(draw_cursor=True)
        self.execution_driver.save_screenshot(valid_screenshot,
                                              f'Validation_screenshot_for_{self.action_type}.png')
        validation_prompt = f"""
        Considering the action was {self.action_type} that was supposed to complete the plan {self.action_list[self.action_type]}.
        Do you consider the action was completed?
        Respond only with Yes or No.
        """
        val_response = self.open_ai_agent.send_message_with_images(
            validation_prompt, images=valid_screenshot)
        return val_response

    def detect_ui_using_YOLO(self):
        full_screenshot = self.execution_driver.screenshot()
        boxes = self.YOLO_detector.predict(full_screenshot)
        image_with_bbox = self.YOLO_detector.attach_bounding_boxes()
        bounding_box = None
        detect_ui_prompt = f"""
        You are a vision-based detector agent.
        You will receive an image showing several bounding boxes with numeric IDs overlaid.
        The user wants to perform the action: {self.action_type} on target: {self.target}.
        Return ONLY the numeric ID of the box corresponding to that target.
        For example: 1
        No explanation, no extra text.
        """
        response = self.open_ai_agent.send_message_with_images(
            detect_ui_prompt, images=image_with_bbox)
        response = int(response)
        for id_b in boxes.keys():
            if id_b == response:
                bounding_box = boxes[id_b]['bounding_box']
        self.last_bounding_box = BoundingBox(*bounding_box)
        print(f"Detected bounding box: {self.last_bounding_box}")

    def _init_action_set(self):
        self.action_list = {
            'detect': [self.detect_ui_using_YOLO, self.wait],
            'click': [self.move_cursor_to, self.click, self.wait],
            'type': [self.type_string_into, self.wait]
        }
