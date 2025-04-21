import speech_recognition as sr
import requests
# import spacy
# from spacy.matcher import Matcher
from crewai import Agent, Task, Crew
from crewai import LLM
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
import google.generativeai as genai
import os
import pyaudio
import wave
import keyboard
import threading

# # Load spaCy model
# nlp = spacy.load("en_core_web_sm")

# Gemini API setup
GEMINI_API_KEY = "AIzaSyAs7XK-GalTDMQY6vF3cUXuL73PhYbZRYk"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Constants
OPENWEATHER_API_KEY = "80573aba685d05ba2e542d101921b307"
TEMP_AUDIO_FILE = "temp_recording.wav"  # Temporary file for live recording

# Clothing dataset (truncated, add your full list)
clothing_data = [
    ("T-shirt", "Black", "Casual", "Everyday", "Nike", "clear", "tight"),
    ("Jeans", "Blue", "Denim", "Casual", "Levi's", "cloudy", "tight"),
    ("Suit", "Black", "Formal", "Business", "Armani", "cold", "tight"),
    ("Hoodie", "Gray", "Casual", "Winter", "Adidas", "cold", "loose"),
    ("Shorts", "Khaki", "Casual", "Summer", "Puma", "hot", "loose"),
    # Add the rest of your clothing_data here
]

# Weather mapping
weather_map = {
    "clear": "clear", "sunny": "clear", "partly cloudy": "cloudy", "cloudy": "cloudy",
    "overcast": "cloudy", "rain": "cold", "drizzle": "cold", "storm": "cold",
    "snow": "cold", "mist": "cold", "haze": "cloudy", "fog": "cold",
    "thunderstorm": "cold", "smoke": "cloudy", "hot": "hot", "cold": "cold",
    "humid": "hot", "windy": "cloudy"
}

# Audio Recording Function
def record_audio(output_file: str) -> None:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording... Press Enter to stop.")
    frames = []

    # Record until Enter is pressed
    def stop_recording():
        nonlocal recording
        keyboard.wait("enter")
        recording = False

    recording = True
    stop_thread = threading.Thread(target=stop_recording)
    stop_thread.start()

    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording stopped.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a WAV file
    wf = wave.open(output_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Audio to Text Function (modified to use recorded audio)
def audio_to_text(audio_file: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"Extracted Text: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return "Could not understand audio."
    except sr.RequestError:
        print("API unavailable.")
        return "API unavailable."

# # Tool Functions
# def extract_city_and_name(text: str) -> dict:
#     """Extracts the person's name and city from text."""
#     doc = nlp(text)
#     name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), None)
#     city = next((ent.text.capitalize() for ent in doc.ents if ent.label_ == "GPE"), None)
#     if not city:
#         matcher = Matcher(nlp.vocab)
#         pattern = [{"LOWER": "city"}, {"LOWER": "called"}, {"IS_ALPHA": True}]
#         matcher.add("CITY_PATTERN", [pattern])
#         matches = matcher(doc)
#         if matches:
#             city = doc[matches[0][1] + 2].text.capitalize()
#     return {"name": name, "city": city, "text": text}

def get_weather(city: str) -> dict:
    """Fetches weather and temperature for a given city."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_condition = data['weather'][0]['main'].lower()
        temperature = data['main']['temp']
        mapped_weather = weather_map.get(weather_condition, "cloudy")
        return {"weather": mapped_weather, "temperature": temperature}
    return {"weather": None, "temperature": None}

# def suggest_clothing(weather_temp: dict) -> str:
#     """Suggests clothing based on weather and temperature."""
#     weather, temp = weather_temp["weather"], weather_temp["temperature"]
#     if not weather:
#         return "Unable to suggest clothing due to missing weather data."
#     suggestions = [item[0] for item in clothing_data if item[5] == weather]
#     return ", ".join(suggestions) if suggestions else "No specific recommendation, wear something comfortable."

# def infer_gender_tool(name: str) -> str:
#     """Infers the gender based on the name."""
#     if not name:
#         return "neutral"
#     female_names = ["priya", "anita", "rekha", "sneha", "suchitra"]
#     male_names = ["ankur", "rahul", "vikram", "arjun"]
#     name_lower = name.lower()
#     if name_lower in female_names:
#         return "female"
#     elif name_lower in male_names:
#         return "male"
#     return "neutral"

# # Define Tools as Tool Instances
# extract_city_tool = Tool(
#     name="extract_city_and_name",
#     func=extract_city_and_name,
#     description="Extracts the person's name and city from text."
# )

weather_tool = Tool(
    name="get_weather",
    func=get_weather,
    description="Fetches weather and temperature for a given city."
)

# clothing_tool = Tool(
#     name="suggest_clothing",
#     func=suggest_clothing,
#     description="Suggests clothing based on weather and temperature."
# )

# gender_tool = Tool(
#     name="infer_gender",
#     func=infer_gender_tool,
#     description="Infers the gender based on the name."
# )

# Prompt Template
prompt_template = PromptTemplate(
    input_variables=["text"],
    template="""
    You are a friendly personal assistant. Based on the audio input "{text}", respond to <name> in a conversational way, considering their inferred gender (<gender>), the city (<city>), current weather (<weather>, <temp>°C), and clothing suggestions (<clothing>). If any data is missing, handle it gracefully.
    Use the input text to get data for all those variables enclosed in <>
    Example response for a male named Ankur:
    "Hey Ankur, great to hear from you! Looks like you're in Bangalore with <weather> weather at <temp>°C. For that, I'd suggest going with <clothing>. <compliment>"

    Now, craft your response:
    """
)

# Define the Personal Assistant Agent
os.environ["GEMINI_API_KEY"] = "AIzaSyAs7XK-GalTDMQY6vF3cUXuL73PhYbZRYk"

my_llm = LLM(
    model='gemini/gemini-1.5-flash',
    api_key=os.environ["GEMINI_API_KEY"]
)

personal_assistant = Agent(
    role="Personal Assistant",
    goal="Process the provided text to extract the user's name and city, infer the user's gender, fetch the current weather for that city, suggest appropriate clothing based on the weather, and then use the following template to craft a personalized response: \n\n" + prompt_template.template + "\n\nWhere <name>, <gender>, <city>, <weather>, <temp>, <clothing>, are present in {text}.",
    backstory="A highly efficient and friendly assistant designed to help users with personalized information and recommendations.",
    verbose=True,
    llm=my_llm,
    tools=[weather_tool]
)

# Define the Task
task = Task(
    description="Process the provided text {text}, extract the name and city, infer the gender, fetch the weather, suggest clothing, and provide a personalized response using the specified template.",
    agent=personal_assistant,
    expected_output="A friendly, personalized response string."
)

# Create the Crew
crew = Crew(
    agents=[personal_assistant],
    tasks=[task],
    verbose=True
)

# Run the Assistant with Live Recording
def run_assistant():
    # Record live audio
    record_audio(TEMP_AUDIO_FILE)
    
    # Convert audio to text
    text = audio_to_text(TEMP_AUDIO_FILE)
    if text in ["Could not understand audio.", "API unavailable."]:
        return text
    
    # Execute the crew with the text input
    result = crew.kickoff(inputs={"text": text})
    return result

# Execute
if __name__ == "__main__":
    print(run_assistant())