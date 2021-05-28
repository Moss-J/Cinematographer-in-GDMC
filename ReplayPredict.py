import cv2
import mss
import threading
import time
import entropy
import mouse
import keyboard
import win32gui
import HeightAdjuster
from sklearn import tree
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from DirectionIndicator import DirectionIndicator


data_n = 30
data_set_n = 3
path = "D:/OpticalFlow/data/ito_new/ito.xls"


def normalization(x):
    x = (x - x.mean()) / x.std()
    return x.round(2)


def normalization_df(df_n):
    for index, row in df_n.iteritems():
        if index != "action":
            df_n[index] = normalization(df_n[index])


df = pd.concat(pd.read_excel(path, sheet_name=None, nrows=data_n))

features_H = list(df.columns[:3])
features_S = list(df.columns[3:6])
features_All = list(df.columns[:6])
all_columns = list(df.columns[:7])
dp = 7
c_type = 'gini'
i = 1
test_data = df.iloc[i * data_n: (i+1) * data_n, :]
training_data = pd.concat([df.iloc[0: i * data_n, :], df.iloc[(i+1) * data_n: data_n*data_set_n, :]])
normalization_df(training_data)


clf = tree.DecisionTreeClassifier(criterion=c_type, max_depth=dp, class_weight='balanced')
clf.fit(training_data[features_All], training_data.action)
impurity = clf.tree_.impurity

target_x = -187.29806596758155
target_z = 42.56952920473027
target_R = 77.19521414720167

# target_len = np.hypot(target_x, target_z)
r_left = 30.0*np.pi/180
r_right = 30.0*np.pi/180

# r_sin = np.arcsin(target_x/target_len)
r_sin = ((360-target_R)*np.pi/180)
loc_x = 0
loc_z = 0
old_x = 0
old_z = 0
speed = 21.74043673
Equal_centre = 0
# print(r_sin)

hwnd = win32gui.FindWindow(None, r'Minecraft 1.12.2')
win32gui.SetForegroundWindow(hwnd)
dimensions = win32gui.GetWindowRect(hwnd)
print(dimensions)
w = 720
h = 480
# plt.figure(figsize=(8, 6), dpi=80)
exitFlag = 0
prvs_frame = None
next_frame = None
frames = None
flows = None
flag = False
p_flag = False
Monitor_flag = False
monitor = {'top': dimensions[1]+31, 'left': dimensions[0]+8, 'width': w, 'height': h}
count = 0
user_mode = False
tree_mode = False
gravity_mode = False
mixture_mode = False
old_action = '0'

mode = input("mode: ")
# mode = "1"
if mode == '1':
    user_mode = True
elif mode == '2':
    tree_mode = True
elif mode == '3':
    gravity_mode = True
else:
    mixture_mode = True
# map_name = input("name: ")
map_name = "M1S3"
maxHeightMap_map = np.load(map_name + "_maxHeightMap.npy")
currentHeight = maxHeightMap_map[5, 5] + 10.0
nextHeight = currentHeight


def get_height(loc_x, loc_z):
    i = (loc_x + 300) // 60
    j = (loc_z + 300) // 60
    return maxHeightMap_map[int(i), int(j)] + 10


def update_s(data_s, x, y, z, u, v, w):
    data = data_s
    data.x.append(x)
    data.y.append(y)
    data.z.append(z)
    data.u.append(u)
    data.v.append(v)
    data.w.append(w)
    data.seek += 1


def get_pos(action):
    global loc_x, loc_z, r_sin, nextHeight, currentHeight, old_x, old_z, count, data
    if action == "right":  # right
        r_sin -= r_right
    elif action == "left":
        r_sin += r_left
    old_x = loc_x
    old_z = loc_z
    loc_x += np.sin(r_sin) * speed
    loc_z += np.cos(r_sin) * speed
    # update(o_x, currentHeight, o_z, loc_x - o_x, nextHeight - currentHeight, loc_z - o_z)
    print(count, "--------------------------------------------")
    print("x': %.2f" % loc_x, "z': %.2f" % loc_z)
    nextHeight = get_height(loc_x, loc_z)
    update_s(data, old_x, currentHeight, old_z, loc_x - old_x, nextHeight - currentHeight, loc_z - old_z)
    # print("currentHeight: ", currentHeight, "nextHeight", nextHeight)
    if nextHeight > currentHeight:
        HeightAdjuster.heightAdjuster(currentHeight, nextHeight)
        currentHeight = nextHeight


def get_len(p1, p2):
    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    return np.sqrt((x**2)+(y**2))


initial_distance = get_len([0, 0], [target_x, target_z])


gravity_point = np.array([target_x, target_z])
indicator = DirectionIndicator(gravity_point)


def tree_predict(count):
    global frames, flows, test_data, old_x, old_z, data_g, currentHeight, old_action
    if count > 29:
        time.sleep(10000)
    target = test_data.action.values[count]
    # 画面データ採取
    X = []
    for one in calculate_entropy(frames):
        X.append(float(one))
    for one in sum_flows(flows):
        X.append(float(one))
    X.append(test_data.action[count])
    realtime_test_df = test_data.copy()
    realtime_test_df.loc[-1] = X
    normalization_df(realtime_test_df)
    X = realtime_test_df[features_All][-1:]
    predicted = clf.predict(X)[0]
    node_indicator = clf.decision_path(X)
    leaf_id = clf.apply(X)
    sample_id = 0
    # obtain ids of the nodes `sample_id` goes through, i.e., row `sample_id`
    node_index = node_indicator.indices[node_indicator.indptr[sample_id]:
                                        node_indicator.indptr[sample_id + 1]]
    reliability = 0.0
    print_impurity = 0.0
    for node_id in node_index:
        if leaf_id[sample_id] == node_id:
            print_impurity = impurity[node_id]
            reliability = 1.0-(print_impurity/np.log2(3))
            continue

    # print("count: ", count)
    print('target: ', target)
    # print('reliability: %.2f' % reliability, ', impurity: %.2f' % print_impurity)
    pre_point = np.array([old_x, old_z])
    pos = np.array([loc_x, loc_z])

    indicator.update_pre_point(pre_point)
    if count >= 8:
        a1 = pos - pre_point
        b1 = gravity_point - pos
        a2 = a1 / np.linalg.norm(a1)
        b2 = b1 / np.linalg.norm(b1)
        update_s(data_g, loc_x, currentHeight, loc_z, a2[0], currentHeight, a2[1])
        update_s(data_g2, loc_x, currentHeight, loc_z, b2[0], currentHeight, b2[1])
        time.sleep(0.2)
    centre_direction = indicator.get_direction(pos)
    if user_mode:
        print('user_mode')
        # print('target: ', target)
        turnAroundAndSaveData(target)
        return
    if tree_mode:
        print('tree_mode, predicted: ', predicted)
        turnAroundAndSaveData(predicted)
    elif gravity_mode:
        print('gravity_mode')
        print('centre_direction: ', centre_direction)
        turnAroundAndSaveData(centre_direction)
    elif mixture_mode:
        print('mixture_mode')
        distance_of_gravity_centre = get_len([loc_x, loc_z], [target_x, target_z])
        probability = distance_of_gravity_centre/initial_distance
        print('probability of truning to gravity point: %.2f' % probability)
        com = predicted
        if np.random.rand(1)[0] <= probability:
            print('truning to gravity_mode')
            com = centre_direction
        else:
            print('truning to tree_mode')
            com = predicted
        print(com)
        turnAroundAndSaveData(com)


def get_frame():
    with mss.mss() as sct:
        frame = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
    return frame


def get_flows(prvs, next):
    hsv = np.zeros_like(prvs)
    hsv[..., 1] = 255
    prvs = cv2.cvtColor(prvs, cv2.COLOR_BGR2GRAY)
    next = cv2.cvtColor(next, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    f = [mag[:, 0:w // 3], mag[:, w // 3:2 * w // 3], mag[:, 2 * w // 3:w]]
    return f


class Monitor(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name

    def run(self):
        print("start：" + self.name)
        while True:
            if Monitor_flag:
                g = np.zeros_like(frames[0])
                g[..., 0] = cv2.normalize(flows[0], None, 0, 255, cv2.NORM_MINMAX)
                g[..., 1] = cv2.normalize(flows[1], None, 0, 255, cv2.NORM_MINMAX)
                g[..., 2] = cv2.normalize(flows[2], None, 0, 255, cv2.NORM_MINMAX)
                cv2.imshow('flow_v 0', g[..., 0])
                cv2.imshow('flow_v 1', g[..., 1])
                cv2.imshow('flow_v 2', g[..., 2])
                cv2.imshow('frame_v 0', frames[0])
                cv2.imshow('frame_v 1', frames[1])
                cv2.imshow('frame_v 2', frames[2])
                cv2.imshow('prvs_frame', prvs_frame)
                cv2.imshow('next_frame', next_frame)
                k = cv2.waitKey(30) & 0xff
                if k == 27:
                    break
            time.sleep(0.1)


class ScreenRecord(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name

    def run(self):
        global prvs_frame
        print("start：" + self.name)
        while 'Screen capturing':
            time.sleep(0.1)
            if p_flag:
                prvs_frame = get_frame()


def sum_flows(data):
    a = []
    for one in data:
        a.append(np.sum(one))
    return a


def calculate_entropy(data):
    a = []
    for one in data:
        a.append(calculate_avg_entropy(one))
    return a


def calculate_avg_entropy(data):
    a = entropy.calcEntropy(data[..., 0])
    b = entropy.calcEntropy(data[..., 1])
    c = entropy.calcEntropy(data[..., 2])
    return (a+b+c)/3


def turnAroundAndSaveData(command):
    global p_flag, flag, count, currentHeight, nextHeight, old_action
    if flag:
        return
    # db = dbm.open('count', 'c')
    # command = command[0]
    f0 = open("data/" + map_name + r"_Entropy.txt", 'a+')
    f1 = open("data/" + map_name + r"_Optical_Flow.txt", 'a+')
    f2 = open("data/" + map_name + r"_All.txt", 'a+')
    HeightAdjuster.heightAdjuster(currentHeight, nextHeight)
    currentHeight = nextHeight
    if command == "init":
        # db['n'] = str(count)
        get_pos("forward")
        flag = True
        p_flag = True
    elif command == "forward":
        for one in calculate_entropy(frames):
            f0.write(str(one) + ' ')
            f2.write(str(one) + ' ')
        for one in sum_flows(flows):
            f1.write(str(one) + ' ')
            f2.write(str(one) + ' ')
        f0.write("forward\n")
        f1.write("forward\n")
        f2.write("forward\n")
        count += 1
        # db['n'] = str(count)
        get_pos("forward")
        flag = True
        p_flag = True
    elif command == "right":
        for one in calculate_entropy(frames):
            f0.write(str(one) + ' ')
            f2.write(str(one) + ' ')
        for one in sum_flows(flows):
            f1.write(str(one) + ' ')
            f2.write(str(one) + ' ')
        f0.write("right\n")
        f1.write("right\n")
        f2.write("right\n")
        mouse.move(30, 0, absolute=False, duration=1)
        count += 1
        # db['n'] = str(count)
        get_pos("right")
        flag = True
        p_flag = True
    elif command == "left":
        for one in calculate_entropy(frames):
            f0.write(str(one) + ' ')
            f2.write(str(one) + ' ')
        for one in sum_flows(flows):
            f1.write(str(one) + ' ')
            f2.write(str(one) + ' ')
        f0.write("left\n")
        f1.write("left\n")
        f2.write("left\n")
        mouse.move(-30, 0, absolute=False, duration=1)
        count += 1
        # db['n'] = str(count)
        get_pos("left")
        flag = True
        p_flag = True
    f0.close()
    f1.close()
    f2.close()
    old_action = command
    # db.close()


    # print(nbtfile['Rotation'][0], "" ,nbtfile['Pos'][2])
    # time.sleep(10)

class Controller(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name

    def run(self):
        global flag, flows, frames, next_frame, Monitor_flag, p_flag
        while True:
            time.sleep(0.1)
            if flag:
                # db = dbm.open('count', 'c')
                # db['f'] = str('0')
                # db.close()
                keyboard.press('w')
                break
        while True:
            time.sleep(2)
            p_flag = False
            keyboard.release('w')
            time.sleep(1)
            next_frame = get_frame()
            flows = get_flows(prvs_frame, next_frame)
            frames = [next_frame[:, 0:w // 3], next_frame[:, w // 3:2 * w // 3], next_frame[:, 2 * w // 3:w]]
            # Monitor_flag = True
            flag = False
            # db = dbm.open('count', 'c')
            # db['f'] = str('1')
            # db.close()
            while True:
                if flag:
                    # db = dbm.open('count', 'c')
                    # db['f'] = str('0')
                    # db.close()
                    keyboard.press('w')
                    break
                tree_predict(count)
                time.sleep(0.1)


class MyDataClass:
    def __init__(self):
        self.x = [0]
        self.y = [0]
        self.z = [0]
        self.u = [0]
        self.v = [0]
        self.w = [0]
        self.seek = 0

    def print(self):
        print(self.seek,
              self.x[self.seek],
              self.y[self.seek],
              self.z[self.seek],
              self.u[self.seek],
              self.v[self.seek],
              self.w[self.seek],
              )


data = MyDataClass()
data_g = MyDataClass()
data_g2 = MyDataClass()

keyboard.add_hotkey('enter', turnAroundAndSaveData, args=["init"])
# keyboard.add_hotkey('up', turnAroundAndSaveData, args="forward")
# keyboard.add_hotkey('right', turnAroundAndSaveData, args="right")
# keyboard.add_hotkey('left', turnAroundAndSaveData, args="left")

sr = ScreenRecord(0, 'sr')
sr.start()
cl = Controller(1, 'cl')
cl.start()
# m = Monitor(2, 'm')
# m.start()

fig = plt.figure()  # 生成画布
ax = fig.add_subplot(111, projection='3d')
# ax = fig.add_subplot(111)
plt.ion()  # 打开交互模式
# ax.plot(target_x, 0, target_z)
# ax.scatter(target_x, currentHeight, target_z, c='r', marker='o')

# ax.set_zlabel('Z Label')
seek = 0
while True:
    ax.cla()
    ax.set_xlabel('X Label')
    ax.set_zlabel('Z Label')
    # ax.set_aspect(1)
    # ax.invert_xaxis()
    # ax.invert_yaxis()
    # ax.scatter(target_x, target_z, c='r', marker='o')
    # ax.quiver(data_g.x, data_g.z, data_g.u, data_g.w, color='y', alpha=.5)
    # ax.quiver(data_g2.x, data_g2.z, data_g2.u, data_g2.w, color='r', alpha=.5)
    # ax.quiver(data.x, data.z, data.u, data.w, alpha=.5)

    ax.scatter(target_x, 0, target_z, c='r', marker='o')
    ax.quiver(data_g.x, 0, data_g.z, data_g.u, 0, data_g.w, color='y', alpha=.5, length=10)
    ax.quiver(data_g2.x, 0, data_g2.z, data_g2.u, 0, data_g2.w, color='r', alpha=.5, length=10)
    ax.quiver(data.x, 0, data.z, data.u, 0, data.w, alpha=.5, length=1)
    # if data.seek != 0:
    #     ax.quiver(data.x[data.seek], data.z[data.seek], data.u[data.seek], data.w[data.seek], alpha=.5)
    #     # data.print()
    # if data_g.seek != 0:
    #     ax.quiver(data_g.x[data_g.seek], data_g.z[data_g.seek], data_g.u[data_g.seek], data_g.w[data_g.seek], color='y', alpha=.1)
    # if data_g2.seek != 0:
    #     ax.quiver(data_g2.x[data_g2.seek], data_g2.z[data_g2.seek], data_g2.u[data_g2.seek], data_g2.w[data_g2.seek], color='r',
    #               alpha=.1)
    # if data.seek == seek:
    #     fig.clf()
    #     seek += 1
    # data.print()
    # ax.quiver(data.x[data.seek], data.y[data.seek], data.z[data.seek], data.u[data.seek], data.v[data.seek],
    #           data.w[data.seek], length=1)
    #
    # ax.quiver(data_g.x[data_g.seek], data_g.y[data_g.seek], data_g.z[data_g.seek], data_g.u[data_g.seek],
    #           data_g.v[data_g.seek], data_g.w[data_g.seek], length=10, color='r')
    #
    # ax.quiver(data_g2.x[data_g2.seek], data_g2.y[data_g2.seek], data_g2.z[data_g2.seek], data_g2.u[data_g2.seek],
    #           data_g2.v[data_g2.seek], data_g2.w[data_g2.seek], length=10, color='y')

    plt.pause(0.1)

