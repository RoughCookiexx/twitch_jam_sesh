import speech_recognition as sr

class MicInput:

    def __init__(self, spoken_text):
        self.recognizer = sr.Recognizer()
        self.spoken_text = spoken_text

    def listen_for_keyword(self):
        # Use the microphone as the audio source
        with sr.Microphone() as source:
            print("Listening...")

            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    spoken_text = self.recognizer.recognize_google(audio).lower()
                    print(spoken_text)
                    self.spoken_text.append(spoken_text)

                except sr.WaitTimeoutError:
                    print(".", end='')
                    # recognized_label.config(text="Listening timeout, still listening...")
                except sr.UnknownValueError:
                    print("x", end='')
                    # recognized_label.config(text="Couldn't understand, try again...")
                except sr.RequestError as e:
                    print(f"Error with the API: {e}")
                    # recognized_label.config(text="API error")
                    break
                except Exception as e:
                    print(e)
