from ultralytics import YOLO


def main():

    model = YOLO(
        "runs/detect/runs/drone_bird_yolo11n/weights/best.pt"
    )

    model.track(
        source=0,
        tracker="bytetrack.yaml",
        classes=[1],
        conf=0.35,
        iou=0.50,
        imgsz=640,
        show=True
    )


if __name__ == "__main__":
    main()