import time
import requests

# replace your vercel domain
base_url = 'http://localhost:3000'


def custom_generate_audio(payload):
    url = f"{base_url}/api/custom_generate"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()


def extend_audio(payload):
    url = f"{base_url}/api/extend_audio"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()

def generate_audio_by_prompt(payload):
    url = f"{base_url}/api/generate"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()


def get_audio_information(audio_ids):
    url = f"{base_url}/api/get?ids={audio_ids}"
    response = requests.get(url)
    return response.json()


def get_quota_information():
    url = f"{base_url}/api/get_limit"
    response = requests.get(url)
    return response.json()

def get_clip(clip_id):
    url = f"{base_url}/api/clip?id={clip_id}"
    response = requests.get(url)
    return response.json()

def generate_whole_song(clip_id):
    payload = {"clip_id": clip_id}
    url = f"{base_url}/api/concat"
    response = requests.post(url, json=payload)
    return response.json()

# def create_persona(clip_id, name):
#     url = f"{base_url}/api/persona/create"
#     payload = {"user_id": "2e49ef16-b484-43a9-8714-9c91db70d212",
#                "root_clip_id": clip_id,
#                "name": name,
#                "description": "none",
#                "clips": [clip_id],
#                "is_public": False
#                }
#     response = requests.post(url, json=payload)
    return response.json()


    # "user_id": "2e49ef16-b484-43a9-8714-9c91db70d212",
    # "root_clip_id": "2ca4ed86-adb0-4ce7-bfb3-07320f94f09e",
    # "name": "song naaame",
    # "description": "sooound ",
    # "image_s3_id": "data:image/png;base64,
    # "clips": [
    #     "2ca4ed86-adb0-4ce7-bfb3-07320f94f09e"
    # ],
    # "is_public": true


if __name__ == '__main__':
    pass
    # response = create_persona('0b568a82-70e9-4cac-83f7-d434aaa6809b', 'test band')
    # print(response)

    # data = generate_audio_by_prompt({
    #     "prompt": "A love song about using the potty",
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
