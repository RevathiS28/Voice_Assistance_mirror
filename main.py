import random
import time
from voice_utils import speak, listen_for_command
from actions.outfit_suggestion import suggest_outfit_based_on_body_and_skin_tone

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
        speak("You have a lovely light skin tone..")
        time.sleep(1)
        speak("Soft pastels, cool blues, and pinks will look amazing on you!")
    elif "Medium" in skin_tone:
        speak("Your warm medium skin tone looks fantastic!")
        time.sleep(1)
        speak("Earthy tones like olive, mustard, and rust will complement you well.")
    elif "Dark" in skin_tone:
        speak("You have a beautiful dark skin tone.")
        time.sleep(1)
        speak("Bright colors like royal blue, yellow, and white will really stand out on you!")
    else:
        speak("Couldn't determine your exact skin tone, but you're always glowing!")


def suggest_outfits_based_on_body_type(body_type):
    speak(f"I've analyzed your body type. It looks like: {body_type}")
    time.sleep(1)

    if "Mesomorph" in body_type:
        speak("Since you have an athletic build, fitted clothing and structured jackets will enhance your silhouette.")
    elif "Endomorph" in body_type:
        speak("With your curvy build, high-waist pants and wrap dresses can look fabulous on you.")
    elif "Ectomorph" in body_type:
        speak("For your lean build, layered clothing and patterns can add volume and look great.")
    else:
        speak("Based on your structure, I suggest choosing well-fitted outfits that highlight your best features.")

def ask_about_body_detection():
    prompts = [
        "Are you ready to proceed with body structure detection?",
        "Shall we begin detecting your body structure now?",
        "Ready to start analyzing your body structure?",
        "Would you like to continue with body shape detection?"
    ]
    speak(random.choice(prompts))
    speak("Please respond with 'Yes, I am ready' or 'No, not now'.")

    attempts = 3
    while attempts > 0:
        user_reply = listen_for_command()

        if user_reply:
            user_reply = user_reply.lower()
            if "yes" in user_reply:
                speak(f"You said: '{user_reply}'. Let's proceed.")
                print("📸 Opening camera for body structure detection...")
                speak("Opening the camera. Please stand in front.")
                return True
            elif "no" in user_reply:
                speak("Okay, skipping for now.")
                return False
            else:
                speak(f"I heard: '{user_reply}'. Please say 'Yes' or 'No'.")
        else:
            speak("Sorry, I didn't hear you clearly.")
        attempts -= 1

    speak("No valid response received. Skipping body detection.")
    return False

def main():
    speak(get_greeting())
    speak("You can say something like 'Yes, I need your help' or 'No, I'm good.'")
    print("💬 Tip: Use a full sentence like 'Yes, I need your help'.")

    attempts = 3
    while attempts > 0:
        user_reply = listen_for_command()

        if user_reply:
            user_reply = user_reply.lower()
            if "yes" in user_reply or "need" in user_reply:
                speak("Great! Let's get started.")
                speak("Would you like real-time camera analysis now or do it later?")
                speak("Say 'Open the camera' or 'Later'.")

                option_response = listen_for_command()
                if option_response:
                    option_response = option_response.lower()

                    if "camera" in option_response:
                        try:
                            speak("Opening camera for real-time analysis...")
                            from actions.real_time_camera import start_real_time_analysis
                            skin_tone = start_real_time_analysis()

                            if skin_tone:
                                respond_to_skin_tone(skin_tone)

                                if ask_about_body_detection():
                                    try:
                                        from actions.body_structure_analysis import start_body_structure_detection
                                        speak("Analyzing body structure...")
                                        body_type = start_body_structure_detection()

                                        if body_type:
                                            suggest_outfits_based_on_body_type(body_type)
                                            speak("Would you like to choose an outfit now?")
                                            speak("Say 'Yes' to continue or 'No' to skip.")

                                            outfit_response = listen_for_command()
                                            if outfit_response and "yes" in outfit_response.lower():
                                                speak("Opening camera for outfit selection...")
                                                suggestion = suggest_outfit_based_on_body_and_skin_tone(body_type, skin_tone)
                                                if suggestion:
                                                    speak(suggestion)
                                                else:
                                                    speak("I couldn't suggest an outfit right now..")
                                            else:
                                                speak("No problem. You can try later.")
                                        else:
                                            speak("Body structure detection failed.")
                                    except Exception as e:
                                        speak("There was a problem with body structure detection.")
                                        print(e)
                            else:
                                speak("Skin tone detection failed.")
                        except Exception as e:
                            speak("There was an error analyzing your skin tone.")
                            print(e)

                    elif "later" in option_response:
                        speak("Okay! Let me know when you're ready.")
                    else:
                        speak("Sorry, I didn't get that.")
                else:
                    speak("No response received. Try again later.")
                break

            elif "no" in user_reply:
                speak("Okay! Let me know if you need help later.")
                break
            else:
                speak("Please say 'Yes' or 'No'.")
        else:
            speak("Didn't catch that. Please speak clearly.")
        attempts -= 1

    if attempts == 0:
        speak("Still no response. Try again later.")

if __name__ == "__main__":
    main()
