import pandas as pd
from sklearn import tree
import time
import WindowCapturer
from GameController import Controller
import entropy
import keyboard
from sklearn import preprocessing
import numpy as np
from DirectionIndicator import DirectionIndicator
import DataReader as DR


def get_len(p1, p2):
    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    return np.sqrt((x ** 2) + (y ** 2))


data_n = 30
data_set_n = 3

map_num = int(input('input the map num(1 M1S8, 2 M1S1, 3 M1S3): '))
map_names = ["M1S8", "M1S1", "M1S3"]
map_name = map_names[map_num-1]
print(map_name)

player_num = input('input the Player num(1-3): ')
data_set_name = 'Player' + player_num
print(data_set_name)
path = "data/" + data_set_name + "/Data_Set.xls"

player_data = pd.read_excel(path, sheet_name=map_name, nrows=data_n)

action_type = int(input('input the action type(0 Player Decision, 1 Decision Tree Prediction, 2  Toward Center): '))

clfs = {}
player_1_fts = {'short': 'features_opt', 'medium': 'features_col', 'long': 'features_col'}
player_2_fts = {'short': 'features_col', 'medium': 'features_dir_dis', 'long': 'features_dir_dis'}
player_3_fts = {'short': 'features_col', 'medium': 'features_dir_dis', 'long': 'features_opt'}
player_fts = [player_1_fts, player_2_fts, player_3_fts]
dr = DR.DataReader(data_set_name)
grouping_data = dr.get_grouping_data()
grouping_fts = dr.get_grouping_fts()

if action_type == 1:
    print('Please confirm current map is the second map in player data ')

    for one_key in grouping_data.keys():
        training_data = pd.concat([grouping_data[one_key][0], grouping_data[one_key][2]])
        clf = tree.DecisionTreeClassifier(criterion='entropy', max_depth=30, class_weight='balanced', random_state=1)
        clf.fit(training_data[grouping_fts[player_fts[int(player_num)-1][one_key]]], training_data.action)
        clfs[one_key] = clf


target_x = [-221.62184328424001, -245.784687740458, -187.29806596758155][map_num - 1]
target_z = [48.96858578599651, 90.02881449401426, 42.56952920473027][map_num - 1]
target_R = [77.54036814845725, 69.88265252376814, 77.19521414720167][map_num - 1]

g_point = np.array([target_x, target_z])

indicator = DirectionIndicator(g_point)
indicator.set_threshold(0.1)


max_count = data_n
steer_angle = 30.0
r_left = steer_angle * np.pi/180
r_right = steer_angle * np.pi/180
r_sin = ((360-target_R)*np.pi/180)
loc_x = 0
loc_z = 0
speed = 20
count = 0
# map_name = input("name: ")

currentHeight = 98.0
nextHeight = currentHeight

max_dis_to_g_point = get_len(g_point, np.array([0, 0]))
if action_type == 1:
    print('distange to centre point', max_dis_to_g_point)


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
    print(count,  command,"---------------------------------")
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
time.sleep(1)
sr = WindowCapturer.WindowCapturer(0, 'sr', r'Minecraft 1.12.2')
sr.start()
cl = Controller(1, 'cl')
# cl.monitor_flag = False

data_set = np.zeros((max_count, 8), dtype=np.float)
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
            cl.start()
            time.sleep(1)
            target_pos = get_target_pos(command)
            cl.move_to_target_pos(target_pos, speed)
    else:
        h = calculate_entropy(sr.get_frame_bgr())
        for i in range(3):
            data_set[count - 1, i] = h[i]/8
        s = sum_flows(sr.flow_frames)
        for i in range(3, 6):
            data_set[count - 1, i] = s[i - 3]/dr.max_opt

        if action_type == 1:
            pos = np.array([loc_x, loc_z])
            dir_v = 0
            if command == 'forward':
                dir_v = 0.5
            elif command == 'right':
                dir_v = 1.0
            data_set[count - 1, 6] = dir_v
            dis_v = get_len(pos, g_point) / max_dis_to_g_point
            if dis_v > 1.0:
                dis_v = 1.0
            data_set[count - 1, 7] = dis_v
            dis_group_name = 'medium'
            if dis_v < 1/3:
                dis_group_name = 'short'
            if dis_v >= 2/3:
                dis_group_name = 'long'

            if dis_group_name == 'long':
                print('Dis: long, use Toward Centre')
                print('Toward Centre: ', command)
            else:
                column_names = ["H_left", "H_center", "H_right", "O_left", "O_center", "O_right", "Dir", "Dis"]
                df = pd.DataFrame(data_set, columns=column_names)
                print(df.loc[count - 1])
                print(dis_group_name)
                print(grouping_fts[player_fts[int(player_num) - 1][dis_group_name]])
                p = clfs[dis_group_name].predict(
                    df[grouping_fts[player_fts[int(player_num) - 1][dis_group_name]]])[count - 1]
                print('predicted:', p)
                command = p
        action_labels.append(command)
        if command == 'right':
            cl.add_angle(steer_angle)
        elif command == 'left':
            cl.add_angle(-steer_angle)
        target_pos = get_target_pos(command)
        cl.move_to_target_pos(target_pos, speed)


def replay_function(command):
    global count, max_count
    command_passer(command)
    while count <= max_count:
        time.sleep(0.2)
        if action_type == 0:
            command_passer(player_data.action.values[count-1])
        elif action_type == 1:
            if cl.command_in_progress:
                continue
            pos = np.array([loc_x, loc_z])
            command_passer(indicator.get_direction(pos))
            indicator.update_pre_point(pos)
        elif action_type == 2:
            if cl.command_in_progress:
                continue
            pos = np.array([loc_x, loc_z])
            command_passer(indicator.get_direction(pos))
            indicator.update_pre_point(pos)


keyboard.add_hotkey('enter', replay_function, args=["init"])
# keyboard.add_hotkey('up', command_passer, args=["forward"])
# keyboard.add_hotkey('right', command_passer, args=["right"])
# keyboard.add_hotkey('left', command_passer, args=["left"])
print('press enter to start')
keyboard.wait('esc')
sr.stop()
cl.stop()
# print(data_set)
column_names = ["H_left", "H_center", "H_right", "O_left", "O_center", "O_right", 'Dir', 'Dis']
df = pd.DataFrame(data_set, columns=column_names)
for i in range(max_count - len(action_labels)):
    action_labels.append('None')
# print(len(action_labels))
df['action'] = action_labels
# print(df)
df.to_excel('data/ ' + map_name + '_replay.xls', sheet_name=map_name)
print('saved to data/' + map_name + '_replay.xls')
