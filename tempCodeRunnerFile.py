import random
from voice_utils import speak, listen_for_command

def get_greeting():
    greetings = [
        "Hey! Would you like some help getting ready?",
        "Hello! Need some assistance getting ready?",
        "Hi there! How can I assist you with your preparations today?",
        "Good day! Would you like help with getting ready?"
    ]
    return random.choice(greetings)

def respond_to_skin_tone(skin_tone):
    if "Light" in skin_tone:
        speak("You have a lovely light skin tone.")
        speak("Soft pastels, cool blues, and pinks will look amazing on you!")
    elif "Medium" in skin_tone:
        speak("Your warm medium skin tone looks fantastic!")
        speak("Earthy tones like olive, mustard, and rust will complement you well.")
    elif "Dark" in skin_tone:
        speak("You have a beautiful dark skin tone.")
        speak("Bright colors like royal blue, yellow, and white will really stand out on you!")
    else:
        speak("Couldn't determine your exact skin tone, but you're always glowing!")

def ask_about_body_detection():
    body_detection_prompts = [
        "Are you ready to proceed with body structure detection?",
        "Shall we begin detecting your body structure now?",
        "Ready to start analyzing your body structure?",
        "Would you like to continue with body shape detection?"
    ]
    speak(random.choice(body_detection_prompts))
    speak("Please respond with 'Yes, I am ready' if you want to proceed, or say 'No, not now' if you'd prefer to skip this step.")

    attempts = 3
    while attempts > 0:
        user_reply = listen_for_command()

        if user_reply:
            if "yes" in user_reply.lower():
                speak(f"Yes, you said: '{user_reply}'. Let's proceed with body structure detection.")
                speak("📸 I’m opening the camera to analyze your body structure...")
                speak("Please stand in front of the camera.")
                return True
            elif "no" in user_reply.lower():
                speak(f"No, you said: '{user_reply}'. We'll skip this for now.")
                return False
            else:
                speak(f"I didn't quite catch that. You said: '{user_reply}'. Please respond with 'Yes, I am ready' or 'No, not now'.")
                attempts -= 1
        else:
            speak("Sorry, I didn't hear you. Please respond with 'Yes, I am ready' or 'No, not now'.")
            attempts -= 1

    speak("❌ No valid response received. Skipping body structure detection for now.")
    return False

def main():
    greeting = get_greeting()
    speak(greeting)
    speak("You can say something like 'Yes, I need your help' or 'No, I'm good.'")
    print("💬 Tip: Use a full sentence, not just 'yes' or 'no'.")

    attempts = 3
    user_reply = ""

    while attempts > 0:
        user_reply = listen_for_command()

        if user_reply:
            if "yes" in user_reply.lower() or "need" in user_reply.lower():
                speak(f"Yes, you said: '{user_reply}'. Let's continue!")
                speak("Would you like me to open the camera for real-time analysis, or would you prefer to import your image and outfit collection?")
                speak("You can say 'Open the camera', 'Import images', or say 'Later' if you'd like to do it later.")

                option_response = listen_for_command()

                if "camera" in option_response.lower():
                    speak("Opening camera for real-time analysis...")
                    from actions.real_time_camera import start_real_time_analysis
                    skin_tone = start_real_time_analysis()  # 👈️ this should now return the skin tone
                    respond_to_skin_tone(skin_tone)

                    # Ask about body structure detection after skin tone response
                    body_detection_response = ask_about_body_detection()
                    if body_detection_response:
                        from actions.body_structure_analysis import start_body_structure_detection
                        start_body_structure_detection()  # Proceed with body structure detection

                elif "import" in option_response.lower():
                    speak("Let me help you import your images and analyze your outfits.")
                    from actions.import_images import start_import_and_analysis
                    start_import_and_analysis()

                elif "later" in option_response.lower():
                    speak("No problem! Let me know when you're ready to proceed.")

                else:
                    speak("Sorry, I didn't catch that. Please say 'Open the camera', 'Import images', or 'Later'.")
                break

            elif "no" in user_reply.lower():
                speak("No, thanks. Let me know if you change your mind!")
                break

            else:
                speak("I didn't understand that. Please say 'Yes' if you need help or 'No' if you're all set.")
                attempts -= 1
                if attempts > 0:
                    speak(f"Please try again. You have {attempts} attempts left.")
                else:
                    speak("Sorry, I still didn't catch that. Please try again later.")
        else:
            speak("Sorry, I couldn't hear anything. Please try speaking again.")
            attempts -= 1
            if attempts > 0:
                speak(f"You have {attempts} attempts left.")
            else:
                speak("Sorry, I couldn't hear you. Please try again later.")
                break

if __name__ == "__main__":
    main()
