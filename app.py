import cv2
from ultralytics import YOLO
from flask import Flask, jsonify, request, render_template, Response, send_from_directory
from dotenv import load_dotenv
import os
import logging  # Import logging
import pygame
import time
import random

pygame.mixer.init()

# Set logging level for the ultralytics module to suppress messages
logging.getLogger("ultralytics").setLevel(logging.WARNING)

load_dotenv()

app = Flask(__name__)

model_path = os.getenv('MODEL_PATH', './yolov8n.pt')
model = YOLO(model_path)

state = {
    "system_status": True,
    "volume": 50,
}

conf_threshold_value = 0.7  # Set confidence threshold to 70%
bird_count = 0
flying_count = 0
standing_count = 0

standing_start_time = None


def process_frame(model, frame, conf=0.7):
    # Pass the confidence threshold of 0.7 to filter out predictions below 70%
    results = model(frame, conf=conf)

    global bird_count, flying_count, standing_count, standing_start_time  # Declare as global to modify them
    bird_count = 0
    flying_count = 0
    standing_count = 0

    bird_standing_detected = False

    for result in results:
        for obj in result.boxes:
            if obj.conf >= conf:  # Check confidence
                bird_count += 1
                if obj.cls == 1:  # Assuming 0 is the class ID for birds
                    standing_count += 1
                    bird_standing_detected = True

                else:
                    flying_count += 1

    if bird_standing_detected:
        print("====== 1 =======")

        # If it's the first time a bird is standing, start the timer
        if standing_start_time is None:
            standing_start_time = time.time()
            print("====== Time start +=======")
        
    else:
        # Reset the timer if no standing bird is detected
        print("====== 2 =======")
        standing_start_time = None

    # Check if standing bird has been detected for 5 seconds
    if standing_start_time is not None and time.time() - standing_start_time >= 5:
        # Trigger sound if the bird has been standing for 5 seconds
        print("===================Time out =====================")
        play_sound_flask()

        # Reset the timer after triggering the sound
        standing_start_time = None
    annotated_frame = results[0].plot()

    return annotated_frame

def generate_frames(conf_threshold=0.7):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    while True:
        if state["system_status"]:
            success, frame = cap.read()
            if not success:
                print("Error: Could not read frame.")
                break
            # Pass the confidence threshold of 0.7 to process_frame
            annotated_frame = process_frame(model, frame, conf=conf_threshold)
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            cap.release()
            break
def play_sound_flask():
    sound_path = "./static/sound/falcon.wav"  # Update to .mp3 file

    # Ensure the file exists before trying to play it
    if os.path.exists(sound_path):
        # Initialize the mixer and load the sound
        pygame.mixer.music.load(sound_path)
        
        # Calculate random start position (in seconds)
        audio_duration = 60  # 10 minutes in seconds
        random_start = random.randint(0, audio_duration - 5)  # Ensure there's at least 5 seconds left
        
        # Set playback start position
        pygame.mixer.music.set_volume(0.5)

        pygame.mixer.music.play(start=random_start)
        
        print(f"Playing audio from {random_start} seconds for 5 seconds.")
        
        # Let the audio play for 5 seconds
        time.sleep(5)
        
        # Stop the audio after 5 seconds
        pygame.mixer.music.stop()
    else:
        print("Sound file not found")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(conf_threshold_value), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/play_sound', methods=['GET'])
def play_sound():
    # return "Audio playing"
    # sound_path = os.path.join('static', 'sound', 'test_sound.aac')
    sound_path = "./static/sound/falcon.wav"
    # Ensure the file exists before trying to play it
    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
        
        # Calculate random start position (in seconds)
        audio_duration = 60  # 10 minutes in seconds
        random_start = random.randint(0, audio_duration - 5)  # Ensure there's at least 5 seconds left
        
        # Set playback start position
        pygame.mixer.music.set_volume(0.5)

        pygame.mixer.music.play(start=random_start)
        
        print(f"Playing audio from {random_start} seconds for 5 seconds.")
        
        # Let the audio play for 5 seconds
        time.sleep(5)
        
        # Stop the audio after 5 seconds
        pygame.mixer.music.stop()

        return jsonify({"message": "Sound played successfully"})
    else:
        return jsonify({"error": "Sound file not found"}), 404
@app.route('/sound/<path:filename>')
def download_file(filename):
    return send_from_directory('./static/sound', filename)

@app.route('/get_state', methods=['GET'])
def get_state():
    return jsonify(state)

@app.route('/update_state', methods=['POST'])
def update_state():
    global state
    data = request.json
    state['system_status'] = data.get('system_status', state['system_status'])
    state['volume'] = data.get('volume', state['volume'])
    print(state['system_status'])
    return jsonify(state)

@app.route('/set_confidence', methods=['POST'])
def set_confidence():
    global conf_threshold_value
    data = request.json
    conf_threshold_value = data.get('conf_threshold', 0.7)
    return jsonify({"message": "Confidence threshold updated", "confidence_threshold": conf_threshold_value})

@app.route('/get_counts', methods=['GET'])
def get_counts():
    return jsonify({
        "total": bird_count,
        "flying": flying_count,
        "standing": standing_count
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

