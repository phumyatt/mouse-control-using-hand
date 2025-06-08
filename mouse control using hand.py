import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import pyttsx3 
import threading  
import speech_recognition as sr

# ========== Voice Feedback Setup ======== I will be home==
engine = pyttsx3.init()
engine.setProperty('rate', 175)
VOICE_ENABLED = True
last_spoken = ""

def speak(text):
    global last_spoken
    if VOICE_ENABLED and text != last_spoken:
        engine.say(text)
        engine.runAndWait()
        last_spoken = text 

# ========== Voice Command Thread ==========
voice_command = ""

def listen_for_voice():
    global voice_command
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio).lower()
                voice_command = text
                print(f"Voice command: {text}")
        except:
            continue

threading.Thread(target=listen_for_voice, daemon=True).start()  

# ========== Hand Gesture Setup ==========
cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()
prev_loc_x, prev_loc_y = 0, 0
smoothening = 7

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75)
mp_draw = mp.solutions.drawing_utils

gesture_buffer = {"LEFT_CLICK": 0, "RIGHT_CLICK": 0, "DRAG": 0, "SCROLL": 0}
gesture_threshold = 5
fps_time = time.time()
dragging = False
auto_click_time = 0
auto_click_triggered = False

mode = "MOVE"

def finger_up(lm, tip, pip):
    return lm[tip].y < lm[pip].y

def get_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def get_finger_xy(lm, idx, w, h):
    return int(lm[idx].x * w), int(lm[idx].y * h)

# ========== Main Loop ==========
while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    curr_time = time.time()
    fps = 1 / (curr_time - fps_time)
    fps_time = curr_time

    # ===== Voice Control Mode Switch =====
    if voice_command:
        cmd = voice_command.strip()
        if "move" in cmd:
            mode = "MOVE"
            speak("Move mode")
        elif "pause" in cmd:
            mode = "PAUSED"
            speak("Paused")
        elif "click" in cmd and "right" not in cmd:
            pyautogui.click()
            speak("Left click")
        elif "right click" in cmd:
            pyautogui.click(button="right")
            speak("Right click")
        elif "scroll" in cmd:
            mode = "SCROLL"
            speak("Scroll mode")
        elif "drag" in cmd:
            pyautogui.mouseDown()
            dragging = True
            mode = "DRAG"
            speak("Drag start")
        elif "stop drag" in cmd:
            pyautogui.mouseUp()
            dragging = False
            speak("Drag stop")
            mode = "MOVE"
        voice_command = ""  # Reset command

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        lm = hand_landmarks.landmark
        mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        index = get_finger_xy(lm, 8, w, h)
        thumb = get_finger_xy(lm, 4, w, h)
        middle = get_finger_xy(lm, 12, w, h)
        ring = get_finger_xy(lm, 16, w, h)

        fingers = [
            finger_up(lm, 8, 6),
            finger_up(lm, 12, 10),
            finger_up(lm, 16, 14),
            finger_up(lm, 20, 18)
        ]

        pinch_index = get_distance(index, thumb) < 40
        pinch_ring = get_distance(ring, thumb) < 40
        all_up = sum(fingers) == 4

        gesture_buffer = {k: max(v - 1, 0) for k, v in gesture_buffer.items()}

        if all_up:
            if mode != "PAUSED":
                mode = "PAUSED"
                speak("Paused")
        elif pinch_index and not fingers[0]:
            gesture_buffer["DRAG"] += 2
            if gesture_buffer["DRAG"] > gesture_threshold:
                if mode != "DRAG":
                    speak("Drag start")
                mode = "DRAG"
        elif pinch_ring:
            gesture_buffer["RIGHT_CLICK"] += 2
            if gesture_buffer["RIGHT_CLICK"] > gesture_threshold:
                pyautogui.click(button="right")
                speak("Right click")
                gesture_buffer["RIGHT_CLICK"] = 0
        elif pinch_index:
            gesture_buffer["LEFT_CLICK"] += 2
            if gesture_buffer["LEFT_CLICK"] > gesture_threshold:
                pyautogui.click()
                speak("Left click")
                gesture_buffer["LEFT_CLICK"] = 0
                auto_click_time = time.time()
                auto_click_triggered = False
        elif fingers[0] and fingers[1] and not fingers[2] and not fingers[3]:
            gesture_buffer["SCROLL"] += 2
            if gesture_buffer["SCROLL"] > gesture_threshold:
                if mode != "SCROLL":
                    speak("Scroll mode")
                mode = "SCROLL"
        else:
            if mode != "MOVE":
                speak("Move mode")
            mode = "MOVE"

        # ===== Cursor Control =====
        if mode == "MOVE":
            x = np.interp(lm[8].x * screen_w, [0, screen_w], [0, screen_w])
            y = np.interp(lm[8].y * screen_h, [0, screen_h], [0, screen_h])
            curr_loc_x = prev_loc_x + (x - prev_loc_x) / smoothening
            curr_loc_y = prev_loc_y + (y - prev_loc_y) / smoothening
            pyautogui.moveTo(curr_loc_x, curr_loc_y)
            prev_loc_x, prev_loc_y = curr_loc_x, curr_loc_y

        elif mode == "DRAG":
            pyautogui.moveTo(lm[8].x * screen_w, lm[8].y * screen_h)
        else:
            if dragging:
                pyautogui.mouseUp()
                dragging = False
                speak("Drag stop")

        if mode == "SCROLL":
            scroll_speed = int((lm[8].y - lm[12].y) * 30)
            pyautogui.scroll(scroll_speed)

        if pinch_index:
            if not auto_click_triggered and time.time() - auto_click_time > 2:
                pyautogui.click()
                speak("Auto click")
                auto_click_triggered = True
        else:
            auto_click_time = time.time()
            auto_click_triggered = False

        cv2.putText(img, f"Mode: {mode}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    else:
        if mode != "PAUSED":

            mode = "PAUSED"
            speak("Paused")

    cv2.putText(img, f'FPS: {int(fps)}', (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.imshow("Gesture + Voice Controlled Mouse", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
