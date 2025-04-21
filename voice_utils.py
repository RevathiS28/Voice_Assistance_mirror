import pyttsx3
import speech_recognition as sr

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set voice properties (optional)
engine.setProperty('rate', 160)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume 0.0 to 1.0

def speak(text):
    """Speak and also print the given text."""
    print(f"🗣️ {text}")
    engine.say(text)
    engine.runAndWait()

def listen_for_command(attempts=2):
    """Listen to user voice and return the text."""
    r = sr.Recognizer()

    for attempt in range(attempts):
        try:
            with sr.Microphone() as source:
                print("🎤 Adjusting for ambient noise...")
                r.adjust_for_ambient_noise(source)
                print("🎙️ Listening...")
                audio = r.listen(source, timeout=5)
                print("📡 Recognizing...")
                command = r.recognize_google(audio)
                print(f"✅ You said: {command}")
                return command.lower()
        except sr.WaitTimeoutError:
            print("⏱️ Timeout: No speech detected.")
        except sr.UnknownValueError:
            print("❌ Sorry, I couldn't understand that.")
        except sr.RequestError:
            print("🚫 Network error.")

        print(f"❗ Attempt {attempt + 1} failed. Trying again...")

    return ""
