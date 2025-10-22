from models.widget_detector import WidgetDetector
from openai_integration.openai_client import OpenAIClient
from selenium_web_interaction.selenium_executor_driver import SeleniumExecutorDriver
from utils.BoundingBox import BoundingBox


class ExecutorAgent:
    def __init__(self,
                 execution_driver: SeleniumExecutorDriver,
                 openai_agent: OpenAIClient):
        self.execution_driver = execution_driver
        self.open_ai_agent = openai_agent
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

    def execute(self, actions):
        for action in actions:
            self.action_type = action['action']
            self.target = action['target']
            self.value = action.get('value', '')
        if self.action_type not in self.action_list:
            raise Exception('Not a valid action')
        else:
            functions = self.action_list[self.action_type]
            for func in functions:
                if func != self.wait:
                    func()
                    val_response = self.validation()
                    if val_response == 'Yes':
                        pass
                    else:
                        print('Action was not completed')
                else:
                    func()

    def move_cursor_to(self):
        self.execution_driver.move_cursor_to(self.last_bounding_box)

    def type_string_into(self):
        self.execution_driver.type_string(self.value)

    def click(self):
        self.execution_driver.click()

    def wait(self):
        self.execution_driver.wait(1.5)

    def validation(self):
        valid_screenshot = self.execution_driver.screenshot(draw_cursor=True)
        self.execution_driver.save_screenshot(valid_screenshot, f'Validation_screenshot_for_{self.action_type}')
        validation_prompt= f"""
        Considering the action was {self.action_type} that was supposed to complete the plan {self.action_list[self.action_type]}.
        Do you consider the action was completed?
        Respond only with Yes or No.
        """
        val_response = self.open_ai_agent.send_message_with_images(validation_prompt, images=valid_screenshot)
        return val_response

    def detect_ui_using_YOLO(self):
        full_screenshot=self.execution_driver.screenshot()
        boxes=self.YOLO_detector.predict(full_screenshot)
        image_with_bbox=self.YOLO_detector.attach_bounding_boxes()
        bounding_box=None
        detect_ui_prompt = f"""
        Considering the action plan: {self.action_type}: {self.target}.
        What would be the ID attached to the bounding box that would complete the action?
        Return only the ID of the widget.
        """
        response = self.open_ai_agent.send_message_with_images(detect_ui_prompt, images=image_with_bbox)
        response = int(response)
        for id_b in boxes.keys():
            if id_b == response:
                bounding_box = boxes[id]['bounding_box']
        self.last_bounding_box = BoundingBox(*bounding_box)

    def _init_action_set(self):
        self.action_list={
            'detect': [self.detect_ui_using_YOLO, self.wait],
            'click':  [self.move_cursor_to, self.click, self.wait],
            'type': [self.type_string_into, self.wait]
        }