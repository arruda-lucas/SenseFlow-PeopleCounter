import cv2

def draw_ui(frame, counter, line):
    cv2.line(frame, line.start, line.end, (0, 255, 255), 2)
    cv2.putText(frame, f"Entradas: {counter.count_in}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Saídas: {counter.count_out}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    return frame

def annotate_bbox(tracks, frame, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        x1, y1, x2, y2 = track.to_ltrb()
        p1 = (int(x1), int(y1))
        p2 = (int(x2), int(y2))

        cv2.rectangle(
            frame,
            p1,
            p2,
            color=(int(colors[0][0]), int(colors[0][1]), int(colors[0][2])),
            thickness=2,
        )
        cv2.putText(
            frame,
            f"ID: {track_id}",
            (p1[0], p1[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
            lineType=cv2.LINE_AA,
        )
        
    return frame