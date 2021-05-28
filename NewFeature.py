import numpy as np
from DirectionIndicator import DirectionIndicator


def get_len(p1, p2):
    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    return np.sqrt((x ** 2) + (y ** 2))


class NewFeature:
    def __init__(self, actions, gravity_point, speed, r_sin, r_offset,origin_point=np.array([0, 0])):
        self.actions = actions
        self.gravity_point = gravity_point
        self.speed = speed
        self.r_sin = r_sin
        self.r_offset = r_offset
        self.loc_X = [origin_point[0]]
        self.loc_Z = [origin_point[1]]
        self.initial_distance = get_len(origin_point, gravity_point)
        self.get_pos(1, '1')
        self.indicator = DirectionIndicator(gravity_point)
        self.centre_directions = []
        self.distance = []
        for i in range(2, 2+len(self.actions)):
            self.get_pos(i, self.actions[i-2])
            pos = np.array([self.loc_X[i-1], self.loc_Z[i-1]])
            distance_to_g = get_len(pos, gravity_point)
            b = distance_to_g/self.initial_distance
            if b > 1.0:
                b = 1.0
            self.distance.append(b)
            a = self.indicator.get_direction(pos)
            if a == 'left':
                self.centre_directions.append(0)
            elif a == 'right':
                self.centre_directions.append(1)
            else:
                self.centre_directions.append(0.5)
            self.indicator.update_pre_point(pos)

    def get_pos(self, count, action):
        if action == "right":  # right
            self.r_sin -= self.r_offset
        elif action == "left":
            self.r_sin += self.r_offset
        loc_x = self.loc_X[count-1]
        loc_z = self.loc_Z[count-1]
        loc_x += np.sin(self.r_sin) * self.speed
        loc_z += np.cos(self.r_sin) * self.speed
        self.loc_X.append(loc_x)
        self.loc_Z.append(loc_z)

