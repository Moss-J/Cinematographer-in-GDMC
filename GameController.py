import threading
import time
from PlayerMovementHandler import PlayerMovementHandler
import WindowCapturer
import numpy as np


def get_len(p1, p2):
    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    return np.sqrt((x ** 2) + (y ** 2))


class Controller(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self._running = True
        self.command_in_progress = False
        self.moving_flag = False
        self.steering_flag = False
        self.player_handler = PlayerMovementHandler()
        self.p_angle = None
        self.p_pos = None
        self.t_angle = None
        self.t_pos = None
        self.speed = 20


    def update_player_info(self):
        p_info = self.player_handler.get_player_info()
        self.p_angle = p_info['YAW']
        self.p_pos = [p_info['X'], p_info['Y'], p_info['Z']]

        # print(self.p_pos, self.p_angle)

    def get_max_height(self, target_pos):
        return self.player_handler.get_max_height(target_pos)

    def move_to_target_pos(self, target_pos, speed):
        self.t_pos = target_pos
        self.speed = speed
        self.moving_flag = True
        self.command_in_progress = True

    def add_angle(self, angle):
        self.t_angle = self.p_angle + angle
        self.steering_flag = True
        self.command_in_progress = True

    def stop(self):
        self._running = False

    def run(self):
        print("start：" + self.name)
        self.update_player_info()
        print(self.p_pos, self.p_angle)
        while self._running:
            time.sleep(0.017)
            if self.command_in_progress:
                if self.steering_flag:
                    self.player_handler.steer_player_rotation(self.t_angle)
                    while not self.player_handler.player_reached_rotation(self.t_angle):
                        pass
                    self.update_player_info()
                    self.steering_flag = False

                if self.moving_flag:
                    one_time_flag = True
                    if self.p_pos[1] < self.t_pos[1]:
                        t_pos_y = [self.p_pos[0], float(self.t_pos[1]), self.p_pos[2]]
                        self.player_handler.move_player(t_pos_y, int(self.t_pos[1] - self.p_pos[1]))
                        while not self.player_handler.player_reached_pos(t_pos_y):
                            pass
                        self.update_player_info()

                    t_pos_xz = [float(self.t_pos[0]), self.p_pos[1], float(self.t_pos[2])]
                    self.player_handler.move_player(t_pos_xz, self.speed)
                    while not self.player_handler.player_reached_pos(t_pos_xz):
                        self.update_player_info()
                        if (get_len([self.p_pos[0], self.p_pos[2]], [t_pos_xz[0], t_pos_xz[2]])/self.speed) <= 0.2:
                            if one_time_flag:
                                WindowCapturer.set_prvs_flag(True)
                                one_time_flag = False
                    self.update_player_info()
                    WindowCapturer.set_next_flag(True)

                    if self.p_pos[1] > self.t_pos[1]:
                        t_pos_y = [self.p_pos[0], float(self.t_pos[1]), self.p_pos[2]]
                        self.player_handler.move_player(t_pos_y, int(self.p_pos[1] - self.t_pos[1]))
                        while not self.player_handler.player_reached_pos(t_pos_y):
                            pass
                        self.update_player_info()
                self.command_in_progress = False

        print("stop：" + self.name)
