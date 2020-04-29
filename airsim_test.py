import airsim
import cv2
import numpy as np

if __name__ == '__main__':
    # init airsim
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    # client.takeoffAsync().join()

    while True:
        imgs = client.simGetImages([
            airsim.ImageRequest(0, airsim.ImageType.Scene, False, False),
            # airsim.ImageRequest(0, airsim.ImageType.DepthPlanner, True, False),
            # airsim.ImageRequest(0, airsim.ImageType.DepthPerspective, True, False),
            airsim.ImageRequest(0, airsim.ImageType.DepthVis, True, False)
            # airsim.ImageRequest(0, airsim.ImageType.Segmentation, False, False)
        ])
        img = imgs[0]
        img1d = np.frombuffer(img.image_data_uint8, np.uint8)
        img_rgb = img1d.reshape(img.height, img.width, 3)
        cv2.imshow('Scene', img_rgb)
        img = imgs[1]
        # if img.pixels_as_float == 0.0:
        #     img1d = np.frombuffer(img.image_data_uint8, np.uint8)
        #     img2d = img1d.reshape(img.height, img.width, 3)
        # else:
        #     data_float = list(map(lambda x: x / 50, img.image_data_float))
        #     img2d = airsim.list_to_2d_float_array(data_float, img.width, img.height)
        # cv2.imshow('DepthPlanner', img2d)
        # img = imgs[2]
        # data_float = list(map(lambda x: x / 50, img.image_data_float))
        # img2d = airsim.list_to_2d_float_array(data_float, img.width, img.height)
        # cv2.imshow('DepthPerspective', img2d)
        # img = imgs[3]
        img1d = airsim.list_to_2d_float_array(img.image_data_float, img.width, img.height)
        cv2.imshow('DepthVis', img1d)
        # img = imgs[4]
        # img1d = np.frombuffer(img.image_data_uint8, dtype=np.uint8)
        # img_rgb = img1d.reshape(img.height, img.width, 3)
        # cv2.imshow('Segmentation', img_rgb)

        # Esc的ASCII码为27, 0xFF可以防止某些系统出bug
        if cv2.waitKey(1) & 0xFF == 27:
            break

    client.simPause(True)
    client.enableApiControl(False)
    client.armDisarm(False)
    cv2.destroyAllWindows()
