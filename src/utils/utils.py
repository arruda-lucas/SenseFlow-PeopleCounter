import cv2


def convert_detections(results):
    raw_detections = []

    for i in results.boxes:
        coords = i.xyxy.cpu().numpy()[0]
        x1, y1, x2, y2 = coords
        w = x2 - x1
        h = y2 - y1
        conf = i.conf.cpu().numpy()[0]

        cls = "person"

        raw_detections.append(([x1, y1, w, h], conf, cls))

    return raw_detections


def annotate(tracks, frame, colors):
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


def produto_vetorial(start, end, point):
    x2, y2 = start
    x3, y3 = end
    x1, y1 = point

    return (x3 - x2) * (y1 - y2) - (y3 - y2) * (x1 - x2)
