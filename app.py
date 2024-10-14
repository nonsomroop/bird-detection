import cv2
from ultralytics import YOLO
from flask import Flask, jsonify, request, render_template, Response, send_from_directory
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

model_path = os.getenv('MODEL_PATH', './yolov8n.pt')

model = YOLO(model_path)

state = {
    "system_status": False,  
    "volume": 50,
}

def process_frame(model, frame):
    results = model(frame)
    return results[0].plot()

def generate_frames():
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

            annotated_frame = process_frame(model, frame)
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
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/play_sound', methods=['GET'])
def play_sound():
    return "Audio playing"

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
    return jsonify(state)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
