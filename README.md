# Drone vs Bird Detection using YOLO11

End-to-end computer vision project for detecting and tracking **birds and drones** using a custom fine-tuned YOLO11 model.

Dataset Collection → Annotation → Fine-Tuning → Evaluation → Image Detection → Video Tracking → FastAPI → Web Interface → Live Drone Tracking

---

## Features

### Image Detection

- Detects birds and drones
- Supports multiple objects
- Displays bounding boxes and confidence scores
- Returns annotated images

### Video Tracking

- Detects birds and drones
- Uses YOLO11 + ByteTrack
- Assigns track IDs across frames
- Produces annotated output video
- Uses FFmpeg for browser-compatible MP4 playback

### Live Camera

- Drone-only real-time monitoring
- YOLO11 + ByteTrack tracking
- Displays bounding box, confidence and Track ID
- Shows continuous tracked duration
- Allows short detection gaps without immediately resetting the timer

---

## Classes

| ID | Class |
|---:|---|
| 0 | Bird |
| 1 | Drone |

---

## Dataset

The dataset was manually collected and annotated using Roboflow.

**Total annotated images: 192**

| Split | Images |
|---|---:|
| Train | 134 |
| Validation | 28 |
| Test | 30 |

### Dataset Distribution

| Split | Bird | Drone | Mixed |
|---|---:|---:|---:|
| Train | 59 | 64 | 11 |
| Validation | 16 | 10 | 2 |
| Test | 16 | 12 | 2 |

A fixed random seed was used for reproducible dataset splitting.

---

## Model

- **Model:** YOLO11n
- **Pretrained weights:** yolo11n.pt
- **Epochs:** 50
- **Image size:** 640
- **Batch size:** 4
- **GPU:** NVIDIA GTX 1650 4GB

The pretrained YOLO11n model was fine-tuned on the custom bird and drone dataset instead of being trained from scratch.

---

## Evaluation Results

### Validation Results

| Metric | Result |
|---|---:|
| Precision | 0.708 |
| Recall | 0.809 |
| mAP50 | 0.821 |
| mAP50-95 | 0.544 |

### Final Test Results

| Metric | Result |
|---|---:|
| Precision | 0.878 |
| Recall | 0.837 |
| mAP50 | 0.880 |
| mAP50-95 | 0.584 |

### Per-Class Results

| Class | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| Bird | 0.845 | 0.889 | 0.907 | 0.543 |
| Drone | 0.910 | 0.786 | 0.854 | 0.625 |

Approximate YOLO inference speed during evaluation: **9.3 ms/image**

---

## Object Tracking

Video and live tracking use **ByteTrack**.

YOLO detects objects in each frame, while ByteTrack associates detections across consecutive frames and assigns temporary track IDs.

Example:

    Frame 1 → Drone ID 4
    Frame 2 → Drone ID 4
    Frame 3 → Drone ID 4

Track IDs are temporary tracking identities and do not represent permanent identification of a physical drone.

---

## FastAPI Backend

The trained model is served through FastAPI.

| Endpoint | Purpose |
|---|---|
| GET /health | API health check |
| POST /predict | Image detection |
| POST /track-video | Video detection and tracking |
| POST /live-detect | Live drone tracking |

---

## Web Interface

The frontend is built using:

- HTML
- CSS
- JavaScript

The application provides three modes:

**Image Detection | Video Tracking | Live Camera**

### Live Camera Pipeline

    Webcam
       ↓
    Browser Frame Capture
       ↓
    FastAPI
       ↓
    YOLO11
       ↓
    ByteTrack
       ↓
    Track ID + Confidence + Duration
       ↓
    Live Bounding Box

---

## Project Structure

    drone-bird-detection/
    │
    ├── app.py
    ├── README.md
    ├── requirements.txt
    │
    ├── scripts/
    │   ├── split_dataset.py
    │   ├── train.py
    │   ├── evaluate.py
    │   ├── predict.py
    │   ├── track.py
    │   └── realtime.py
    │
    └── static/
        ├── index.html
        ├── style.css
        └── app.js

---

## Technologies Used

- Python
- PyTorch
- Ultralytics YOLO11
- ByteTrack
- OpenCV
- FastAPI
- Roboflow
- HTML
- CSS
- JavaScript


---

## Limitations

- Dataset contains only 192 annotated images
- Small or distant drones may be harder to detect
- Lighting, motion blur and different environments can affect performance
- ByteTrack IDs may change after longer detection gaps
- Real-time performance depends on available hardware

This project is intended as an **AI/Computer Vision portfolio project**, not a production surveillance system.

---

## Future Improvements

- Larger and more diverse dataset
- Improved small-drone detection
- More stable long-term tracking
- Drone event alerts
- Automatic recording of confirmed drone events
- Cloud deployment

---

