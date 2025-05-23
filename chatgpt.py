import openai
from openai import OpenAI

from secrets import CHAT_GPT_API_KEY


def send_message_to_chatgpt(message, client, temperature=0.8):

    messages = []
    messages.append(
        {"role": "user", "content": message}
    )

    response = client.chat.completions.create(model='gpt-4.1-mini-2025-04-14',
                                        messages=messages,
                                        max_tokens=500,
                                        temperature=temperature)

    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    client = OpenAI(api_key=CHAT_GPT_API_KEY)
    user_message = input("Enter your message for ChatGPT: ")
    reply = send_message_to_chatgpt(user_message, client)
    print("ChatGPT's reply:", reply)
