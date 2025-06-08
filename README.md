Gesture and Voice Controlled Mouse

Features
Hand Gesture Recognition:
Move mouse cursor by moving your index finger.
Left-click and right-click with pinch gestures.
Drag and drop using pinch gestures.
Scroll by using two fingers.
Automatic clicking after holding pinch for 2 seconds.
Voice Commands:
Switch between modes like move, pause, scroll, and drag.
Trigger left and right clicks by voice.
Start and stop drag via voice.
Voice Feedback:
Audio feedback announces mode changes and actions.

Requirements
Python 3.7+
Webcam
Microphone
Python Libraries

Install dependencies via pip:
pip install opencv-python mediapipe pyautogui numpy pyttsx3 SpeechRecognition pyaudio
Note: For pyaudio installation, you might need to install system-specific dependencies. On Windows, use precompiled wheels from here. On Linux, use sudo apt-get install portaudio19-dev python3-pyaudio.

Usage
Run the Python script:
python gesture_voice_mouse.py
Allow access to your webcam and microphone.
Use your hand gestures in front of the webcam:
Move your index finger to move the cursor.
Pinch index finger and thumb for left click.
Pinch ring finger and thumb for right click.
Use two fingers to scroll.
Pinch and hold for dragging.
Use voice commands like:
"move" - switch to move mode
"pause" - pause mouse control
"click" - perform left click
"right click" - perform right click
"scroll" - switch to scroll mode
"drag" - start drag
"stop drag" - stop drag
Press ESC to quit.

Code Structure
Hand tracking and gestures handled by MediaPipe.
Mouse actions performed by PyAutoGUI.
Voice commands captured in a background thread using SpeechRecognition.
Voice feedback via pyttsx3 text-to-speech engine.
Gesture states managed with buffers to reduce false positives.
Smooth cursor movement with interpolation.

Troubleshooting
Make sure webcam and microphone are working properly.
Adjust gesture_threshold and smoothing parameters for your environment.
If voice recognition fails frequently, ensure good microphone quality and minimal background noise.
Use headphones to prevent microphone picking up computer speakers.

License
This project is open source and free to use.


