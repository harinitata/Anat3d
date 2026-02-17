import cv2
import mediapipe as mp
import pyautogui
import math
import time
from collections import deque
import pygetwindow as gw

# =========================
# Window Layout (UNCHANGED)
# =========================
def setup_layout():
    print("Adjusting window layout...")
    time.sleep(2) 
    try:
        blender_wins = [w for w in gw.getAllWindows() if 'Blender' in w.title]
        if blender_wins:
            blender_win = blender_wins[0]
            blender_win.moveTo(0, 0)
            blender_win.resizeTo(1344, 1080)
        
        camera_wins = gw.getWindowsWithTitle('ANAT3D - Controller')
        if camera_wins:
            camera_win = camera_wins[0]
            camera_win.moveTo(1344, 0)
            camera_win.resizeTo(576, 1080)
            camera_win.activate()
    except Exception as e:
        print(f"Layout Error: {e}")

setup_layout()

# =========================
# MediaPipe Setup
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
# Camera Setup
# =========================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 30)

# =========================
# Control Variables
# =========================
PROCESS_EVERY_N_FRAMES = 3
frame_count = 0
last_hand_landmarks = None
hand_detected = False
frames_without_hand = 0
MAX_FRAMES_WITHOUT_HAND = 5

gesture_buffer = deque(maxlen=3)

# Timing for actions
last_rotation_time = 0
last_zoom_time = 0
last_mode_time = 0  # Cooldown for Palm/Fist
MODE_COOLDOWN = 1.5 # Seconds between mode swaps

# =========================
# Gesture Logic
# =========================
def get_gesture(dx, dy, distance):
    if abs(dx) > abs(dy):
        if abs(dx) > 20: # rotation_deadzone
            return "ROTATE_RIGHT" if dx > 0 else "ROTATE_LEFT"
        return "HOLD"
    else:
        return "ZOOM_IN" if distance > 70 else "ZOOM_OUT"

while cap.isOpened():
    success, image = cap.read()
    if not success: continue

    now = time.time()
    frame_count += 1

    if frame_count % PROCESS_EVERY_N_FRAMES == 0:
        small = cv2.resize(image, (160, 120))
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = hands.process(rgb)
        
        if results.multi_hand_landmarks:
            last_hand_landmarks = results.multi_hand_landmarks[0]
            hand_detected = True
            frames_without_hand = 0
        else:
            frames_without_hand += 1
            if frames_without_hand > MAX_FRAMES_WITHOUT_HAND:
                last_hand_landmarks = None
                hand_detected = False
                gesture_buffer.clear()

    if hand_detected and last_hand_landmarks:
        # Get Key Points
        landmarks = last_hand_landmarks.landmark
        thumb = landmarks[4]
        index = landmarks[8]
        
        # 1. ZOOM & ROTATE LOGIC (Your friend's logic)
        dx = (thumb.x - index.x) * 320
        dy = (thumb.y - index.y) * 240
        dist = math.hypot(dx, dy)
        
        gesture = get_gesture(dx, dy, dist)
        gesture_buffer.append(gesture)

        if len(gesture_buffer) == 3 and len(set(gesture_buffer)) == 1:
            g = gesture_buffer[0]
            if "ROTATE" in g and now - last_rotation_time > 0.1:
                pyautogui.press("right" if g == "ROTATE_RIGHT" else "left")
                last_rotation_time = now
            elif "ZOOM" in g and now - last_zoom_time > 0.15:
                pyautogui.hotkey("ctrl", "+" if g == "ZOOM_IN" else "-")
                last_zoom_time = now

        # 2. NEW: PALM & FIST (Mode Switching)
        # Check if 4 fingers are "up" (y-coordinate is smaller than the knuckle)
        fingers_up = [
            landmarks[8].y < landmarks[6].y,   # Index
            landmarks[12].y < landmarks[10].y, # Middle
            landmarks[16].y < landmarks[14].y, # Ring
            landmarks[20].y < landmarks[18].y  # Pinky
        ]

        if now - last_mode_time > MODE_COOLDOWN:
            # OPEN PALM -> Rendered View
            if all(fingers_up):
                pyautogui.press('z')
                pyautogui.press('8')
                print("MODE: Rendered")
                last_mode_time = now
            
            # CLOSED FIST -> Solid View
            elif not any(fingers_up):
                pyautogui.press('z')
                pyautogui.press('6')
                print("MODE: Solid")
                last_mode_time = now

    # Display
    image = cv2.flip(image, 1)
    cv2.putText(image, "ANAT3D ACTIVE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("ANAT3D - Controller", image)

    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()
