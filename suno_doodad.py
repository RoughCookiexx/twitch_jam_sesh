import pyperclip
import time
import random
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class SunoDoodad:
    def __init__(self):
        options = Options()
        options.debugger_address = "127.0.0.1:9222"  # Attach to an open Chrome session

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Attempt to bypass bot detection
        # self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def human_like_typing(self, element, text):
        """Types text into an element with slight variations to mimic human behavior."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Randomized typing delay

    def generate_suno_song(self, prompt, style, title):
        self.driver.get("https://suno.com/create?wid=default")

        wait = WebDriverWait(self.driver, 10)

        # Locate and input the song prompt
        text_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                              "#main-container > div.css-1d1kf3t > div > div.chakra-stack.w-split-pane.css-14jdhr2 > div > div.px-2.pb-2.flex.flex-col.flex-1.overflow-y-auto.w-full.mb-8 > div.chakra-stack.css-f98g6d > div.css-1a6ryd7 > div.chakra-stack.css-1jx0in4 > div.relative.rounded-lg.bg-quaternary.mt-3 > div.relative.rounded-lg.border.border-quaternary.overflow-hidden.flex-1.bg-tertiary.p-0\\.5.pb-10 > textarea")))

        text_box.click()
        pyperclip.copy(prompt)
        text_box.send_keys(Keys.CONTROL, "v")

        # Locate and input the song style
        style_text_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                    "#main-container > div.css-1d1kf3t > div > div.chakra-stack.w-split-pane.css-14jdhr2 > div > div.px-2.pb-2.flex.flex-col.flex-1.overflow-y-auto.w-full.mb-8 > div.chakra-stack.css-f98g6d > div.css-1a6ryd7 > div.relative.p-4.rounded-lg.border.border-quaternary.overflow-hidden.flex-1.bg-tertiary > textarea")))

        style_text_box.click()
        self.human_like_typing(style_text_box, style)

        # Locate and input the song title
        title_text_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                    "#main-container > div.css-1d1kf3t > div > div.chakra-stack.w-split-pane.css-14jdhr2 > div > div.px-2.pb-2.flex.flex-col.flex-1.overflow-y-auto.w-full.mb-8 > div.chakra-stack.css-f98g6d > div.css-ngugm6 > div.relative.rounded-lg.border.border-quaternary.overflow-hidden.flex-1.bg-tertiary.p-0\\.5 > textarea")))

        title_text_box.click()
        self.human_like_typing(title_text_box, title)

        # Simulate natural mouse movement before clicking generate
        submit_button = self.driver.find_element(By.CSS_SELECTOR,
                                                 "#main-container > div.css-1d1kf3t > div > div.chakra-stack.w-split-pane.css-14jdhr2 > div > div.px-2.pb-2.flex.flex-col.flex-1.overflow-y-auto.w-full.mb-8 > div.flex.flex-col.mb-20 > div > div.create-button.css-508v4f > button")

        action = ActionChains(self.driver)
        time.sleep(random.uniform(1, 5))  # Wait for processing
        action.move_to_element(submit_button).click().perform()

        time.sleep(random.uniform(45, 55))  # Wait for processing
        self.click_new_song()
        print("🎵 Song is playing!")

        time.sleep(random.uniform(3, 7))  # Wait for processing
        # self.driver.quit()

    def click_new_song(self):
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div[id^='react-aria']")

        # Check for the second element and find the button within it
        if len(elements) > 1:
            second_element = elements[1]

            # You could also highlight the second element here for visualization if needed
            self.driver.execute_script("arguments[0].style.border = '2px solid red'", second_element)

            # Find the first button inside the second element
            first_button = second_element.find_element(By.TAG_NAME, "button")

            # Click the button
            first_button.click()


if __name__ == "__main__":
    suno = SunoDoodad()
    suno.generate_suno_song(
        """\
puppies are cool
puppies are great
ruff ruff ruff ruff
let's go on a puppy date!\
        """,
        "Death Metal",
        "Duel of the Fates"
    )

# C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\Tommy\AppData\Local\Google\Chrome\User Data"
#
# #react-aria2523349361-\:r23\:-621a6e13-fb42-4dab-85da-a57a67a19855 > div > div > div > div > div.css-gj6ubv > button
# /html/body/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[1]/div/div[3]/div/div[2]/div/div[1]/div/div/div/div/div[1]/button
#
# #react-aria2523349361-\:r23\:-f3158ff4-2c95-4783-acd6-9bcb3e8eb221 > div > div > div > div > div.css-gj6ubv > button
# /html/body/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[1]/div/div[3]/div/div[2]/div/div[3]/div/div/div/div/div[1]/button
#
# #react-aria2523349361-\:r23\:-108a5c33-55d5-449b-bf2e-cadd33285d2a > div > div > div > div > div.css-gj6ubv > button
# /html/body/div[2]/div[1]/div[2]/div[2]/div/div[1]/div[1]/div/div[3]/div/div[2]/div/div[5]/div/div/div/div/div[1]/button
