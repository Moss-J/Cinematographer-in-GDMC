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


def get_accuracy(predicted, label):
    l = len(label)
    count = 0
    for i in range(l):
        if predicted[i] == label[i]:
            count += 1
    return count / l


# def normalization(x):
#     x = (x - x.mean()) / x.std()
#     return x.round(2)
#     # return x

# def normalization(x):
#     x = x / x.sum()
#     return x


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
# for index, row in df.iteritems():
#     if index != "action":
#         df[index] = normalization(df[index])
long = 1.0 / 3 * 2
medium = 1.0 / 3

data_set_long_distance = []
data_set_medium_distance = []
data_set_short_distance = []

for d in data_set:
    data_set_long_distance.append(d.loc[d['distance'] >= long])
    data_set_medium_distance.append(d.loc[(d['distance'] >= medium) & (d['distance'] < long)])
    data_set_short_distance.append(d.loc[d['distance'] < medium])

# fig = plt.figure()  # 生成画布
# ax = fig.add_subplot(111)
# ax.invert_yaxis()
# ax.scatter(g_point[0], g_point[1], c='b', marker='o')
# ax.scatter(new_features.loc_X, new_features.loc_Z, c='r', marker='o')
# plt.show()
# for index, row in df.iterrows():
#     df.loc[index, features_H] = normalization(row[features_H])
#     df.loc[index, features_S] = normalization(row[features_S])

# df.to_excel("./test.xls", encoding="utf_8_sig", header=None)
features_new = list(data_1.columns[:2])
features_H = list(data_1.columns[2:5])
features_S = list(data_1.columns[5:8])
features_All = list(data_1.columns[:8])

print('re_H use features:', features_H)
print('re_S use features:', features_S)
print('re_All use features:', features_All)
print('re_new_F use features:', features_new)

# c_type = 'gini'
# c_type = 'entropy'

data_set_g_distance = data_set_long_distance
# data_set_g_distance = data_set_medium_distance
# data_set_g_distance = data_set_short_distance
# for distance_group_name in ['中距离']:
for distance_group_name in ['short_d', 'middle_d', 'long_d']:
    if distance_group_name == 'long_d':
        data_set_g_distance = data_set_long_distance
    elif distance_group_name == 'middle_d':
        data_set_g_distance = data_set_medium_distance
    else:
        data_set_g_distance = data_set_short_distance

    for c_type in ['gini', 'entropy']:
        print('use ', c_type, 'as criterion')
        print('on ', distance_group_name)
        mean_H_r = []
        mean_S_r = []
        mean_All_r = []
        mean_new_f_r = []
        for r in range(1, 101):
            # print(r)
            mean_H = []
            mean_S = []
            mean_All = []
            mean_new_f = []
            for dp in range(1, 31):
                accuracy_H = []
                accuracy_S = []
                accuracy_All = []
                accuracy_new_f = []
                scores = [accuracy_H, accuracy_S, accuracy_All, accuracy_new_f]
                for i in range(data_set_n):
                    test_data = data_set_g_distance[0]
                    training_data = data_set_g_distance[2]
                    # print(i)
                    if i == 1:
                        continue
                    if i == 2:
                        test_data = data_set_g_distance[2]
                        training_data = data_set_g_distance[0]

                    clf_H = tree.DecisionTreeClassifier(criterion=c_type, max_depth=dp, class_weight='balanced',
                                                        random_state=r)
                    clf_H.fit(training_data[features_H], training_data.action)
                    predicted = clf_H.predict(test_data[features_H])
                    scores[0].append(get_accuracy(predicted, test_data.action.values))

                    clf_S = tree.DecisionTreeClassifier(criterion=c_type, max_depth=dp, class_weight='balanced',
                                                        random_state=r)
                    clf_S.fit(training_data[features_S], training_data.action)
                    predicted = clf_S.predict(test_data[features_S])
                    scores[1].append(get_accuracy(predicted, test_data.action.values))

                    clf_All = tree.DecisionTreeClassifier(criterion=c_type, max_depth=dp, class_weight='balanced',
                                                          random_state=r)
                    clf_All.fit(training_data[features_All], training_data.action)
                    predicted = clf_All.predict(test_data[features_All])
                    scores[2].append(get_accuracy(predicted, test_data.action.values))

                    clf_All = tree.DecisionTreeClassifier(criterion=c_type, max_depth=dp, class_weight='balanced',
                                                          random_state=r)
                    clf_All.fit(training_data[features_new], training_data.action)
                    predicted = clf_All.predict(test_data[features_new])
                    scores[3].append(get_accuracy(predicted, test_data.action.values))

                A = np.array(scores[0])
                mean_H.append(A.mean())
                A = np.array(scores[1])
                mean_S.append(A.mean())
                A = np.array(scores[2])
                mean_All.append(A.mean())
                A = np.array(scores[3])
                mean_new_f.append(A.mean())
            # print("mean_H:\n")
            # for o in mean_H:
            #     print(o)
            # print("mean_S:\n")
            # for o in mean_S:
            #     print(o)
            # print("mean_All:\n")
            # for o in mean_All:
            #     print(o)
            # print("mean_new_f:\n")
            # for o in mean_new_f:
            #     print(o)
            mean_H_r.append(mean_H)
            mean_S_r.append(mean_S)
            mean_All_r.append(mean_All)
            mean_new_f_r.append(mean_new_f)

        final_re_H = []
        for i in range(30):
            sum = 0
            for j in range(100):
                sum += mean_H_r[j][i]
            final_re_H.append(sum / 100)
        print('re_H:')
        for o in final_re_H:
            print(o)

        final_re_S = []
        for i in range(30):
            sum = 0
            for j in range(100):
                sum += mean_S_r[j][i]
            final_re_S.append(sum / 100)
        print('re_S:')
        for o in final_re_S:
            print(o)

        final_re_All = []
        for i in range(30):
            sum = 0
            for j in range(100):
                sum += mean_All_r[j][i]
            final_re_All.append(sum / 100)
        print('re_All:')
        for o in final_re_All:
            print(o)

        final_re_new_f = []
        for i in range(30):
            sum = 0
            for j in range(100):
                sum += mean_new_f_r[j][i]
            final_re_new_f.append(sum / 100)
        print('re_new_F:')
        for o in final_re_new_f:
            print(o)


