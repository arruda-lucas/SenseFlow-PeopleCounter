from models.yolo_model import Yolov5m
from video_process.video_stream import VideoProcess
from deep_sort_realtime.deepsort_tracker import DeepSort
from utils.utils import convert_detections
from utils.processing import PolylineCounter, PeopleCounter, PolylineConfig
from utils.annotate import draw_ui, annotate_bbox
import cv2
import json
import numpy as np

def main():
    # Carrega configuração
    config = json.load(open("config/config.json"))
    polyline_segments = PolylineConfig.load_from_config(config)
    roi_points = config.get("roi", [])
    
    # Parâmetros de otimização
    detection_interval = 3  # Processa detecção a cada 3 frames
    frame_counter = 0
    
    # Inicializa objetos
    camera = VideoProcess(config["local"])
    model = Yolov5m()
    tracker = DeepSort(max_age=30)
    polyline_counter = PolylineCounter(polyline_segments, right=False)
    people_counter = PeopleCounter()

    try:
        while True:
            frame = camera.get_frame()
            frame_counter = (frame_counter + 1) % detection_interval  # Contador cíclico

            # Processamento de objetos com frame skipping e ROI
            if frame_counter == 0:
                if roi_points:
                    # Cria máscara para ROI
                    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                    cv2.fillPoly(mask, [np.array(roi_points)], 255)
                    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
                    detections = convert_detections(model.detect(masked_frame))
                else:
                    detections = convert_detections(model.detect(frame))
                
                tracks = tracker.update_tracks(detections, frame=frame)
            else:
                # Apenas atualiza as tracks sem nova detecção
                tracks = tracker.predict()

            active_ids = {t.track_id for t in tracks if t.is_confirmed()}

            # Verificação de cruzamentos
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                bbox = track.to_ltrb()
                center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
                
                if direction := polyline_counter.check_crossing(track.track_id, center):
                    people_counter.update_count(direction)

            # Limpeza de tracks inativos
            polyline_counter.cleanup_inactive_tracks(active_ids)
            
            # Visualização - Desenha elementos na tela
            # 1. Poligonal de contagem
            for segment in polyline_segments:
                cv2.line(frame, segment[0], segment[1], (0, 255, 0), 2)
            
            # 2. ROI (se existir)
            if roi_points:
                cv2.polylines(frame, [np.array(roi_points)], True, (255, 0, 0), 1)
            
            # 3. Bounding boxes e UI
            frame = draw_ui(
                annotate_bbox([t for t in tracks if t.is_confirmed()], frame),
                people_counter
            )

            # Mostra informações de otimização
            info_text = f"Frame skip: {detection_interval-1} | ROI: {'ON' if roi_points else 'OFF'}"
            cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

            cv2.imshow("People Counter (Optimized)", frame)
            
            # Controles por teclado
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):  # Toggle ROI display
                roi_points = [] if roi_points else config.get("roi", [])
            elif key == ord('+'):  # Aumenta intervalo de detecção
                detection_interval = min(detection_interval + 1, 10)
            elif key == ord('-'):  # Diminui intervalo de detecção
                detection_interval = max(detection_interval - 1, 1)

    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()