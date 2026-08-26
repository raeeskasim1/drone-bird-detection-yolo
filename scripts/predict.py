from ultralytics import YOLO

def main():

    model = YOLO(
        r"runs\detect\runs\drone_bird_yolo11n\weights\best.pt"
    )

    results = model.predict(
        source="inference_samples",
        imgsz=640,
        conf=0.25,
        save=True,
        project="runs/inference",
        name="new_images"
    )

    print(f"Processed {len(results)} images")

if __name__ == "__main__":
    main()