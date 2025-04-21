import cv2
import numpy as np
from mtcnn import MTCNN
from sklearn.cluster import KMeans
from collections import Counter

def detect_skin_tone(face_img):
    """Detect the skin tone using KMeans clustering and return valid skin tones only."""
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    pixels = face_img.reshape((-1, 3))  # Flatten the image
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    kmeans.fit(pixels)
    dominant_color = kmeans.cluster_centers_[kmeans.labels_[0]].astype(int)
    
    r, g, b = dominant_color
    if r > 200 and g > 180 and b > 160:
        return "Light"
    elif 130 < r < 200 and 100 < g < 180:
        return "Medium"
    elif r < 130 and g < 110 and b < 100:
        return "Dark"
    else:
        return None  # Instead of "Unknown", return None for invalid skin tones

def start_real_time_analysis(max_frames=40):
    """Open camera and detect skin tone for up to max_frames times."""
    detector = MTCNN()
    cap = cv2.VideoCapture(0)
    skin_tone_detections = []
    frame_count = 0

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture frame.")
            break

        result = detector.detect_faces(frame)
        if result:
            for detection in result:
                x, y, w, h = map(abs, detection['box'])  # Bounding box
                face_img = frame[y:y+h, x:x+w]  # Crop the face

                if face_img.size > 0:
                    # Get skin tone of the detected face
                    skin_tone = detect_skin_tone(face_img)
                    if skin_tone:  # Only add valid skin tones
                        print(f"Detected: {skin_tone} skin tone")
                        skin_tone_detections.append(skin_tone)

                    # Draw rectangle around face and label it with skin tone
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, skin_tone if skin_tone else "Unknown", 
                                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Display the frame with face detection and skin tone analysis
        cv2.imshow("Real-Time Skin Tone Detection (Press 'q' to stop)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 User exited manually.")
            break

        frame_count += 1

    # Stop camera and close window
    cap.release()
    cv2.destroyAllWindows()

    # Return the most frequent skin tone detected, if any
    if not skin_tone_detections:
        return None  # If no valid skin tone detected, return None

    most_common = Counter(skin_tone_detections).most_common(1)[0][0]
    return most_common

def respond_to_skin_tone(skin_tone):
    """AI response based on detected skin tone."""
    if skin_tone == "Light":
        print("AI: You have a lovely light skin tone.")
        print("AI: Soft pastels, cool blues, and pinks will look amazing on you!")
    elif skin_tone == "Medium":
        print("AI: Your warm medium skin tone looks fantastic!")
        print("AI: Earthy tones like olive, mustard, and rust will complement you well.")
    elif skin_tone == "Dark":
        print("AI: You have a beautiful dark skin tone.")
        print("AI: Bright colors like royal blue, yellow, and white will really stand out on you!")
    else:
        print("AI: Couldn't determine your exact skin tone, but you're always glowing!")

# Start the real-time analysis and respond based on skin tone
def main():
    skin_tone = start_real_time_analysis(max_frames=40)
    if skin_tone:
        print(f"AI: The most frequent detected skin tone is: {skin_tone}")
        respond_to_skin_tone(skin_tone)
    else:
        print("AI: No valid skin tone detected.")

if __name__ == "__main__":
    main()
