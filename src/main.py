from models.yolo_model import Yolov5m
from deep_sort_realtime.deepsort_tracker import DeepSort
from utils.utils import convert_detections
from utils.processing import PolylineCounter, PeopleCounter, PolylineConfig
from utils.annotate import draw_ui, annotate_bbox
from src.utils.buffer_manager import buffer_manager
import atexit
import numpy as np
import cv2
import json


def main():
    config = json.load(open("config/config.json"))
    polyline_segments = PolylineConfig.load_from_config(config)
    roi_points = config.get("roi", [])

    detection_interval = 3
    frame_counter = 0
    
    cap = cv2.VideoCapture(config["local"])
    model = Yolov5m()
    tracker = DeepSort(max_age=5)
    polyline_counter = PolylineCounter(polyline_segments, right=False)
    people_counter = PeopleCounter()

    tracks = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erro ao capturar a imagem")
                return None
            frame_counter = (frame_counter + 1) % detection_interval

            if frame_counter == 0:
                if roi_points:
                    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                    cv2.fillPoly(mask, [np.array(roi_points)], 255)
                    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
                    detections = convert_detections(model.detect(masked_frame))
                else:
                    detections = convert_detections(model.detect(frame))
                
                tracks = tracker.update_tracks(detections, frame=frame)

            # Filtra apenas tracks confirmados
            confirmed_tracks = [t for t in tracks if t.is_confirmed()]
            active_ids = {t.track_id for t in confirmed_tracks}

            for track in confirmed_tracks:
                bbox = track.to_ltrb()
                center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
                
                if direction := polyline_counter.check_crossing(track.track_id, center):
                    people_counter.update_count(direction)

            polyline_counter.cleanup_inactive_tracks(active_ids)

            for segment in polyline_segments:
                cv2.line(frame, segment[0], segment[1], (0, 255, 0), 2)

            if roi_points:
                cv2.polylines(frame, [np.array(roi_points)], True, (255, 0, 0), 1)
            
            if confirmed_tracks:
                frame = annotate_bbox(confirmed_tracks, frame)
        
            frame = draw_ui(frame, people_counter)

            cv2.imshow("People Counter", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        atexit.register(buffer_manager.shutdown)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()