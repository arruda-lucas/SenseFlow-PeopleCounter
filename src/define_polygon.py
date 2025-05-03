import cv2
import json
import numpy as np

# Configurações
config = json.load(open("config/config.json"))
video_path = config["local"]

class ROI_PolygonDrawer:
    def __init__(self):
        self.polygon_points = []
        self.roi_points = []
        self.current_frame = None
        self.drawing_polygon = False
        self.drawing_roi = False
        self.mode = "polygon"
        self.instructions = [
            "TAB: Alternar modos (ROI/Poligonal)",
            "Poligonal: Clique+arraste para criar segmentos",
            "ROI: Clique para adicionar pontos, ENTER para finalizar",
            "BACKSPACE: Remover último ponto",
            "c: Limpar tudo | s: Salvar | q: Sair"
        ]
        self.load_config()

    def load_config(self):
        """Carrega configuração existente"""
        self.polygon_points = []
        self.roi_points = config.get("roi", [])

    def save_config(self):
        """Salva ambas as configurações no arquivo"""
        try:
            with open("config/config.json", "r+") as f:
                config["polyline"] = [
                    {"start": list(start), "end": list(end)}
                    for start, end in self.polygon_points
                    if end is not None
                ]
                config["roi"] = self.roi_points
                f.seek(0)
                json.dump(config, f, indent=4)
                f.truncate()
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")

    def click_event(self, event, x, y, flags, param):
        """Manipula eventos do mouse"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.mode == "polygon":
                if self.polygon_points and self.polygon_points[-1][1]:
                    start_point = self.polygon_points[-1][1]
                else:
                    start_point = (x, y)

                self.polygon_points.append((start_point, None))
                self.drawing_polygon = True
                
            elif self.mode == "roi":
                if not self.drawing_roi:
                    self.roi_points = [(x, y)]
                    self.drawing_roi = True
                else:
                    self.roi_points.append((x, y))

            self.redraw()

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing_polygon and self.polygon_points:
                self.polygon_points[-1] = (self.polygon_points[-1][0], (x, y))
                self.redraw()
                
            elif self.drawing_roi and self.roi_points:
                self.redraw()

        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing_polygon:
                self.drawing_polygon = False
                if self.polygon_points[-1][1]:
                    print(f"Segmento adicionado: {self.polygon_points[-1]}")
                    
            elif self.drawing_roi:
                pass
                
            self.redraw()

    def draw_instructions(self, frame):
        """Desenha as instruções na imagem"""
        y_offset = 30
        for i, instruction in enumerate(self.instructions):
            cv2.putText(frame, instruction, (10, y_offset + i*25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, instruction, (10, y_offset + i*25), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    def redraw(self):
        """Redesenha o frame com todas as marcações"""
        frame = self.current_frame.copy()

        # Desenha a ROI
        if self.roi_points:
            if len(self.roi_points) > 1:
                if self.drawing_roi:
                    temp_points = self.roi_points.copy()
                    cv2.polylines(frame, [np.array(temp_points)], False, (255, 0, 0), 1)
                else:
                    cv2.polylines(frame, [np.array(self.roi_points)], True, (255, 0, 0), 2)
            
            for point in self.roi_points:
                cv2.circle(frame, point, 5, (255, 0, 0), -1)

        # Desenha a poligonal
        for i, (start, end) in enumerate(self.polygon_points):
            if end:
                cv2.line(frame, start, end, (0, 255, 0), 2)
                cv2.circle(frame, start, 5, (0, 0, 255), -1)
                cv2.circle(frame, end, 5, (0, 0, 255), -1)

        if self.drawing_polygon and self.polygon_points and len(self.polygon_points[-1]) == 2:
            start, end = self.polygon_points[-1]
            if end:
                cv2.line(frame, start, end, (0, 255, 255), 1)
                cv2.circle(frame, start, 5, (0, 0, 255), -1)
                cv2.circle(frame, end, 5, (0, 255, 255), -1)

        # Mostra modo atual
        mode_text = f"Modo: {'ROI (azul)' if self.mode == 'roi' else 'Poligonal (verde)'}"
        cv2.putText(frame, mode_text, (10, frame.shape[0] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, mode_text, (10, frame.shape[0] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

        # Adiciona instruções
        self.draw_instructions(frame)

        cv2.imshow("Definir ROI e Poligonal", frame)

    def run(self):
        """Executa a aplicação principal"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Erro ao abrir o vídeo")
            return

        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar frame")
            cap.release()
            return

        self.current_frame = frame
        cv2.namedWindow("Definir ROI e Poligonal")
        cv2.setMouseCallback("Definir ROI e Poligonal", self.click_event)

        self.redraw()

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("c"):
                if self.mode == "polygon":
                    self.polygon_points = []
                else:
                    self.roi_points = []
                self.redraw()
            elif key == ord("s"):
                self.save_config()
                # Feedback visual que foi salvo
                self.current_frame = cv2.putText(
                    self.current_frame, "Configuração salva!", 
                    (self.current_frame.shape[1]//2 - 100, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
                )
                self.redraw()
                cv2.waitKey(1000)  # Mostra por 1 segundo
                ret, self.current_frame = cap.read()  # Recupera o frame original
                if not ret: 
                    break
            elif key == 9:  # TAB
                self.mode = "roi" if self.mode == "polygon" else "polygon"
                self.redraw()
            elif key == 13:  # ENTER
                if self.mode == "roi" and len(self.roi_points) > 2:
                    self.drawing_roi = False
                    self.redraw()
            elif key == 8:  # BACKSPACE
                if self.mode == "roi" and self.roi_points:
                    self.roi_points.pop()
                    self.redraw()

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    drawer = ROI_PolygonDrawer()
    drawer.run()