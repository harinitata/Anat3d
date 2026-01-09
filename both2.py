import cv2
import mediapipe as mp
import pyautogui
import math
import time
from collections import deque

import pygetwindow as gw


def setup_layout():
    print("Adjusting window layout...")
    # Give the windows a second to actually appear
    time.sleep(2) 
    
    try:
        # 1. Position Blender (Left Side - 70% of screen)
        # Blender's window title usually starts with 'Blender'
        blender_wins = [w for w in gw.getAllWindows() if 'Blender' in w.title]
        if blender_wins:
            blender_win = blender_wins[0]
            blender_win.moveTo(0, 0)
            blender_win.resizeTo(1344, 1080) # Adjust based on your resolution
            print("Blender positioned.")

        # 2. Position the Camera (Right Side - 30% of screen)
        # Use the exact name you gave in cv2.imshow()
        camera_wins = gw.getWindowsWithTitle('ANAT3D - Visualized Controller')
        if camera_wins:
            camera_win = camera_wins[0]
            camera_win.moveTo(1344, 0)
            camera_win.resizeTo(576, 1080)
            camera_win.activate() # Make camera active so gestures work
            print("Camera window positioned.")
            
    except Exception as e:
        print(f"Layout Error: {e}")

# Call this function right before your while loop starts
setup_layout()
# =========================
# MediaPipe Setup - MAXIMUM PERFORMANCE
# =========================
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=0
)

# =========================
# Camera Setup - REDUCED RESOLUTION
# =========================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Reduced from 640
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Reduced from 480
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# =========================
# Frame Processing - AGGRESSIVE SKIP
# =========================
PROCESS_EVERY_N_FRAMES = 3  # Process every 3rd frame
frame_count = 0
last_hand_landmarks = None
hand_detected = False  # Track if hand is currently detected
frames_without_hand = 0  # Counter for frames without detection
MAX_FRAMES_WITHOUT_HAND = 5  # Clear after N frames without detection

# Smoothing buffer
gesture_buffer = deque(maxlen=3)

# =========================
# Gesture Parameters
# =========================
rotation_deadzone = 20
rotation_interval = 0.1
last_rotation_time = 0

zoom_threshold = 70
zoom_interval = 0.15
last_zoom_time = 0

# =========================
# Display optimization
# =========================
SHOW_LANDMARKS = False  # Disable drawing for speed
SHOW_VIDEO = True  # Set to False for max speed

fps = 0
prev_frame_time = time.time()

print("ULTRA-FAST Gesture Controller")
print("- Horizontal -> Rotate")
print("- Vertical -> Zoom")
print("- ESC to quit")

def get_gesture(dx, dy, distance, threshold=70):
    """Determine gesture type"""
    if abs(dx) > abs(dy):
        if abs(dx) > rotation_deadzone:
            return "ROTATE_RIGHT" if dx > 0 else "ROTATE_LEFT"
        return "HOLD"
    else:
        return "ZOOM_IN" if distance > threshold else "ZOOM_OUT"

# =========================
# Main Loop - OPTIMIZED
# =========================
while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    now = time.time()
    frame_count += 1

    # Only process MediaPipe every N frames
    if frame_count % PROCESS_EVERY_N_FRAMES == 0:
        # Resize for even faster processing
        small = cv2.resize(image, (160, 120))
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = hands.process(rgb)
        
        if results.multi_hand_landmarks:
            last_hand_landmarks = results.multi_hand_landmarks[0]
            hand_detected = True
            frames_without_hand = 0  # Reset counter
        else:
            frames_without_hand += 1
            # Clear hand data after several frames without detection
            if frames_without_hand > MAX_FRAMES_WITHOUT_HAND:
                last_hand_landmarks = None
                hand_detected = False
                gesture_buffer.clear()

    # Execute gestures ONLY if hand is detected
    if hand_detected and last_hand_landmarks is not None:
        # Get coordinates (scaled back to original size)
        scale_x = 320 / 160
        scale_y = 240 / 120
        
        thumb = last_hand_landmarks.landmark[4]
        index = last_hand_landmarks.landmark[8]

        thumb_x = thumb.x * 320 * scale_x
        thumb_y = thumb.y * 240 * scale_y
        index_x = index.x * 320 * scale_x
        index_y = index.y * 240 * scale_y

        dx = thumb_x - index_x
        dy = thumb_y - index_y
        distance = math.hypot(dx, dy)

        # Get gesture
        gesture = get_gesture(dx, dy, distance)
        gesture_buffer.append(gesture)

        # Execute only if gesture is stable
        if len(gesture_buffer) == 3 and len(set(gesture_buffer)) == 1:
            stable_gesture = gesture_buffer[0]

            if stable_gesture == "ROTATE_RIGHT":
                if now - last_rotation_time > rotation_interval:
                    pyautogui.press("right")
                    last_rotation_time = now

            elif stable_gesture == "ROTATE_LEFT":
                if now - last_rotation_time > rotation_interval:
                    pyautogui.press("left")
                    last_rotation_time = now

            elif stable_gesture == "ZOOM_IN":
                if now - last_zoom_time > zoom_interval:
                    pyautogui.hotkey("ctrl", "+")
                    last_zoom_time = now

            elif stable_gesture == "ZOOM_OUT":
                if now - last_zoom_time > zoom_interval:
                    pyautogui.hotkey("ctrl", "-")
                    last_zoom_time = now

    # Optional display (disable for max performance)
    if SHOW_VIDEO:
        if frame_count % 2 == 0:  # Update display every 2 frames
            fps = 1 / (now - prev_frame_time) if (now - prev_frame_time) > 0 else 0
            prev_frame_time = now

            image = cv2.flip(image, 1)
            status = gesture_buffer[-1] if gesture_buffer else "NEUTRAL"
            
            # Show hand detection status
            detection_status = "HAND DETECTED" if hand_detected else "NO HAND"
            color = (0, 255, 0) if hand_detected else (0, 0, 255)
            
            # Minimal UI
            cv2.putText(image, f"{status} | FPS:{fps:.0f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(image, detection_status, (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            cv2.imshow("Controller", image)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
hands.close()
print("Controller closed")