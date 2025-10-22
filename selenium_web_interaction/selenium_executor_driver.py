import time
import math
from datetime import datetime
from typing import Optional, Tuple
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from utils.BoundingBox import BoundingBox
import os


class SeleniumExecutorDriver:
    """
    Minimal UI execution layer using Selenium + PyAutoGUI.
    Focused on real cursor control, clicking, typing, and waiting.
    """

    def __init__(self, chromedriver_path: str, chrome_binary_path: str,
                 start_url: str,
                 test_run_folder: str):
        """
        Initialize ChromeDriver with a visible window and optional starting URL.
        """

        # --- Configure Chrome
        options = Options()
        options.binary_location = chrome_binary_path
        options.add_argument("--start-maximized")

        service = ChromeService(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.arrow_cursor_img = './selenium_web_interaction/arrow_cursor.png'
        self.test_run_folder = test_run_folder

        # Load optional start URL
        if start_url:
            self.load_url(start_url)

        # Store screen size for safety bounds
        self.screen_width, self.screen_height = pyautogui.size()

    # ----------------------------------------------------------
    # 🧭 BASIC BROWSER CONTROL
    # ----------------------------------------------------------

    def load_url(self, url: str):
        """Open a given URL in the controlled Chrome instance."""
        self.driver.get(url)
        time.sleep(2)  # wait for layout to load

    def quit(self):
        """Gracefully close the browser."""
        self.driver.quit()

    # ----------------------------------------------------------
    # 🖱️ CURSOR CONTROL
    # ----------------------------------------------------------
    # TODO wait for BoundingBox
    def move_cursor_to(
            self,
            bounding_box: Optional[BoundingBox] = None,
            offset: Optional[Tuple[int, int]] = None,
            direction: Optional[Tuple[float, float]] = None,
            distance: Optional[float] = None,
    ):
        """
        Move the OS cursor:
        - To the center of a bounding box (optional offset)
        - Or in a direction vector by a given distance
        """

        if bounding_box:
            # Move to the center of a specific region
            x, y = bounding_box.center()
            if offset:
                x += offset[0]
                y += offset[1]
            pyautogui.moveTo(x, y, duration=0.3)
            return

        elif direction and distance:
            dx, dy = direction
            length = math.hypot(dx, dy)
            if length == 0:
                print("[WARNING] Zero-length direction vector.")
                return
            dx_norm = dx / length
            dy_norm = dy / length

            move_x = dx_norm * distance
            move_y = dy_norm * distance

            current_x, current_y = pyautogui.position()
            pyautogui.moveTo(current_x + move_x, current_y + move_y,
                             duration=0.3)
            return

        else:
            print("[WARNING] move_cursor_to called without parameters.")

    # ----------------------------------------------------------
    # 🖱️ CLICK / TYPE
    # ----------------------------------------------------------

    def click(self, double_click: bool = False):
        """Perform a left mouse click (or double click) at current cursor position."""
        if double_click:
            pyautogui.doubleClick()
        else:
            pyautogui.click()

    def type_string(self, text: str, delay_between_keys: float = 0.05):
        """Type a string into the currently focused input field."""
        pyautogui.typewrite(text, interval=delay_between_keys)

    # ----------------------------------------------------------
    # ⏳ WAIT
    # ----------------------------------------------------------

    def wait(self, seconds: float = 2.0):
        """Pause execution for a number of seconds."""
        time.sleep(seconds)

    def screenshot(self, draw_cursor=False):
        image_shoted = pyautogui.screenshot()  # type: ignore
        # TODO, am comentat asta pentru ca crapa.
        # mouse_x, mouse_y = pyautogui.position()
        # if draw_cursor:
        #     image_shoted.paste(self.arrow_cursor_img, (mouse_x, mouse_y))
        return image_shoted

    def save_screenshot(self, image, filename: str):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(self.test_run_folder, f'{now}_{filename}')
        # TODO Am adaugat asta sa nu crape, dar nu salveaza nimic.
        os.makedirs(os.path.dirname(path), exist_ok=True)
        image.save(path)
