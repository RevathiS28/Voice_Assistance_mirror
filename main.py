import os
import cv2
import mediapipe as mp
import numpy as np

# Paths
video_path = r"C:\Users\Admin\PycharmProjects\ShirtTryOns\Resources\Videos\ANKUR_1.mp4"
shirtFolderPath = r"C:\Users\Admin\PycharmProjects\ShirtTryOns\Resources\Shirts"

# Validation
if not os.path.exists(video_path):
    print(f"Error: The video file '{video_path}' does not exist.")
    exit()

if not os.path.exists(shirtFolderPath):
    print(f"Error: The folder '{shirtFolderPath}' does not exist.")
    exit()

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(video_path)

listShirts = os.listdir(shirtFolderPath)
if not listShirts:
    print("Error: No shirt images found in the folder.")
    exit()

print(f"Available shirts: {listShirts}")

# Load initial shirt
current_shirt_index = 0
shirt_path = os.path.join(shirtFolderPath, listShirts[current_shirt_index])
imgShirt = cv2.imread(shirt_path, cv2.IMREAD_UNCHANGED)
if imgShirt is None:
    print(f"Error: Could not load shirt image '{shirt_path}'.")
    exit()


def overlay_shirt(base_img, shirt_img, pos, scale_factor):
    """Overlay shirt with alpha blending"""
    # Calculate new dimensions
    new_width = int(shirt_img.shape[1] * scale_factor)
    new_height = int(shirt_img.shape[0] * scale_factor)

    # Resize shirt
    resized_shirt = cv2.resize(shirt_img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Adjust position to stay within bounds
    x, y = pos
    x = max(0, min(x, base_img.shape[1] - new_width))
    y = max(0, min(y, base_img.shape[0] - new_height))

    # Extract alpha channel if present
    if resized_shirt.shape[2] == 4:
        alpha = resized_shirt[:, :, 3] / 255.0
        shirt_colors = resized_shirt[:, :, :3]
    else:
        alpha = np.ones((new_height, new_width))
        shirt_colors = resized_shirt

    # Region of interest
    roi = base_img[y:y + new_height, x:x + new_width]

    # Blend images
    if roi.shape[:2] == shirt_colors.shape[:2]:  # Ensure dimensions match
        for c in range(3):
            roi[:, :, c] = (1.0 - alpha) * roi[:, :, c] + alpha * shirt_colors[:, :, c]
        base_img[y:y + new_height, x:x + new_width] = roi

    return base_img


while True:
    success, img = cap.read()
    if not success:
        print("Video ended or failed to read frame.")
        break

    # Convert to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)
    img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    if results.pose_landmarks:
        # Draw landmarks (optional)
        mp_drawing.draw_landmarks(
            img,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
        )

        # Get shoulder coordinates (11: left shoulder, 12: right shoulder)
        h, w = img.shape[:2]
        left_shoulder = results.pose_landmarks.landmark[11]
        right_shoulder = results.pose_landmarks.landmark[12]

        lm11 = [int(left_shoulder.x * w), int(left_shoulder.y * h)]  # [x, y]
        lm12 = [int(right_shoulder.x * w), int(right_shoulder.y * h)]  # [x, y]

        # Calculate metrics
        shoulder_width = abs(lm12[0] - lm11[0])
        center_x = (lm11[0] + lm12[0]) // 2
        center_y = (lm11[1] + lm12[1]) // 2

        if shoulder_width > 0:
            # Scale shirt based on shoulder width
            scale_factor = shoulder_width / imgShirt.shape[1] * 1.2
            shirt_width = int(imgShirt.shape[1] * scale_factor)

            # Position shirt (align top slightly above shoulders)
            pos_x = center_x - shirt_width // 2
            pos_y = min(lm11[1], lm12[1]) - int(shirt_width * 0.1)  # 10% of width offset

            # Overlay shirt
            img = overlay_shirt(img, imgShirt, [pos_x, pos_y], scale_factor)

        # Debug info
        cv2.putText(img, f"Left: {lm11}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(img, f"Right: {lm12}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.circle(img, (lm11[0], lm11[1]), 5, (0, 255, 0), -1)
        cv2.circle(img, (lm12[0], lm12[1]), 5, (0, 255, 0), -1)

    cv2.imshow("Image", img)

    key = cv2.waitKey(20) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('n'):
        current_shirt_index = (current_shirt_index + 1) % len(listShirts)
        shirt_path = os.path.join(shirtFolderPath, listShirts[current_shirt_index])
        imgShirt = cv2.imread(shirt_path, cv2.IMREAD_UNCHANGED)
        if imgShirt is None:
            print(f"Error: Could not load shirt image '{shirt_path}'. Skipping.")
            imgShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[0]), cv2.IMREAD_UNCHANGED)

cap.release()
cv2.destroyAllWindows()
pose.close()