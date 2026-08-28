from fastapi import FastAPI, UploadFile, File, HTTPException
from ultralytics import YOLO
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import time
from pathlib import Path
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import subprocess

app = FastAPI()

OUTPUT_DIR = Path("runs/api_outputs")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

VIDEO_INPUT_DIR = Path("runs/video_inputs")

VIDEO_INPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

VIDEO_OUTPUT_DIR = Path("runs/video_outputs").resolve()

VIDEO_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUT_DIR),
    name="outputs"
)

app.mount(
    "/video-outputs",
    StaticFiles(directory=VIDEO_OUTPUT_DIR),
    name="video_outputs"
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

live_tracks = {}

TRACK_GAP_TOLERANCE = 1.0

model = YOLO(
    r"runs\detect\runs\drone_bird_yolo11n\weights\best.pt"
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    image_bytes = await file.read()

    try:
        image =Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )
    start = time.perf_counter()
    results = model.predict(
        source=image,
        conf=0.35,
        imgsz=640,
        verbose=False
    )
    inference_ms = (
        time.perf_counter() - start
    ) * 1000

    result = results[0]

    filename = f"prediction_{uuid4().hex}.jpg"

    output_path = OUTPUT_DIR / filename

    result.save(
        filename=str(output_path)
    )

    detections = []

    for box in result.boxes:

        class_id = int(box.cls[0])
        class_name = model.names[class_id]

        confidence = float(box.conf[0])
        coordinates = box.xyxy[0].tolist()

        detections.append({
            "class_id": class_id,
            "class": class_name,
            "confidence": round(confidence, 3),
            "box": [round(x, 2) for x in coordinates]
        })

    return {
        "count": len(detections),
        "inference_ms": round(inference_ms, 2),
        "detections": detections,
        "annotated_image": f"/outputs/{filename}"
    }

@app.post("/track-video")
async def track_video(file:UploadFile = File(...)):

    extension = Path(file.filename).suffix.lower()

    allowed_extensions = {
        ".mp4",
        ".avi",
        ".mov",
        ".mkv"
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid video file"
        )

    filename = f"video_{uuid4().hex}{extension}"

    input_path = VIDEO_INPUT_DIR / filename

    with open(input_path, "wb") as buffer:

        while True:

            chunk = await file.read(1024 * 1024)

            if not chunk:
                break

            buffer.write(chunk)

    job_id = f"tracking_{uuid4().hex}"

    results = model.track(
        source=str(input_path),
        tracker="bytetrack.yaml",
        conf=0.25,
        imgsz=640,
        save=True,
        project=str(VIDEO_OUTPUT_DIR),
        name=job_id,
        stream=True,
        verbose=False
    )


    for _ in results:
        pass

    output_folder = VIDEO_OUTPUT_DIR / job_id

    video_files = [
        file
        for file in output_folder.iterdir()
        if file.suffix.lower() in {".mp4", ".avi", ".mov", ".mkv"}
    ]

    
    if not video_files:
        raise HTTPException(
        status_code=500,
        detail="Processed video was not created"
    )


    output_video = video_files[0]

    mp4_output = output_video.with_suffix(".mp4")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", str(output_video),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(mp4_output)
        ],
        check=True
    )

    relative_path = mp4_output.relative_to(
        VIDEO_OUTPUT_DIR
    ).as_posix()


    input_path.unlink(missing_ok=True)


    return {
        "message": "Video tracking completed",
        "processed_video": f"/video-outputs/{relative_path}"
    }


@app.post("/live-detect")
async def live_detect(file: UploadFile = File(...)):

    image_bytes = await file.read()

    try:
        image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid camera frame"
        )


    results = model.track(
        source=image,
        tracker="bytetrack.yaml",
        persist=True,
        conf=0.35,
        imgsz=640,
        classes=[1],
        verbose=False
    )


    result = results[0]

    detections = []

    current_time = time.time()

    seen_track_ids = set()


    for box in result.boxes:

        class_id = int(box.cls[0])

        class_name = model.names[class_id]

        confidence = float(box.conf[0])

        coordinates = box.xyxy[0].tolist()

        track_id = (
            int(box.id[0])
            if box.id is not None
            else None
        )

        if track_id is not None:

            if track_id not in live_tracks:

                live_tracks[track_id] = {
                    "first_seen": current_time,
                    "last_seen": current_time
                }

            else:

                gap = (
                    current_time
                    - live_tracks[track_id]["last_seen"]
                )

                # Same ID returned after a long gap
                # Start a NEW timer
                if gap > TRACK_GAP_TOLERANCE:

                    live_tracks[track_id] = {
                        "first_seen": current_time,
                        "last_seen": current_time
                    }

                else:

                    live_tracks[track_id]["last_seen"] = (
                        current_time
                    )


            duration = (
                current_time
                - live_tracks[track_id]["first_seen"]
            )

        else:

            duration = 0

        detections.append({
            "track_id": track_id,
            "class_id": class_id,
            "class": class_name,
            "confidence": round(confidence, 3),
            "duration": round(duration, 1),

            "box": [
                round(value, 2)
                for value in coordinates
            ]
        })
        for track_id in list(live_tracks.keys()):

            last_seen = live_tracks[track_id]["last_seen"]

            if current_time - last_seen > TRACK_GAP_TOLERANCE:
                del live_tracks[track_id]

    return {
        "count": len(detections),
        "detections": detections
    }

@app.get("/")
def home():
    return FileResponse("static/index.html")