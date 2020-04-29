import airsim

if __name__ == '__main__':
    # init airsim
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    # client.takeoffAsync().join()
    client.moveByVelocityZAsync(0, 0, -10, 1).join()

    while True:
        try:
            s = input("vx,vy,z,yaw:")
            if s.startswith("/"):
                break
            ints = list(map(int, s.split(' ')))
            # client.moveByVelocityZAsync(ints[0], ints[1], ints[2], 1, 0, airsim.YawMode(False, ints[3])).join()
            client.moveByAngleZAsync(ints[0], ints[1], -10, ints[2], 1).join()
            # client.moveByRC(airsim.RCData(throttle=ints[2], yaw=ints[3], is_initialized=True,is_valid=True))
        except Exception as e:
            print(e)
            break

    # client.simPause(True)
    client.armDisarm(False)
    client.enableApiControl(False)
