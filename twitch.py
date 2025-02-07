import threading
import time
from datetime import datetime

from openai import OpenAI
from twitchAPI.object.eventsub import ChatMessage
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData

import asyncio
import pygame
import yt_dlp

import chatgpt
import secrets
from main import get_audio_information, custom_generate_audio
from mic_input import MicInput
from suno_doodad import SunoDoodad

ALL_MESSAGES = ''


class TwitchJamSesh:

    def __init__(self):
        self.song_description = []
        self.suno = SunoDoodad()
        self.spoken_text = []

    def begin(self):
        mic_input = MicInput(self.spoken_text)

        threads = [
            threading.Thread(target=mic_input.listen_for_keyword),
            threading.Thread(target=self.twitch_listener_thread)
        ]
        # Start all the threads
        for thread in threads:
            thread.start()

        # Join threads to wait for them to finish
        for thread in threads:
            thread.join()

    async def read_message(self, message: ChatMessage):
        if 'Cheer' not in message.text:
            self.song_description.append(message.text)

        print(self.song_description)

        MESSAGE_THRESHOLD = 25

        with open('message_count_down', "w") as file:
            file.write(f'NEXT SONG: {len(self.song_description)} / {MESSAGE_THRESHOLD}')

        if len(self.song_description) >= MESSAGE_THRESHOLD:
            print(f"  {','.join(self.spoken_text)}")
            my_summary = chatgpt.send_message_to_chatgpt(
                "Re-word these words I recorded. Condense it down to a short paragraph.\n"
                "\n{}".format("\n".join(self.spoken_text)),
                client
            )
            print(my_summary)

            self.song_description.append(my_summary)

            reply = chatgpt.send_message_to_chatgpt(
                f"Take the contents from below, and turn it into a short song. Generate the lyrics for us."
                f"Keep the lyrics between 750 and 1,250 characters. "
                f"Annotate sections of the song like this: [INTRO], [VERSE 1], etc. etc. "
                f"Only return the lyrics, no introduction. no conclusion. "
                f"Use your own words aside from "
                f"no 'here is your summary bullshit'. "
                f"just get to the point.\n"
                f"  {','.join(self.song_description)}",
                client)

            tags = chatgpt.send_message_to_chatgpt(
                f"Decide the style of music the following song should be written in. Use 10 words or less. Just reply with descriptors: {reply}", client)
            title = chatgpt.send_message_to_chatgpt(
                f"Take the following content and reply with only a title for a song:{reply}", client)

            print(title)
            print(tags)
            print(reply)

            reply = reply[:2000]

            self.suno.generate_suno_song(reply, tags, title)

            # data = custom_generate_audio({
            #     "prompt": reply,
            #     "tags": tags,
            #     "title": title,
            #     "make_instrumental": False,
            #     "wait_audio": False
            # })
            #
            # ids = f"{data[0]['id']},{data[1]['id']}"
            # print(f"ids: {ids}")
            #
            # for _ in range(60):
            #     data = get_audio_information(ids)
            #     if data[0]["status"] == 'streaming':
            #         print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            #         print(f"{data[1]['id']} ==> {data[1]['audio_url']}")
            #         break
            #     # sleep 5s
            #     time.sleep(5)
            #
            # time.sleep(15)
            #
            # await self.play_audio_stream(data[0]['audio_url'], data[0]['lyric'], data[0]['title'])

            self.spoken_text = []
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
