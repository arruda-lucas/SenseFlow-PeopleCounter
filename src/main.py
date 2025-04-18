from models.yolo_model import Yolov5m
from video_process.video_stream import VideoProcess
from deep_sort_realtime.deepsort_tracker import DeepSort
from utils.utils import convert_detections, annotate, produto_vetorial
import cv2
import json

with open("config/config.json", "r") as file:
    config = json.load(file)
assert config["url"] is not None, "URL não pode ser nulo."

camera = VideoProcess(config["url"])
model = Yolov5m()
tracker = DeepSort(max_age=30)

frame_width, frame_height = camera.get_shape()
line_start = (0, frame_height // 2)
line_end = (frame_width, frame_height // 2)

count_in = 0
count_out = 0
track_history = {}

while True:
    frame = camera.get_frame()

    results = model.detect(frame)

    detections = convert_detections(results)

    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        bbox = track.to_ltrb()
        x1, y1, x2, y2 = bbox
        # o point é dado pelo centro da bb
        center = ((x1 + x2) // 2, (y1 + y2) // 2)

        if track_id in track_history:
            # salva os centros antigos
            prev_center = track_history[track_id]

            prev_vet = produto_vetorial(line_start, line_end, prev_center)
            center_vet = produto_vetorial(line_start, line_end, center)

            if (
                prev_vet < 0
                and center_vet > 0
                and (line_start[1] < center[1] < line_end[1])
            ):
                count_in += 1
                print(f"Nova entrada. Total {count_in}")

            elif (
                prev_vet > 0
                and center_vet < 0
                and (line_start[1] < center[1] < line_end[1])
            ):
                count_out += 1
                print(f"Nova saída. Total {count_out}")

        track_history[track_id] = center

        frame = annotate(tracks, frame, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)])

    cv2.line(frame, (line_start), (line_end), (255, 0, 0), 2)

    cv2.putText(
        frame,
        f"Entradas: {count_in}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
    )
    cv2.putText(
        frame,
        f"Saídas: {count_out}",
        (50, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
    )

    cv2.imshow("Detected", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
