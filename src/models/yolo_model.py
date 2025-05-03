import torch
from ultralytics import YOLO

class Yolov5m:
    def __init__(self, model_path="src/models/yolov5mu.pt"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Usando dispositivo: {self.device}")
        
        self.model = YOLO(model_path).to(self.device)
        self.model.eval()

    def detect(self, frame):
        if isinstance(frame, torch.Tensor):
            frame = frame.to(self.device)

        results = self.model.predict(frame, classes=[0], conf=0.5, verbose=False)
        return results[0]

if __name__ == "__main__":
    detector = Yolov5m()
    print(f"Modelo está na GPU? {next(detector.model.parameters()).is_cuda}")
