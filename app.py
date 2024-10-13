import cv2
from flask import Flask, render_template, Response
from ultralytics import YOLO

app = Flask(__name__)

model = YOLO('yolov8n.pt')

def process_frame(model, frame):
    results = model(frame)
    return results[0].plot()

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        annotated_frame = process_frame(model, frame)
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/play_sound')
def play_sound():
    return app.send_static_file('sound/test_sound.aac')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
