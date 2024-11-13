import cv2
from ultralytics import YOLO
from flask import Flask, jsonify, request, render_template, Response, send_from_directory
from dotenv import load_dotenv
import os
import logging  # Import logging
import pygame

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

conf_threshold_value = 0.3  # Set confidence threshold to 70%
bird_count = 0
flying_count = 0
standing_count = 0

def process_frame(model, frame, conf=0.3):
    # Pass the confidence threshold of 0.7 to filter out predictions below 70%
    results = model(frame, conf=conf)

    global bird_count, flying_count, standing_count  # Declare as global to modify them
    bird_count = 0
    flying_count = 0
    standing_count = 0

    for result in results:
        for obj in result.boxes:
            if obj.conf >= conf:  # Check confidence
                bird_count += 1
                if obj.cls == 1:  # Assuming 0 is the class ID for birds
                    standing_count += 1
                else:
                    flying_count += 1
    
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
    sound_path = "./static/sound/test_sound.wav"
    # Ensure the file exists before trying to play it
    if os.path.exists(sound_path):
        pygame.mixer.music.load(sound_path)
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
