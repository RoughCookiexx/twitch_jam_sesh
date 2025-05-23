import asyncio
import os
import random
import tempfile
import threading
import time
from datetime import datetime

import pygame
import requests
from elevenlabs import ElevenLabs
from obswebsocket import obsws, requests as obs_requests
from openai import OpenAI
from twitchAPI.object.eventsub import (ChannelPointsCustomRewardRedemptionAddEvent)

import chatgpt
import secrets
from clipboard_queue import ClipboardQueue
from descriptors import generate_song_description
from mic_input import MicInput

import asyncio

from quart import Quart, request, jsonify

ALL_MESSAGES = ''
MINUTES_BETWEEN_SONGS = 20

elevenlabs = ElevenLabs(api_key=secrets.ELEVENLABS_API_KEY)

voices = ['iCVkdoGNYLTCRiLXC3Iu',
          'kbTLheY1CmCRIqLetJJL',
          'oQ2gVLvmfdFGixPqL5m2',
          'iHSDkze8smw4MQyIFKPZ',
          'Tn4bhLlhD26sndFn0Kgw',
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
        while True:
            try:
                self.ws = obsws(self.obs_host, self.obs_port, self.obs_password)
                self.ws.connect()
            except:
                time.sleep(10)
            finally:
                break

        self.user_id = None

        self.clipboard_queue = ClipboardQueue()

    async def begin(self):
        mic_input = MicInput(self.song_description)

        tasks = [
            # asyncio.create_task(mic_input.listen_for_keyword()),
            asyncio.create_task(self.listen_to_redemptions()),
            asyncio.create_task(self.clipboard_queue.monitor_paste()),
            asyncio.create_task(app.run_task(host='0.0.0.0', port=6973))
        ]
        await asyncio.gather(*tasks)

    async def read_message(self, message):

        if 'Cheer' in message:
            return

        # filtered_message = message.text  # Start with the full message

        # if message.emotes:
        #     # Sort the emotes by start_position to remove them in reverse order
        #     sorted_emotes = sorted(message.emotes.values(), key=lambda e: int(e[0]['start_position']), reverse=True)
        #
        #     # Loop through each emote in reverse order and remove it from the message
        #     for emote in sorted_emotes:
        #         start_pos = int(emote[0]['start_position']) - 1
        #         end_pos = int(emote[0]['end_position']) + 1
        #
        #         # Remove the emote from the message
        #         filtered_message = filtered_message[:start_pos] + filtered_message[end_pos:]

        print(message)
        self.song_description.append(message)

    async def on_channel_point_redemption(self, data: dict) -> None:
        event = data['event']['event']['reward']['title']
        if event == 'Request Song':
            await self.trigger_song_creation()

    async def trigger_song_creation(self):
        try:
            lyrics = chatgpt.send_message_to_chatgpt(
                f"Take the contents from below, and turn it into a short song. Create the lyrics for us in your own words."
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
                f"Don't ask for a specific song, just something that would prompt the DJ to choose this song."
                f" \n\n {lyrics}",
                client,
                1)

            print(lyrics)
            print(f'TITLE: {title}')
            print(f'DESCRIPTION: {tags}')

            lyrics = lyrics[:2000]

            self.clipboard_queue.queue_clipboard([lyrics, tags, title])

            # self.suno.generate_suno_song(lyrics, tags, title)
            self.ws.call(obs_requests.SetCurrentProgramScene(sceneName="Radio Station 2"))
            pygame.mixer.music.load("Office_phone_ringing.mp3")
            pygame.mixer.music.play()
            await asyncio.sleep(4)
            self.ws.call(obs_requests.SetCurrentProgramScene(sceneName="Radio Station"))
            await asyncio.sleep(6)
            await self.caller_blurb(blurb)


        except Exception as e:
            print(e)
            pass
        finally:
            self.song_description = []

    async def caller_blurb(self, message):
        filename = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.mp3'
        await self.gen_blurb(message, filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

    async def change_scene(self, scene_name):
        pygame.mixer.music.load("Office_phone_ringing.mp3")
        pygame.mixer.music.play()
        self.ws.call(obs_requests.SetCurrentProgramScene(sceneName=scene_name))
        await asyncio.sleep(2)
        pygame.mixer.music.play()

    async def on_eventsub_redemption(self, data: ChannelPointsCustomRewardRedemptionAddEvent):
        title = data.event.reward.title

        if title == 'Request Song':
            await self.trigger_song_creation()

    async def listen_to_redemptions(self):
        response = requests.post('http://127.0.0.1:6969/subscribe/event',
                                 json={"callback_url": 'http://127.0.0.1:6973/spin',
                                       "subscriptions": ['ChannelPointsCustomRewardRedemptionAddEvent']})

        if response.status_code == 201:
            print("good job!")
        else:
            print('bad job...')

        response = requests.post('http://127.0.0.1:6969/subscribe/chat',
                                 json={"callback_url": 'http://127.0.0.1:6973/mutter'})

        if response.status_code == 201:
            print("good job!")
        else:
            print('bad job...')

        # Keep it alive
        # print('Keeping Trombone alive...\n')
        # while True:
        #     await asyncio.sleep(0)

    async def gen_blurb(self, text: str, file_name: str):
        voice_id = random.choice(voices)
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        response = requests.post(url, json={"text": text}, headers={"xi-api-key": secrets.ELEVENLABS_API_KEY})

        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio.write(response.content)
                temp_audio_path = temp_audio.name

            pygame.mixer.music.load(temp_audio_path)
            pygame.mixer.music.play()
            await asyncio.sleep(30)
            os.remove(temp_audio_path)
        else:
            print("Error:", response.text)


app = Quart(__name__)


@app.route('/spin', methods=['POST'])
async def handle_events():
    data = await request.get_json()

    if not input:
        return jsonify({"error": "Missing user_name"}), 400

    asyncio.create_task(jam_sesh.on_channel_point_redemption(data))

    return 'success', 200


@app.route('/mutter', methods=['POST'])
async def listen_to_chat():
    data = await request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "Missing message"}), 400

    await jam_sesh.read_message(message)

    return 'success', 200


pygame.mixer.init()
client = OpenAI(api_key=secrets.CHAT_GPT_API_KEY)
jam_sesh = TwitchJamSesh()

if __name__ == '__main__':
    asyncio.run(jam_sesh.begin())
