import numpy as np


class DirectionIndicator:
    def __init__(self, gravity_point, origin_point=np.array([0, 0])):
        self.gravity_point = gravity_point
        self.origin_point = origin_point
        self.pre_point = origin_point
        self.pre_action = 'forward'
        self.threshold = 0.01

    def __str__(self):
        return '[gravity_point:%s,%s]' % self.gravity_point  # 可视化object

    def update_pre_point(self, point):
        self.pre_point = point

    def set_threshold(self, threshold):
        self.threshold = threshold

    def get_direction(self, pos):
        # print('pre pos = ', self.pre_point)
        # print('now pos = ', pos)
        # print('gravity_point= ', self.gravity_point)
        a1 = pos - self.pre_point
        b1 = self.gravity_point - pos
        a2 = a1 / np.linalg.norm(a1)
        b2 = b1 / np.linalg.norm(b1)
        loc_cross = np.cross(b2, a2)
        # print('loc_corss: ', loc_cross)

        centre_direction = "forward"
        if loc_cross > self.threshold:
            centre_direction = "left"
        elif loc_cross < -self.threshold:
            centre_direction = "right"
        else:
            # print(sum(a2/b2))
            if sum(a2/b2) < 0:
                centre_direction = 'left'
                if np.random.rand(1)[0] >= 0.5:
                    centre_direction = 'right'
                if self.pre_action == centre_direction:
                    if centre_direction == 'right':
                        centre_direction = 'left'
                    else:
                        centre_direction = 'right'
        self.pre_action = centre_direction
        # print(centre_direction)
        return centre_direction
