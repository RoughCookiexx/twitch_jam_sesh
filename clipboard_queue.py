import asyncio

import pyperclip
import time
import keyboard


class ClipboardQueue:
    def __init__(self):
        self.texts = None

    def queue_clipboard(self, texts):
        self.texts = texts
        self.update_clipboard()

    # Function to update clipboard with next item in the list
    def update_clipboard(self):
        if self.texts:
            # Get the next item from the list and copy it to the clipboard
            next_text = self.texts.pop(0)
            pyperclip.copy(next_text)
            print(f"Copied to clipboard: {next_text}")

    # Function to monitor for paste action
    async def monitor_paste(self):
        print("Press 'ctrl+v' to trigger paste (and update clipboard with next item)...")
        while True:
            await asyncio.sleep(0.2)
            if keyboard.is_pressed('ctrl+v'):
                self.update_clipboard()


# if __name__ == "__main__":
#     texts = [
#         "First text",
#         "Second text",
#         "Third text",
#         "Fourth text"
#     ]
#
#     clipboard_queue = ClipboardQueue()
#     clipboard_queue.queue_clipboard(texts)
#     clipboard_queue.monitor_paste()
