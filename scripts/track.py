from ultralytics import YOLO

def main():

    model = YOLO(
         r"runs\detect\runs\drone_bird_yolo11n\weights\best.pt"
    )

    model.track(
        source=r"tracking_samples\mixkit-drone-view-over-trees-613-hd-ready.mp4",
        tracker="bytetrack.yaml",
        classes=[1],
        conf=0.20,
        iou=0.50,
        imgsz=640,
        save=True,
        project="runs/tracking",

        name="drone_tracking"
    )
if __name__ == "__main__":
    main()