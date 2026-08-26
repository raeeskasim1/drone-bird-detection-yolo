from pathlib import Path
import random
import shutil


SOURCE_IMAGES = Path("dataset/train/images")
SOURCE_LABELS = Path("dataset/train/labels")

OUTPUT_DIR = Path("dataset_split")

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

RANDOM_SEED = 42


def get_image_label_pairs():
    image_files = list(SOURCE_IMAGES.glob("*"))

    pairs = []

    for image_path in image_files:
        label_path = SOURCE_LABELS / f"{image_path.stem}.txt"

        if label_path.exists():
            pairs.append((image_path, label_path))

    return pairs


def create_folders():
    for split in ["train", "val", "test"]:
        (OUTPUT_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)


def copy_pairs(pairs, split_name):
    for image_path, label_path in pairs:
        shutil.copy2(
            image_path,
            OUTPUT_DIR / "images" / split_name / image_path.name
        )

        shutil.copy2(
            label_path,
            OUTPUT_DIR / "labels" / split_name / label_path.name
        )


def main():
    random.seed(RANDOM_SEED)

    pairs = get_image_label_pairs()

    print(f"Total image-label pairs: {len(pairs)}")

    random.shuffle(pairs)

    total = len(pairs)

    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_pairs = pairs[:train_end]
    val_pairs = pairs[train_end:val_end]
    test_pairs = pairs[val_end:]

    create_folders()

    copy_pairs(train_pairs, "train")
    copy_pairs(val_pairs, "val")
    copy_pairs(test_pairs, "test")

    print(f"Train: {len(train_pairs)}")
    print(f"Validation: {len(val_pairs)}")
    print(f"Test: {len(test_pairs)}")


if __name__ == "__main__":
    main()