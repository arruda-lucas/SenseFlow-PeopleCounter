import cv2


class VideoProcess:
    def __init__(self, source):
        self.source = source
        try:
            self.cap = cv2.VideoCapture(self.source)
        except Exception as e:
            print(f"Erro ao abrir a câmera: {e}")
            self.cap = None

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Erro ao capturar a imagem")
            return None

        if frame is None:
            print("Erro ao capturar frame da câmera.")
            return None

        return frame

    def release(self):
        self.cap.release()

    def restart(self):
        self.cap.release()
        self.cap = cv2.VideoCapture(self.source)

    def is_opened(self):
        return self.cap.isOpened()

    def get_shape(self):
        if self.cap is None:
            return None
        return int(self.cap.get(3)), int(self.cap.get(4))
