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

def produto_vetorial(start, end, point):
    x2, y2 = start
    x3, y3 = end
    x1, y1 = point

    return (x3 - x2) * (y1 - y2) - (y3 - y2) * (x1 - x2)
