# Drone vs Bird Detection using YOLO11

Custom object detection project for detecting and distinguishing birds and drones using Ultralytics YOLO11.

The project is being built end-to-end as an AI engineering project:

Dataset Collection → Annotation → Dataset Split → Fine-Tuning → Evaluation → Error Analysis → Inference → FastAPI Deployment

---

## Project Goal

Build a lightweight object detection model capable of:

- Detecting birds
- Detecting drones
- Localizing each object using bounding boxes
- Handling images containing multiple objects

Classes:

0 = bird  
1 = drone

---

## Dataset

The dataset was manually collected and annotated using Roboflow.

Total annotated images: 192

A custom Python script was used to create the final dataset split:

- Train: 134 images
- Validation: 28 images
- Test: 30 images

Distribution:

Train:
- Bird: 59
- Drone: 64
- Mixed: 11

Validation:
- Bird: 16
- Drone: 10
- Mixed: 2

Test:
- Bird: 16
- Drone: 12
- Mixed: 2

A fixed random seed was used so the split is reproducible.

Each image is always kept together with its matching YOLO annotation file.

---

## YOLO Annotation Format

Each object is stored in YOLO format as:

class_id x_center y_center width height

The bounding box coordinates are normalized between 0 and 1.

---

## Model

Model used: YOLO11 Nano

Pretrained weights: yolo11n.pt

YOLO11n was selected because it is lightweight, fast, and suitable for local training and later API deployment.

---

## Fine-Tuning

The pretrained YOLO11n model was fine-tuned on the custom bird and drone dataset.

The model was not trained from scratch.

Ultralytics automatically adapted the detection head according to the two project classes defined in data.yaml.

Training configuration:

- Epochs: 50
- Image size: 640
- Batch size: 4
- Workers: 0

Batch size was reduced from 8 to 4 because of GPU memory limitations on the GTX 1650.

---

## Training Losses

YOLO uses multiple losses because object detection must learn both object class and location.

- cls_loss → predicts whether the object is bird or drone
- box_loss → improves bounding box location
- dfl_loss → improves bounding box precision

Lower loss values are generally better.

During training:

- cls_loss decreased from about 3.893 to 0.883
- box_loss decreased from about 1.426 to 0.799

---

## Train, Validation and Test

Training data is used to update model weights.

Validation data is used during training to measure generalization and select the best model.

Test data is only used after training is complete for final evaluation.

YOLO saves:

- best.pt → best validation checkpoint
- last.pt → final epoch checkpoint

best.pt is used for final evaluation and inference.

---

## Evaluation Metrics

Object detection is evaluated mainly using Precision, Recall and mAP instead of plain classification accuracy.

- Precision → how many predicted objects were actually correct
- Recall → how many real objects were successfully detected
- mAP50 → detection performance at IoU 0.50
- mAP50-95 → stricter evaluation across IoU thresholds from 0.50 to 0.95

Higher values are better.

---

## Validation Results

| Metric | Result |
|---|---:|
| Precision | 0.708 |
| Recall | 0.809 |
| mAP50 | 0.821 |
| mAP50-95 | 0.544 |

---

## Final Test Results

| Metric | Result |
|---|---:|
| Precision | 0.878 |
| Recall | 0.837 |
| mAP50 | 0.880 |
| mAP50-95 | 0.584 |

Per-class results:

| Class | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| Bird | 0.845 | 0.889 | 0.907 | 0.543 |
| Drone | 0.910 | 0.786 | 0.854 | 0.625 |

The model performed well on the held-out test set.

Bird detection achieved strong recall, while drone detection achieved very high precision.

---

## Inference Speed

Approximate test-time speed:

- Preprocessing: 0.8 ms/image
- Inference: 9.3 ms/image
- Postprocessing: 1.6 ms/image

This makes YOLO11n suitable for lightweight deployment.

---

