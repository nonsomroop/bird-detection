# Bird Detection 🐦

Real-time bird detection with a Flask UI, live video feed, and audio alerts.

## System Overview
![IoT Components](image/Bird%20Detection.png)

## IoT Components
- Camera module for live video capture
- Speaker for audio deterrent
- Raspberry Pi for on-device inference
- Power storage for field deployment

## Quick Start
1. Install dependencies:
```
pip install -r requirements.txt
```
2. Run the app (laptop/desktop):
```
python app.py
```
3. Open `http://localhost:5000`.

## What’s Inside
- `app.py`: laptop/desktop webcam
- `app-pi.py`: Raspberry Pi with Pi Camera

## Features
- Live video stream with YOLO annotations
- Counts for total, flying, and standing birds
- Automatic sound when a standing bird is detected for 5 seconds
- Manual sound trigger for debugging

## Requirements
- Python 3.9+
- Camera device (webcam or Pi Camera)
- `pygame` audio output configured on your device

Dependencies are listed in `requirements.txt`:
```
Flask==2.3.2
opencv-python==4.6.0.66
python-dotenv==1.0.0
ultralytics==8.0.14
```
On macOS, use `requirements-mac.txt` (pins `ultralytics==8.4.14`, `torch<2.6`, `torchvision==0.20.1`, and `numpy<2`):
```
pip install -r requirements-mac.txt
```
Default install:
```
pip install -r requirements.txt
```

## Project Structure
- `app.py`: Laptop/desktop server (webcam)
- `app-pi.py`: Raspberry Pi server (Pi Camera)
- `templates/index.html`: UI
- `static/js/index.js`: UI logic
- `static/css/index.css`: UI styles
- `static/sound/`: audio files used for alerts

## Setup
1. Create a virtual environment (recommended).
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Create a `.env` file with your model path:
```
MODEL_PATH=./bird.pt
```
If you omit this, the default is `./bird.pt`.

## Run (Laptop/Desktop)
```
python app.py
```
Open `http://localhost:5000` in your browser.

## Run (Raspberry Pi)
```
python app-pi.py
```
Open `http://<pi-ip>:5000` in your browser.

## Notes
- Audio files are expected in `static/sound/`.
- `app.py` uses `./static/sound/falcon.wav` for auto alerts and `./static/sound/hawksound.wav` for manual play.
- `app-pi.py` uses `./static/sound/hawksound.wav` for auto alerts and `./static/sound/falcon.wav` for manual play.

## Troubleshooting
- If the camera fails to open, verify device permissions and that no other app is using it.
- If audio does not play, verify `pygame` audio output is configured on your OS.
