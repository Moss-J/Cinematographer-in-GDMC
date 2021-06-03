import pandas as pd
import time
import WindowCapturer
from GameController import Controller
import entropy
import keyboard
from sklearn import preprocessing
import numpy as np

map_num = int(input('input the map num(0-2): '))
map_names = ["M1S8", "M1S1", "M1S3"]
target_R_3 = [77.54036814845725, 69.88265252376814, 77.19521414720167]
target_R = target_R_3[map_num]
steer_angle = 30.0
r_left = steer_angle * np.pi/180
r_right = steer_angle * np.pi/180
r_sin = ((360-target_R)*np.pi/180)
loc_x = 0
loc_z = 0
speed = 20
count = 0
# map_name = input("name: ")
map_name = map_names[map_num]
currentHeight = 98.0
nextHeight = currentHeight
max_count = 30


def sum_flows(data, isScale = False):
    a = []
    for one in data:
        a.append(np.sum(one))
    if isScale:
        a = preprocessing.scale(a)
    return a


def calculate_entropy(data, isScale = False):
    a = []
    for one in data:
        a.append(calculate_avg_entropy(one))
    if isScale:
        a = preprocessing.scale(a)
    return a


def calculate_avg_entropy(data):
    r = entropy.calcEntropy(data[..., 0])
    g = entropy.calcEntropy(data[..., 1])
    b = entropy.calcEntropy(data[..., 2])
    return (r+g+b)/3


def get_target_pos(command):
    global loc_x, loc_z, r_sin, nextHeight, currentHeight, count
    if command == "right":  #right
        r_sin -= r_right
    elif command == "left":
        r_sin += r_left
    loc_x += np.round(np.sin(r_sin) * speed, 1)
    loc_z += np.round(np.cos(r_sin) * speed, 1)
    print(count, "--------------------------------------------")
    t_pos = [loc_x, nextHeight, loc_z]
    nextHeight = float(cl.get_max_height(t_pos)) + 10.0
    print("x': %.1f" % loc_x, "y': %.1f" % nextHeight, "z': %.1f" % loc_z)
    t_pos[1] = nextHeight
    # print("currentHeight: ", currentHeight, "nextHeight", nextHeight)
    # if nextHeight > currentHeight:
    #     HeightAdjuster.heightAdjuster(currentHeight, nextHeight)
    currentHeight = nextHeight
    count += 1

    return t_pos


WindowCapturer.init_flags()
time.sleep(5)
sr = WindowCapturer.WindowCapturer(0, 'sr', r'Minecraft 1.12.2')
sr.start()
cl = Controller(1, 'cl')
# cl.monitor_flag = False
cl.start()
data_set = np.zeros((max_count, 6), dtype=np.float)
action_labels = []


def command_passer(command):
    global count, r_sin
    if count > max_count:
        return
    if cl.command_in_progress:
        return
    if command == "init":
        if count == 0:
            print('init')
            target_pos = get_target_pos(command)
            cl.move_to_target_pos(target_pos, speed)
    else:
        h = calculate_entropy(sr.get_frame_bgr())
        for i in range(3):
            data_set[count-1, i] = h[i]
        s = sum_flows(sr.flow_frames)
        for i in range(3, 6):
            data_set[count-1, i] = s[i - 3]

        action_labels.append(command)
        if command == 'right':
            cl.add_angle(steer_angle)
        elif command == 'left':
            cl.add_angle(-steer_angle)
        target_pos = get_target_pos(command)
        cl.move_to_target_pos(target_pos, speed)


keyboard.add_hotkey('enter', command_passer, args=["init"])
keyboard.add_hotkey('up', command_passer, args=["forward"])
keyboard.add_hotkey('right', command_passer, args=["right"])
keyboard.add_hotkey('left', command_passer, args=["left"])
print('press enter to start')
keyboard.wait('esc')
sr.stop()
cl.stop()
# print(data_set)
column_names = ["H_left", "H_center", "H_right", "O_left", "O_center", "O_right"]
df = pd.DataFrame(data_set, columns=column_names)
for i in range(max_count - len(action_labels)):
    action_labels.append('None')
# print(len(action_labels))
df['action'] = action_labels
# print(df)
df.to_excel('data/ ' + map_name + '.xls', sheet_name=map_name)
print('saved to data/' + map_name + '.xls')
