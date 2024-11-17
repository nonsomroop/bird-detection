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

load_dotenv()

pygame.mixer.init()
logging.getLogger("ultralytics").setLevel(logging.WARNING)

# Initialize Flask app
app = Flask(__name__)

# Load YOLOv8 model
# model_path = os.getenv('MODEL_PATH', './yolov8n.pt')
model_path = os.getenv('MODEL_PATH', './yolov8n.pt')
model = YOLO(model_path).cpu()

# Initialize PiCamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (320, 240)}))

# Initialize camera stream
picam2.start()

bird_count = 0
flying_count = 0
standing_count = 0

# Function to perform inference and annotate the image with YOLOv8
def process_frame(frame, fps):
    # Convert frame to RGB for YOLOv8 processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Perform object detection
    results = model(rgb_frame)

    global bird_count, flying_count, standing_count  # Declare as global to modify them
    bird_count = 0
    flying_count = 0
    standing_count = 0
    conf = 0.7
#     for result in results:
#         for obj in result.boxes:
#             if obj.conf >= conf:  # Check confidence
#                 bird_count += 1
#                 if obj.cls == 1:  # Assuming 0 is the class ID for birds
#                     standing_count += 1
#                 else:
#                     flying_count += 1
    # Annotate image
    annotated_frame = results[0].plot()  # Annotated image
    
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(annotated_frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    return annotated_frame

# Generator function to stream video to the browser
def generate():
    prev_time = time.time()
    frame_skip = 0

    while True:
        # Capture image from the camera
        frame_skip += 1
         
        if frame_skip % 4 != 0:  # Skip every other frame
            picam2.capture_array()  # Still capture to keep the stream updated
            continue
        
        frame = picam2.capture_array()
        
        # Calculate FPS
        current_time = time.time()
        fps = 1.0 / (current_time - prev_time)
        prev_time = current_time
        
        # Process the frame with YOLOv8
        annotated_frame = process_frame(frame, fps)
        time.sleep(0.1)  # Capture frames at roughly 10 FPS

        # Convert the annotated frame to JPEG format for web transmission
        ret, jpeg = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if not ret:
            continue

        # Yield the frame as a byte string in the correct format for video streaming
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

# Route to serve the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to stream the video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/play_sound', methods=['GET'])
def play_sound():
    # return "Audio playing"
    # sound_path = os.path.join('static', 'sound', 'test_sound.aac')
    sound_path = "./static/sound/test_sound.wav"
    # Ensure the file exists before trying to play it
    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()

        # Wait for the sound to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Check if sound is still playing

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

