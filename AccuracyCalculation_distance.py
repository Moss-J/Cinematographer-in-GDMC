from sklearn import tree
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from NewFeature import NewFeature

player_num = input('input the Player num(1-3): ')

data_n = 30
data_set_n = 3

data_set_name = 'Player' + player_num
print(data_set_name)
path = "data/" + data_set_name + "/Data_Set.xls"

target_x = [-245.784687740458, -187.29806596758155, -221.62184328424001]
target_z = [90.02881449401426, 42.56952920473027, 48.96858578599651]
target_R = [69.88265252376814, 77.19521414720167, 77.54036814845725]
if data_set_name == 'Player2':
    # print('data Liu_data')
    target_x = [-187.29806596758155, -221.62184328424001, -245.784687740458]
    target_z = [42.56952920473027, 48.96858578599651, 90.02881449401426]
    target_R = [77.19521414720167, 77.54036814845725, 69.88265252376814]
elif data_set_name == 'Player3':
    # print('data Yu_data')
    target_x = [-221.62184328424001, -245.784687740458, -187.29806596758155]
    target_z = [48.96858578599651, 90.02881449401426, 42.56952920473027]
    target_R = [77.54036814845725, 69.88265252376814, 77.19521414720167]

r_left = 30.0 * np.pi / 180
r_right = 30.0 * np.pi / 180
speed = 20.0

# def normalization(x):
#     x = (x - x.mean()) / x.std()
#     return x.round(2)
#     # return x

# def normalization(x):
#     x = x / x.sum()
#     return x


def get_accuracy(predicted, label):
    l = len(label)
    count = 0
    for i in range(l):
        if predicted[i] == label[i]:
            count += 1
    return count / l


data_1 = pd.read_excel(path, sheet_name=0, nrows=data_n)
data_2 = pd.read_excel(path, sheet_name=1, nrows=data_n)
data_3 = pd.read_excel(path, sheet_name=2, nrows=data_n)
data_set = [data_1, data_2, data_3]
i = 0
a = 0
for one_data in data_set:
    b = max(max(one_data['S_left']), max(one_data['S_center']), max(one_data['S_right']))
    if a < b:
        a = b
print('max value of optical flow: ', a)

for one_data in data_set:
    g_point = np.array([target_x[i], target_z[i]])
    r_sin = ((360 - target_R[i]) * np.pi / 180)
    new_features = NewFeature(one_data.action.values, g_point, speed, r_sin, r_left)
    one_data.insert(0, "centre_directions", new_features.centre_directions, True)
    one_data.insert(0, "distance", new_features.distance, True)
    one_data['H_left'] = one_data['H_left'] / 8
    one_data['H_center'] = one_data['H_center'] / 8
    one_data['H_right'] = one_data['H_right'] / 8

    one_data['S_left'] = one_data['S_left'] / a
    one_data['S_center'] = one_data['S_center'] / a
    one_data['S_right'] = one_data['S_right'] / a
    i += 1


long = 1.0 / 3 * 2
medium = 1.0 / 3

data_set_long_distance = []
data_set_medium_distance = []
data_set_short_distance = []

for d in data_set:
    data_set_long_distance.append(d.loc[d['distance'] >= long])
    data_set_medium_distance.append(d.loc[(d['distance'] >= medium) & (d['distance'] < long)])
    data_set_short_distance.append(d.loc[d['distance'] < medium])

features_new = list(data_1.columns[:2])
features_H = list(data_1.columns[2:5])
features_S = list(data_1.columns[5:8])
features_All = list(data_1.columns[:8])


f_n = int(input('input distance type num you would like to use(0 short_d, 1 middle_d, 2 long_d): '))
distance_group_name = ['short_d', 'middle_d', 'long_d'][f_n]

if distance_group_name == 'long_d':
    data_set_g_distance = data_set_long_distance
elif distance_group_name == 'middle_d':
    data_set_g_distance = data_set_medium_distance
else:
    data_set_g_distance = data_set_short_distance


f_n = int(input('input the features num you would like to use(0 Entropy, 1 Optical Flow, 2 All, 3 centre directions & '
                'distance): '))
use_features = [features_H, features_S, features_All, features_new][f_n]

c_type = input('input criterion type(gini or entropy): ')
# c_type = 'entropy'
# c_type = 'gini'

dp = int(input('input max depth: '))
# dp = 30
# distance_group_name = '短距离'
# distance_group_name = '中距离'
# distance_group_name = '长距离'



print('use ', use_features, ' as features')
print('use ', c_type, 'as criterion')
print('with max depth:', dp)
print('on ', distance_group_name)

for i in range(3):
    print('--------------------------------------------')
    print('data :', i+1)
    test_data = data_set_g_distance[i]
    training_data = pd.concat([data_set_g_distance[0], data_set_g_distance[2]])

    score_list = []
    for r in range(1, 101):
        clf = tree.DecisionTreeClassifier(criterion=c_type, max_depth=dp, class_weight='balanced', random_state=r)
        clf.fit(training_data[use_features], training_data.action)
        predicted = clf.predict(test_data[use_features])
        score_list.append(get_accuracy(predicted, test_data.action.values))
    A = np.array(score_list)
    print('accuracy of DT:')
    print(A.mean())
    B = []
    for one in test_data['centre_directions']:
        if one == 0.5:
            B.append('forward')
        elif one == 0:
            B.append('left')
        elif one == 1:
            B.append('right')
    print('accuracy of centre directions:')
    print(get_accuracy(B, test_data.action.values))
