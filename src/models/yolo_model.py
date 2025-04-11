import torch
from ultralytics import YOLO

# Para descobrir qual o dispositivo de processamento
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo: {device}")


class Yolov5m:
    def __init__(self, model_path="models/yolov5mu.pt"):
        self.model = YOLO(model_path).to(device)
        self.model.eval()

    def detect(self, frame):
        results = self.model.predict(frame, classes=[0], conf=0.5, verbose=False)

        return results[0]
