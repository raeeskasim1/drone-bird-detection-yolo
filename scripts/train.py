from ultralytics import YOLO


def main():
    # Load pretrained YOLO11 Nano
    model = YOLO("yolo11n.pt")

    # Fine-tune on our custom dataset
    model.train(
        data="dataset_split/data.yaml",
        epochs=50,
        imgsz=640,
        batch=4,
        workers=0,
        project="runs",
        name="drone_bird_yolo11n"
    )


if __name__ == "__main__":
    main()