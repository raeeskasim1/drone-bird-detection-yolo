from ultralytics import YOLO


def main():
    model = YOLO(
        "runs/detect/runs/drone_bird_yolo11n/weights/best.pt"
    )

    metrics = model.val(
        data="dataset_split/data.yaml",
        split="test",
        imgsz=640,
        batch=4,
        workers=0
    )


if __name__ == "__main__":
    main()