# App.py is for running our best model in laptop/computer with the default camera (laptop camera)
# This code requires .env for model path

import cv2
from ultralytics import YOLO
from flask import Flask, jsonify, request, render_template, Response, send_from_directory
from dotenv import load_dotenv
import os
import logging  
import pygame
import time
import random

pygame.mixer.init()

logging.getLogger("ultralytics").setLevel(logging.WARNING)

load_dotenv()

app = Flask(__name__)

model_path = os.getenv('MODEL_PATH', './yolov8n.pt')
model = YOLO(model_path)

state = {
    "system_status": True,
    "volume": 50,
}

conf_threshold_value = 0.5  
bird_count = 0
flying_count = 0
standing_count = 0

standing_start_time = None


def process_frame(model, frame, conf=0.5):
    results = model(frame, conf=conf)

    global bird_count, flying_count, standing_count, standing_start_time  
    bird_count = 0
    flying_count = 0
    standing_count = 0

    bird_standing_detected = False

    for result in results:
        for obj in result.boxes:
            if obj.conf >= conf:  
                bird_count += 1
                if obj.cls == 1:  
                    standing_count += 1
                    bird_standing_detected = True

                else:
                    flying_count += 1

    if bird_standing_detected:

        if standing_start_time is None:
            standing_start_time = time.time()
            print("====== Time start =======")
        
    else:
        print("====== Time reset  ========")
        standing_start_time = None

    if standing_start_time is not None and time.time() - standing_start_time >= 5:
        print("===================!!! Time out !!!=====================")
        play_sound_flask()

        standing_start_time = None
    annotated_frame = results[0].plot()

    return annotated_frame

def generate_frames(conf_threshold=0.5):
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
            annotated_frame = process_frame(model, frame, conf=conf_threshold)
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            cap.release()
            break

#play_sound_flask() is for triggering audio automatically when bird is detected as standing for 5 seconds
def play_sound_flask():
    sound_path = "./static/sound/falcon.wav" 

    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
        
        audio_duration = 60  
        random_start = random.randint(0, audio_duration - 5)  
        
        pygame.mixer.music.set_volume(0.5)

        pygame.mixer.music.play(start=random_start)
        
        print(f"Playing audio from {random_start} seconds for 5 seconds.")
        
        time.sleep(5)
        
        pygame.mixer.music.stop()
    else:
        print("Sound file not found")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(conf_threshold_value), mimetype='multipart/x-mixed-replace; boundary=frame')

#play_sound() is for triggering audio manually for debug purposes
@app.route('/play_sound', methods=['GET'])
def play_sound():
  
    sound_path = "./static/sound/hawksound.wav"
    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
        
        audio_duration = 60  
        random_start = random.randint(0, audio_duration - 5)  
        
        pygame.mixer.music.set_volume(0.5)

        pygame.mixer.music.play(start=random_start)
        
        print(f"Playing audio from {random_start} seconds for 5 seconds.")
        
        time.sleep(5)
        
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
    conf_threshold_value = data.get('conf_threshold', 0.5)
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

