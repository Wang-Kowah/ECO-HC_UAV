import math


def cal_z(x, y, d):
    print(x,y,d,d * d - x * x - y * y)
    return math.sqrt(d * d - x * x - y * y)


def cal_angle(x, y, z):
    projection_len = math.sqrt(x * x + y * y)
    angle_x = math.atan2(y, x) * 180 / math.pi
    angle_z = math.atan2(z, projection_len) * 180 / math.pi
    return angle_x, angle_z


def cal_yaw(y, z):
    yaw = math.atan2(z, y) * 180 / math.pi
    return yaw if y > 0 else yaw - 180


if __name__ == '__main__':
    # print(cal_angle(1, 1, 1.414))
    print(cal_yaw(-1, 1.733))
