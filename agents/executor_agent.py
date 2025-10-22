from models.widget_detector import WidgetDetector
from openai_integration.openai_client import OpenAIClient
from selenium_web_interaction.selenium_executor_driver import SeleniumExecutorDriver

class ExecutorAgent:
    def __init__(self,
                 execution_driver: SeleniumExecutorDriver,
                 openai_agent: OpenAIClient):
        self.execution_driver = execution_driver
        self.open_ai_agent = openai_agent
        self.YOLO_detector = WidgetDetector()
    open_ai_prompt = """
    You are an Executor Agent that will be responsible of doing and completing actions that are provided in the plan.
    You have to be simple and concise regarding the future prompts that will be provided in order to complete the actions.
    You do not plan sequence of  actions or refletc/verify the correctitude of the actions.
    Constraints:
    - Respond only with valid outputs expected for current action.
    - Do not explain or repeat prompts
    - Do not explain outputs
    """

    def detect_ui_using_YOLO(self):
        full_screenshot=self.execution_driver.screenshot()
        self.YOLO_detector.predict(full_screenshot)
        image_with_bbox=self.YOLO_detector.attach_bounding_boxes()
