from models.yolo_model import Yolov5m
from video_process.video_stream import VideoProcess
from deep_sort_realtime.deepsort_tracker import DeepSort
from utils.utils import convert_detections
from utils.processing import PolylineCounter, PeopleCounter, PolylineConfig
from utils.annotate import draw_ui, annotate_bbox
import cv2
import json

def main():
    # Carrega configuração
    config = json.load(open("config/config.json"))
    polyline_segments = PolylineConfig.load_from_config(config)
    
    # Inicializa objetos
    camera = VideoProcess(config["local"])
    model = Yolov5m()
    tracker = DeepSort(max_age=30)
    polyline_counter = PolylineCounter(polyline_segments, right=False)
    people_counter = PeopleCounter()

    try:
        while True:
            ret, frame = camera.get_frame()
            if not ret:
                break

            # Processamento de objetos
            detections = convert_detections(model.detect(frame))
            tracks = tracker.update_tracks(detections, frame=frame)
            active_ids = {t.track_id for t in tracks if t.is_confirmed()}

            # Verificação de cruzamentos
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                bbox = track.to_ltrb()
                center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
                
                if direction := polyline_counter.check_crossing(track.track_id, center):
                    people_counter.update_count(direction)

            # Limpeza e visualização
            polyline_counter.cleanup_inactive_tracks(active_ids)
            
            # Desenha a poligonal dinamicamente
            for segment in polyline_segments:
                cv2.line(frame, segment[0], segment[1], (0, 255, 0), 2)
            
            # Desenha UI
            frame = draw_ui(
                annotate_bbox([t for t in tracks if t.is_confirmed()], frame),
                people_counter
            )

            cv2.imshow("People Counter", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()