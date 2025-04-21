import cv2
import mediapipe as mp
import time
import math

# Calculate the Euclidean distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

# Classify body type based on shoulder, hip, and waist measurements
def classify_body_type(landmarks):
    # Get shoulder, hip, and waist landmarks
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    left_waist = landmarks[25]  # Refined waist landmark
    right_waist = landmarks[26]

    # Calculate shoulder, hip, and waist widths
    shoulder_width = calculate_distance(left_shoulder, right_shoulder)
    hip_width = calculate_distance(left_hip, right_hip)
    waist_width = calculate_distance(left_waist, right_waist)

    # Print measurements for debugging
    print(f"📏 Shoulder: {shoulder_width:.3f}, Hip: {hip_width:.3f}, Waist: {waist_width:.3f}")

    # Classify body type based on measurements
    if shoulder_width > hip_width + 0.05 and waist_width < shoulder_width - 0.05:
        body_type = "🏖 Inverted Triangle"
        recommendation = "Soft, draped fabrics and A-line silhouettes can soften broad shoulders. Try peplum tops, flared skirts, or wide-leg pants for balance."
    elif hip_width > shoulder_width + 0.05 and waist_width < hip_width - 0.05:
        body_type = "🍐 Pear Shape"
        recommendation = "Flaunt your curves with tops that add volume to your upper body like boat necks or puffed sleeves. Go for straight-leg pants to create balance."
    elif abs(shoulder_width - hip_width) < 0.03 and waist_width < shoulder_width - 0.05:
        body_type = "🕰 Hourglass"
        recommendation = "Emphasize your curves with bodycon dresses, pencil skirts, or wrap dresses that cinch the waist."
    elif abs(shoulder_width - hip_width) < 0.03 and abs(waist_width - shoulder_width) < 0.03:
        body_type = "📏 Rectangle"
        recommendation = "Create curves with layered looks, ruffles, peplum tops, and flared trousers."
    elif waist_width >= shoulder_width and waist_width >= hip_width:
        body_type = "🍎 Apple"
        recommendation = "Use V-neck tops, empire waist dresses, and tunics. Choose high-waisted pants to elongate legs and balance your silhouette."
    else:
        body_type = "🧍 Ectomorph (Lean)"
        recommendation = "Add layers and textures like denim or chunky sweaters to add dimension. Fitted jackets work well too."

    return body_type, recommendation

# Start body structure detection and classification
def start_body_structure_detection():
    # Initialize Mediapipe and OpenCV
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Unable to access the camera.")
        return None, None
    else:
        print("✅ Camera accessed successfully.")

    print("🗣️ 📸 I’m opening the camera to analyze your body structure...")
    time.sleep(2)
    print("🗣️ Please stand in front of the camera.")

    body_detected = False
    detection_start_time = time.time()
    max_wait_time = 15
    max_duration = 30

    final_body_type = None
    final_recommendation = None

    # Use Mediapipe Pose for body structure detection
    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to grab frame.")
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                # Draw landmarks on the image
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                landmarks = results.pose_landmarks.landmark

                # Check if required landmarks are visible
                required_landmarks = [11, 12, 23, 24, 25, 26]
                if all(landmarks[i].visibility > 0.7 for i in required_landmarks):
                    body_type, recommendation = classify_body_type(landmarks)

                    # Display body type and recommendations on screen
                    cv2.putText(image, "✅ Body detected", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    print(f"✅ Body Type: {body_type}")
                    print(f"💡 Suggestion: {recommendation}")
                    cv2.putText(image, f"{body_type}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

                    final_body_type = body_type
                    final_recommendation = recommendation
                    body_detected = True

                    # Show the image with body structure
                    cv2.imshow("Body Structure Detection", image)
                    time.sleep(1.5)
                    break
                else:
                    # If body alignment is not good, ask the user to adjust position
                    cv2.putText(image, "📸 Please align your body properly...", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(image, "📸 Waiting for full body visibility...", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Show the image window
            cv2.imshow("Body Structure Detection", image)

            # Check if the user is taking too long to align properly
            if time.time() - detection_start_time > max_wait_time:
                if not body_detected:
                    print("❌ Full body not detected. Please adjust your position.")
                    detection_start_time = time.time()
                    cv2.putText(image, "🗣️ Please adjust your position and try again.", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Timeout after a certain period if the body is not detected
            if time.time() - detection_start_time > max_duration:
                print("⏰ Timed out waiting for body detection.")
                break

            # Allow user to exit with the 'q' key
            if cv2.waitKey(5) & 0xFF == ord('q'):
                print("🛑 Interrupted by user.")
                break

    # Release camera and destroy windows
    cap.release()
    cv2.destroyAllWindows()

    # Return the detected body type and recommendation
    if final_body_type and final_recommendation:
        return final_body_type, final_recommendation
    else:
        return None, None

# Main function to trigger the body structure detection and classification
def main():
    body_type, recommendation = start_body_structure_detection()

    if body_type and recommendation:
        print(f"✅ Detected Body Type: {body_type}")
        print(f"💡 Recommendation: {recommendation}")
        # Use this output in your mirror’s interface or speech module.
    else:
        print("❌ Unable to detect body or provide recommendations.")

if __name__ == "__main__":
    main()
