from py4j.java_gateway import JavaGateway
import math

class PlayerMovementHandler:
    def __init__(self):
        self.gateway = JavaGateway()

    def get_player_info(self):
        player_info = {}
        p = self.gateway.getPlayerData()
        player_info['X'] = p[0]
        player_info['Y'] = p[1]
        player_info['Z'] = p[2]
        player_info['YAW'] = p[3]
        player_info['PITCH'] = p[4]
        return player_info

    def player_reached_pos(self, target_pos):
        realtime = self.get_player_info()
        if not math.isclose(realtime['X'], target_pos[0], rel_tol=0.001):
            return False
        if not math.isclose(realtime['Y'], target_pos[1], rel_tol=0.001):
            return False
        if not math.isclose(realtime['Z'], target_pos[2], rel_tol=0.001):
            return False
        return True

    def player_reached_rotation(self, target_angle):
        if target_angle >= 360.0:
            target_angle -= 360.0
        elif target_angle <= -360.0:
            target_angle += 360.0
        # print(target_angle)
        realtime = self.get_player_info()
        # print(realtime['YAW'])
        if not math.isclose(realtime['YAW'], target_angle, rel_tol=0.001):
            return False
        return True

    def get_max_height(self, target_pos):
        object_class = self.gateway.jvm.double
        java_array = self.gateway.new_array(object_class, len(target_pos))
        for n in range(len(target_pos)):
            java_array[n] = target_pos[n]
        return self.gateway.getMaxHeight(java_array)

    def move_player(self, target_pos, speed):
        object_class = self.gateway.jvm.double
        java_array = self.gateway.new_array(object_class, len(target_pos))
        for n in range(len(target_pos)):
            java_array[n] = target_pos[n]
        self.gateway.movePlayer(java_array, speed)

    def steer_player_rotation(self, t_angle):
        self.gateway.steerPlayerRotation(t_angle)


# a = PlayerMovementHandler()
# time.sleep(3)
# for i in range(1):
#     # mouse.move(1, 0, absolute=False)
#     # a.move('right')
#     # a.move('left')
#     # a.steer_player_rotation(-30.0)
#     # time.sleep(2)
#     pos = a.get_player_info()
#     print(pos)
#     pos2 = [pos['X'] + 30.0, pos['Y'], pos['Z'] + 30.0]
#     a.move_player(pos2)
#     time.sleep(2)
#     pos = a.get_player_info()
#     print(pos)
#     print(a.check_player_pos(pos2))
