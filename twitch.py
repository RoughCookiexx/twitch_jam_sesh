import threading
import time
import pyttsx3
from datetime import datetime

from openai import OpenAI
from twitchAPI.object.eventsub import ChatMessage
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData

import asyncio
import pygame
import tkinter
import yt_dlp

import chatgpt
import secrets
from descriptors import generate_song_description
from main import get_audio_information, custom_generate_audio
from mic_input import MicInput
from obs_timer import ObsTimer
from suno_doodad import SunoDoodad

ALL_MESSAGES = ''
MINUTES_BETWEEN_SONGS = 0.1


class TwitchJamSesh:

    def __init__(self):
        self.song_description = []
        self.suno = SunoDoodad()
        self.tts_engine = pyttsx3.init()
        self.obs_timer = None

    def begin(self):
        mic_input = MicInput(self.song_description)

        root = tkinter.Tk()
        root.title("OBS Timer")
        root.geometry("300x100")

        timer_label = tkinter.Label(root, text="00:00", font=("Helvetica", 24))
        timer_label.pack(expand=True)
        self.obs_timer = ObsTimer(event=self.trigger_song_creation, label=timer_label, tk=root)
        self.obs_timer.start_timer(MINUTES_BETWEEN_SONGS)

        root.mainloop()

        threads = [
            threading.Thread(target=mic_input.listen_for_keyword),
            threading.Thread(target=self.twitch_listener_thread),
            threading.Thread(target=self.obs_timer.update_timer)
        ]
        # Start all the threads
        for thread in threads:
            thread.start()

        # Join threads to wait for them to finish
        for thread in threads:
            thread.join()

    def speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    async def read_message(self, message: ChatMessage):
        if 'Cheer' not in message.text:
            self.song_description.append(message.text)

        print(self.song_description)

    def trigger_song_creation(self):
        try:
            reply = chatgpt.send_message_to_chatgpt(
                f"Take the contents from below, and turn it into a short song. Generate the lyrics for us."
                f"Keep the lyrics between 750 and 1,250 characters."
                f"Don't be afraid to go off on a bit of a tangent. "
                f"Annotate sections of the song like this: [INTRO], [VERSE 1], etc. etc. "
                f"Only return the lyrics, no introduction. no conclusion. "
                f"Use your own words aside from a direct quote or two."
                f"no 'here is your summary bullshit'. "
                f"just get to the point.\n"
                f"  {','.join(self.song_description)}",
                client)

            tags = generate_song_description()
            title = chatgpt.send_message_to_chatgpt(
                f"Take the following content and reply with only a title for a song. Return only alphanumeric characters: {reply}",
                client)

            print(title)
            print(tags)
            print(reply)

            reply = reply[:2000]

            self.suno.generate_suno_song(reply, tags, title)
        except Exception:
            self.tts_engine.say("SONG GENERATION FAILED. GO WATCH MORE PRIMAGEN.")
            pass
        finally:
            self.obs_timer.start_timer(MINUTES_BETWEEN_SONGS)
            self.song_description = []

    async def on_ready(self, ready_event: EventData):
        await ready_event.chat.join_room('roughcookie')

    def run_coroutine(self, coroutine):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coroutine)
        loop.close()

    def twitch_listener_thread(self):
        self.run_coroutine(self.listen_to_redemptions())

    async def listen_to_redemptions(self):
        twitch = await Twitch(secrets.CLIENT_ID, secrets.CLIENT_SECRET)
        auth = UserAuthenticator(twitch, [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT])

        # Authenticate the user and get the token
        token, refresh_token = await auth.authenticate()

        # Set the token
        await twitch.set_user_authentication(token, [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT], refresh_token)

        chat = await Chat(twitch)
        chat.register_event(ChatEvent.READY, self.on_ready)
        chat.register_event(ChatEvent.MESSAGE, self.read_message)
        chat.start()

        # Keep it alive
        while True:
            time.sleep(1)

    async def play_audio_stream(self, url, lyrics, title):
        # Set up the yt-dlp options to download audio only
        filename = f'{datetime.now().strftime("%Y%m%d%H%M%S")}.mp3'
        ydl_opts = {
            'outtmpl': filename  # Output filename
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # Download the audio stream

        with open('title', "w") as file:
            file.write(title)

        with open('lyrics', "w") as file:
            file.write(lyrics)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()


if __name__ == '__main__':
    pygame.mixer.init()
    client = OpenAI(api_key=secrets.CHAT_GPT_API_KEY)
    jam_sesh = TwitchJamSesh()
    jam_sesh.begin()
