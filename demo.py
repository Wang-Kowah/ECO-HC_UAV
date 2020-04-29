import time

import cv2
import numpy as np

from eco import ECOTracker

selecting = False
initializing = False
tracking = False
ix, iy, lx, ly = -1, -1, -1, -1
w, h = 0, 0
duration = 0.01


# mouse callback function
def draw_bbox(event, x, y, flag, params):
    global selecting, initializing, tracking, ix, iy, lx, ly, w, h

    if event == cv2.EVENT_LBUTTONDOWN:
        selecting = True
        tracking = False
        ix, iy = x, y
        lx, ly = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        lx, ly = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        selecting = False
        if abs(x - ix) > 10 and abs(y - iy) > 10:
            w, h = abs(x - ix), abs(y - iy)
            ix, iy = min(x, ix), min(y, iy)
            initializing = True
        else:
            tracking = False
    elif event == cv2.EVENT_RBUTTONDOWN:
        tracking = False
        if w > 0:
            ix, iy = int(x - w / 2), int(y - h / 2)
            initializing = True


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    # 获取摄像头的宽高，如果修改的话摄像头参数会被永久修改
    width = int(cap.get(3))  # CV_CAP_PROP_FRAME_WIDTH
    height = int(cap.get(4))  # CV_CAP_PROP_FRAME_HEIGHT

    cv2.namedWindow('tracking')
    cv2.setMouseCallback('tracking', draw_bbox)

    # init tracker
    tracker = ECOTracker()
    # visualise score(will run slower)
    vis = False
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if selecting:
            cv2.rectangle(frame, (ix, iy), (lx, ly), (0, 255, 255), 1)
        elif initializing:
            cv2.rectangle(frame, (ix, iy), (ix + w, iy + h), (0, 255, 255), 2)

            bbox = [ix, iy, w, h]
            tracker.init(frame, bbox)

            initializing = False
            tracking = True
        elif tracking:
            t0 = time.time()
            bbox = tracker.update(frame, True, vis)
            t1 = time.time()

            bbox = list(map(int, bbox))
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            print(str(w) + '\t' + str(h) + '\t' + str(w / 2 + bbox[0] - width / 2) + '\t'
                  + str(h / 2 + bbox[1] - height / 2))
            frame = cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 255), 1)

            # show score map
            if vis:
                score = tracker.score
                size = tuple(tracker.crop_size.astype(np.int32))
                score = cv2.resize(score, size)
                score -= score.min()
                score /= score.max()
                score = (score * 255).astype(np.uint8)
                # score = 255 - score
                score = cv2.applyColorMap(score, cv2.COLORMAP_JET)
                pos = tracker._pos
                pos = (int(pos[0]), int(pos[1]))
                xmin = pos[1] - size[1] // 2
                xmax = pos[1] + size[1] // 2 + size[1] % 2
                ymin = pos[0] - size[0] // 2
                ymax = pos[0] + size[0] // 2 + size[0] % 2
                left = abs(xmin) if xmin < 0 else 0
                xmin = 0 if xmin < 0 else xmin
                right = width - xmax
                xmax = width if right < 0 else xmax
                right = size[1] + right if right < 0 else size[1]
                top = abs(ymin) if ymin < 0 else 0
                ymin = 0 if ymin < 0 else ymin
                down = height - ymax
                ymax = height if down < 0 else ymax
                down = size[0] + down if down < 0 else size[0]
                score = score[top:down, left:right]
                crop_img = frame[ymin:ymax, xmin:xmax]
                score_map = cv2.addWeighted(crop_img, 0.6, score, 0.4, 0)
                frame[ymin:ymax, xmin:xmax] = score_map

            # show FPS
            duration = 0.8 * duration + 0.2 * (t1 - t0)
            cv2.putText(frame, 'FPS: ' + str(1 / duration)[:4].strip('.'), (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 2)

        cv2.imshow('tracking', frame)
        # Esc的ASCII码为27, 0xFF可以防止某些系统出bug
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
