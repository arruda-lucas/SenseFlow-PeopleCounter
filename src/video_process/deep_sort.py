import cv2

from src.utils.utils import convert_detections, annotate, produto_vetorial

line_start = (1030, 252)
line_end = (764, 464)

count_in = 0
count_out = 0

track_history = {}  #pensar em uma forma melhor de armazenar os ids e os pontos
#perigoso acumular MUITO

cap = cv2.VideoCapture(video_path)

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# save_name = video_path.split(os.path.sep)[-1].split('.')[0]

while cap.isOpened():
    ret, frame = cap.read()

    # if ret:
    # resized_frame = cv2.resize(frame, (args.imgsz, args.imgsz)) if args.imgsz is not None else frame

    if not ret:
        break

    results = model(frame, classes=[0], verbose=False, conf=0.3)[0]

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

        # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        # cv2.putText(frame, f"ID {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # cv2.circle(frame, (center_x, center_y), 4, (0, 0, 255), -1)

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

    out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()
