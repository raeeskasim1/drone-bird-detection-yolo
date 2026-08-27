from fastapi import FastAPI, UploadFile, File, HTTPException
from ultralytics import YOLO
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import time
from pathlib import Path
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

OUTPUT_DIR = Path("runs/api_outputs")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUT_DIR),
    name="outputs"
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

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

@app.get("/")
def home():
    return FileResponse("static/index.html")