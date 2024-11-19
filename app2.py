# App2.py is for running the lightweight model in the raspberry pi with raspberry pi camera
# This code requires .env for model path
import io
import time
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify, send_from_directory
from picamera2 import Picamera2
from ultralytics import YOLO
from dotenv import load_dotenv
import os
import pygame
import logging
import time

load_dotenv()

pygame.mixer.init()
logging.getLogger("ultralytics").setLevel(logging.WARNING)

app = Flask(__name__)

model_path = os.getenv('MODEL_PATH', './yolov8n.pt')
model = YOLO(model_path)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))

picam2.start()

bird_count = 0
flying_count = 0
standing_count = 0

standing_start_time = None

def process_frame(frame):
    global bird_count, flying_count, standing_count, standing_start_time  

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    results = model(rgb_frame)

    bird_count = 0
    flying_count = 0
    standing_count = 0
    conf = 0.5
        
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

def generate():
    while True:
        frame = picam2.capture_array()

        annotated_frame = process_frame(frame)
        time.sleep(0.1)  

        ret, jpeg = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ret:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

#play_sound_flask() is for triggering audio automatically when bird is detected as standing for 5 seconds
def play_sound_flask():
    sound_path = "./static/sound/hawksound.wav"
    
    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10) 
    else:
        print("Sound file not found")
        
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

#play_sound() is for triggering audio manually for debug purposes
@app.route('/play_sound', methods=['GET'])
def play_sound():
 
    sound_path = "./static/sound/falcon.wav"
    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10) 

        return jsonify({"message": "Sound played successfully"})
    else:
        return jsonify({"error": "Sound file not found"}), 404
    
@app.route('/sound/<path:filename>')
def download_file(filename):
    return send_from_directory('./static/sound', filename)

@app.route('/get_counts', methods=['GET'])
def get_counts():
    print(f"Total: {bird_count}, Flying: {flying_count}, Standing: {standing_count}")

    return jsonify({
        "total": bird_count,
        "flying": flying_count,
        "standing": standing_count
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
