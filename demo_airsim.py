import time

import airsim
import cv2
import numpy as np

import angle
from eco import ECOTracker

selecting = False
initializing = False
tracking = False
ix, iy, lx, ly = -1, -1, -1, -1
w, h = 0, 0
duration = 0.01
# AirSim uses NED coordinates so negative axis is up.
# height means z, -10 is 10 meters above the original launch point.
height = -10
# yaw is the angle that camera face
pitch, yaw = 0, 0
distance = 0
vx, vy, tx, ty = 0, 0, 0, 0
countdown = 6


# mouse callback function
def draw_box(event, x, y, flag, params):
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
    cv2.namedWindow('tracking')
    cv2.setMouseCallback('tracking', draw_box)

    # save as video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    img_writer = cv2.VideoWriter('E:\\下载\\Airsim.avi', fourcc, 24, (256, 144))

    # init airsim
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    # client.takeoffAsync().join()
    client.simPause(False)
    client.moveByVelocityZAsync(vx, vy, height, 1, airsim.DrivetrainType.MaxDegreeOfFreedom,
                                airsim.YawMode(False, yaw)).join()

    # init tracker
    tracker = ECOTracker()
    while True:
        imgs = client.simGetImages([
            # uncompressed RGB array bytes
            airsim.ImageRequest(0, airsim.ImageType.Scene, False, False),
            # get depth from camera using a projection ray that hits that pixel
            airsim.ImageRequest(0, airsim.ImageType.DepthPerspective, True, False),
        ])
        img, depth = imgs[0], imgs[1]
        # get numpy array
        img1d = np.frombuffer(img.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        img_rgb = img1d.reshape(144, 256, 3)
        frame = img_rgb

        # # fit depth into [0, 255]
        # data_float = list(map(lambda x: x / 50, depth.image_data_float))
        # # convert float array to numpy 2D array
        # depth2d = airsim.list_to_2d_float_array(data_float, 256, 144)
        # cv2.imshow('DepthPerspective', depth2d)

        t0 = time.time()
        if selecting:
            cv2.rectangle(frame, (ix, iy), (lx, ly), (0, 255, 255), 1)
        elif initializing:
            cv2.rectangle(frame, (ix, iy), (ix + w, iy + h), (0, 255, 255), 2)

            bbox = [ix, iy, w, h]
            tracker.init(frame, bbox)

            initializing = False
            tracking = True
        elif tracking:
            bbox = tracker.update(frame, True, False)

            bbox = list(map(int, bbox))
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tx, ty = int(w / 2 + bbox[0]), int(h / 2 + bbox[1])
            # print(str(w) + '\t' + str(h) + '\t' + str(tx) + '\t' + str(ty))
            cv2.circle(frame, (tx, ty), 1, (0, 0, 255), 0)
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 255), 1)

            # state = client.getMultirotorState().kinematics_estimated
            # orientation = state.orientation
            # position = state.position

            countdown -= 1
            if countdown == 0:
                # make sure target in the center of view
                distance = depth.image_data_float[tx + ty * 256]
                # x,y here don't mean meters! Can't calculate directly
                # z = angle.cal_z(tx - 128, ty - 72, distance)
                # yaw += angle.cal_yaw(ty - 72, z)
                if distance > 40:
                    vx = 1
                elif distance < 20:
                    vx = -1
                else:
                    vx = 0
                if abs(tx - 128) < 16:
                    print('target in center x')
                    vy = 0
                else:
                    if tx > 160:
                        vy = 1
                    elif tx < 96:
                        vy = -1
                if abs(ty - 72) < 18:
                    print('target in center y')
                else:
                    if ty < 54 and height > 4:
                        height -= 1
                    elif ty > 90:
                        height += 1

                countdown = 3
                # client.moveToPositionAsync(tx, ty, height, -5, yaw_mode=airsim.YawMode(False, yaw)).join()
                client.moveByVelocityZAsync(vx, vy, height, 1, airsim.DrivetrainType.MaxDegreeOfFreedom,
                                            airsim.YawMode(False, yaw)).join()

        t1 = time.time()
        # show FPS
        duration = 0.8 * duration + 0.2 * (t1 - t0)
        cv2.putText(frame, 'FPS: ' + str(1 / duration)[:4].strip('.'), (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 255), 2)

        cv2.imshow('tracking', frame)
        img_writer.write(frame)
        # the ASCII code of ESC is 27, 0xFF can prevent bug on some system
        if cv2.waitKey(1) & 0xFF == 27:
            break

    client.simPause(True)
    client.armDisarm(False)
    client.enableApiControl(False)
    cv2.destroyAllWindows()
