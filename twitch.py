import os
import random
import tempfile
import threading
import time
import pyttsx3
from datetime import datetime

import requests
from elevenlabs import ElevenLabs
from openai import OpenAI
from twitchAPI.object.eventsub import ChatMessage
from twitchAPI.pubsub import PubSub
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData

import asyncio
import pygame
import tkinter
import yt_dlp
import elevenlabs

import chatgpt
import secrets
from descriptors import generate_song_description
from mic_input import MicInput
from obs_timer import ObsTimer
from obswebsocket import obsws, requests as obs_requests

from clipboard_queue import ClipboardQueue
# from suno_doodad import SunoDoodad

ALL_MESSAGES = ''
MINUTES_BETWEEN_SONGS = 20

elevenlabs = ElevenLabs(api_key=secrets.ELEVENLABS_API_KEY)

voices = ['iCVkdoGNYLTCRiLXC3Iu',
          'kbTLheY1CmCRIqLetJJL',
          'oQ2gVLvmfdFGixPqL5m2',
          'iHSDkze8smw4MQyIFKPZ',
          'Tn4bhLlhD26sndFn0Kgw',
          'IZA1V6HYiBphGehfV21Q',
          'YVyp28LAMQfmx8iIH88U',
          'FmJ4FDkdrYIKzBTruTkV',
          'j7KV53NgP8U4LRS2k2Gs',
          'fThYUEUmlC2mx7fgTahR',
          'ryn3WBvkCsp4dPZksMIf'
          ]

class TwitchJamSesh:


    def __init__(self):
        self.song_description = []
        # self.suno = SunoDoodad()

        # OBS WebSocket settings
        self.obs_host = "localhost"  # OBS WebSocket host
        self.obs_port = 4455  # WebSocket port (default)
        self.obs_password = "XYWYGiiqfZl1rXlU"  # Replace with your OBS WebSocket password

        # Connect to OBS
        self.ws = obsws(self.obs_host, self.obs_port, self.obs_password)
        self.ws.connect()

        self.clipboard_queue = ClipboardQueue()

    def begin(self):
        mic_input = MicInput(self.song_description)

        threads = [
            threading.Thread(target=mic_input.listen_for_keyword),
            threading.Thread(target=self.twitch_listener_thread),
            threading.Thread(target=self.clipboard_queue.monitor_paste)
        ]
        # Start all the threads
        for thread in threads:
            thread.start()

        # Join threads to wait for them to finish
        for thread in threads:
            thread.join()

    async def read_message(self, message: ChatMessage):

        if 'Cheer' in message.text:
            return

        filtered_message = message.text  # Start with the full message

        if message.emotes:
            # Sort the emotes by start_position to remove them in reverse order
            sorted_emotes = sorted(message.emotes.values(), key=lambda e: int(e[0]['start_position']), reverse=True)

            # Loop through each emote in reverse order and remove it from the message
            for emote in sorted_emotes:
                start_pos = int(emote[0]['start_position'])-1
                end_pos = int(emote[0]['end_position'])+1

                # Remove the emote from the message
                filtered_message = filtered_message[:start_pos] + filtered_message[end_pos:]

        print(filtered_message)
        self.song_description.append(message.text)


    async def on_channel_point_redemption(self, uuid: str, data: dict) -> None:
        message = data.get('data').get('redemption').get('user_input')
        event = data.get('data').get('redemption').get('reward').get('title')
        if event == 'Request Song':
            self.trigger_song_creation()

    def trigger_song_creation(self):
        try:
            lyrics = chatgpt.send_message_to_chatgpt(
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
                f"Take the following content and reply with only a title for a song. Return only alphanumeric characters: {lyrics}",
                client)

            blurb = chatgpt.send_message_to_chatgpt(
                f"Take the following lyrics and create a little blurb a caller might say to prompt the DJ to play this song. "
                f"Give a little preface, how you're feeling, and why you want to hear the type of song you want to hear."
                f" \n\n {lyrics}",
                client,
                1)

            print(lyrics)
            print(f'TITLE: {title}')
            print(f'DESCRIPTION: {tags}')

            lyrics = lyrics[:2000]

            self.clipboard_queue.queue_clipboard([lyrics, tags, title])

            # self.suno.generate_suno_song(lyrics, tags, title)

            self.change_scene("Radio Station")
            time.sleep(10)
            self.caller_blurb(blurb)


        except Exception as e:
            print(e)
            pass
        finally:
            self.song_description = []

    def caller_blurb(self, message):
        filename = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.mp3'
        self.gen_blurb(message, filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

    def change_scene(self, scene_name):
        pygame.mixer.music.load("Office_phone_ringing.mp3")
        pygame.mixer.music.play()
        self.ws.call(obs_requests.SetCurrentProgramScene(sceneName=scene_name))
        time.sleep(2)
        pygame.mixer.music.play()

    async def on_ready(self, ready_event: EventData):
        await ready_event.chat.join_room('roughcookie')

    def run_coroutine(self, coroutine):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coroutine)
        loop.close()

    def twitch_listener_thread(self):
        self.run_coroutine(self.listen_to_redemptions())

    async def listen_to_redemptions(self, TARGET_CHANNEL_ID=None):
        twitch = await Twitch(secrets.CLIENT_ID, secrets.CLIENT_SECRET)
        auth = UserAuthenticator(twitch, [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_READ_REDEMPTIONS])

        # Authenticate the user and get the token
        token, refresh_token = await auth.authenticate()

        # Set the token
        await twitch.set_user_authentication(token, [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT,
                                                     AuthScope.CHANNEL_READ_REDEMPTIONS], refresh_token)

        pubsub = PubSub(twitch)
        pubsub.start()

        # Hook up the PubSub listener for channel points redemptions
        uuid = await pubsub.listen_channel_points('38606166', self.on_channel_point_redemption)

        chat = await Chat(twitch)
        chat.register_event(ChatEvent.READY, self.on_ready)
        chat.register_event(ChatEvent.MESSAGE, self.read_message)
        chat.start()

        # Keep it alive
        while True:
            time.sleep(1)

    def gen_blurb(self, text: str, file_name: str):
        voice_id = random.choice(voices)
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        response = requests.post(url, json={"text": text}, headers={"xi-api-key": secrets.ELEVENLABS_API_KEY})

        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio.write(response.content)
                temp_audio_path = temp_audio.name

            pygame.mixer.music.load(temp_audio_path)
            pygame.mixer.music.play()
            time.sleep(30)
            os.remove(temp_audio_path)
        else:
            print("Error:", response.text)


if __name__ == '__main__':
    pygame.mixer.init()
    client = OpenAI(api_key=secrets.CHAT_GPT_API_KEY)
    jam_sesh = TwitchJamSesh()
    jam_sesh.begin()
