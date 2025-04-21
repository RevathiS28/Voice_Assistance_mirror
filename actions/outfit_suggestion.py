import logging
import cv2
import mediapipe as mp
import time
import math
from voice_utils import speak, listen_for_command

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Calculate distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

# Classify body type based on landmarks
def classify_body_type(landmarks):
    logging.info("Classifying body type based on landmarks...")
    
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]

    shoulder_width = calculate_distance(left_shoulder, right_shoulder)
    hip_width = calculate_distance(left_hip, right_hip)
    waist_width = (shoulder_width + hip_width) / 2 * 0.85  # Estimate waist

    shoulder_hip_diff = abs(shoulder_width - hip_width)

    if shoulder_width > hip_width + 0.05:
        body_type = "🏖 Inverted Triangle"
    elif hip_width > shoulder_width + 0.05:
        body_type = "🍐 Pear Shape"
    elif abs(shoulder_width - hip_width) < 0.03 and waist_width < shoulder_width - 0.05:
        body_type = "🕰 Hourglass"
    elif shoulder_hip_diff < 0.03:
        body_type = "📏 Rectangle"
    elif waist_width >= shoulder_width and hip_width < waist_width:
        body_type = "🍎 Apple"
    else:
        body_type = "🧍 Ectomorph (Lean)"
    
    logging.info(f"Detected body type: {body_type}")
    return body_type

# Suggest outfits based on body type
def suggest_outfit_based_on_body_type(body_type):
    logging.info(f"Suggesting outfit for body type: {body_type}")
    
    suggestions = {
        "🏖 Inverted Triangle": "Wide-leg pants, palazzos, or A-line skirts to balance your frame.",
        "🍐 Pear Shape": "Boat neck tops, statement shoulders, and A-line dresses.",
        "🕰 Hourglass": "Wrap dresses, high-waist pants, and belts will flatter your curves.",
        "📏 Rectangle": "Add volume with layers, ruffles, or peplum tops.",
        "🍎 Apple": "Empire waist tops and v-necklines for a slimming effect.",
        "🧍 Ectomorph (Lean)": "Add volume with textured fabrics, patterns, and layers."
    }
    
    suggestion = suggestions.get(body_type, "No suggestions available.")
    logging.info(f"Outfit suggestion: {suggestion}")
    return suggestion

# Real-time outfit analysis using camera
def analyze_outfit_with_camera(body_type, skin_tone):
    logging.info("Starting real-time outfit analysis with camera...")
    
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logging.error("❌ Unable to access the camera.")
        speak("❌ Unable to access the camera.")
        return

    speak("📸 Please hold your outfit in front of the camera.")
    time.sleep(2)

    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                logging.error("❌ Failed to grab frame.")
                speak("❌ Failed to grab frame.")
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Simple example check (can be extended with ML logic later)
                if body_type == "🕰 Hourglass" and skin_tone == "light":
                    cv2.putText(image, "✅ This outfit suits your body type!", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    logging.info("✅ This outfit suits your body type.")
                else:
                    cv2.putText(image, "❌ This may not suit your body type.", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    logging.warning("❌ This outfit may not suit your body type.")

            cv2.imshow("Outfit Analysis", image)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                logging.info("User pressed 'q' to quit.")
                break

    cap.release()
    cv2.destroyAllWindows()

# Main function to guide the user
def suggest_outfit_based_on_body_and_skin_tone(body_type, skin_tone):
    logging.info(f"User's body type: {body_type}, Skin tone: {skin_tone}")
    
    speak(f"📊 Based on analysis, your body type is: {body_type}")
    suggestion = suggest_outfit_based_on_body_type(body_type)
    speak(f"🧥 Outfit Suggestion: {suggestion}")

    speak("Would you like to select an outfit based on this suggestion?")
    speak(" If you'd like to try this suggestion, say something like 'Yes, I would', 'Open the camera', or 'Let's try'.")
    speak(" If you don't want to, say 'No', 'No need', or 'Maybe later'.")

    response = listen_for_command()

    if response:
        lower_response = response.lower()

        # Positive and Negative keywords to match user intent
        positive_keywords = ["yes", "i would", "open", "camera", "go ahead", "try outfit", "let's try"]
        negative_keywords = ["no", "no need", "skip", "not now", "maybe later"]

        # Check for positive intent
        if any(keyword in lower_response for keyword in positive_keywords):
            speak("📸 Great! Opening the camera now. Please hold your outfit in front of it.")
            analyze_outfit_with_camera(body_type, skin_tone)
            logging.info("✅ Camera opened and outfit analyzed.")
            return "✅ Camera opened and outfit analyzed."

        # Check for negative intent
        elif any(keyword in lower_response for keyword in negative_keywords):
            speak("🛑 Alright! Skipping outfit selection for now.")
            logging.info("🛑 Skipped outfit selection.")
            return "🛑 Skipped outfit selection."

        else:
            speak(f"⚠️ I heard: '{response}', but wasn't sure what you meant.")
            speak("Please say 'Yes, I would' to open the camera or 'No, no need' to skip.")
            logging.warning(f"⚠️ Unclear response: '{response}'")
            return "❓ Unclear response."

    else:
        speak("I didn’t catch your response. Skipping outfit selection for now.")
        logging.warning("No response received. Skipping outfit selection.")
        return "🛑 Skipped outfit selection due to no response." 