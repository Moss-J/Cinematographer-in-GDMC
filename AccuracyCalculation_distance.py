from sklearn import tree
import pandas as pd
import numpy as np
import DataReader as DR


def get_accuracy(predicted, label):
    l = len(label)
    count = 0
    for i in range(l):
        if predicted[i] == label[i]:
            count += 1
    return count / l


num_of_row = 30
num_of_data_sets = 3

player_num = input('input the Player num(1-3): ')
group_num_of_d = int(input('input distance type num you would like to use(0 short, 1 middle, 2 long): '))
group_num_of_ft = int(input('input the features num you would like to use(0 Col, 1 Opt, 2 All, 3 Dir & Dis): '))
# c_type =['gini', 'entropy'][int(input('input criterion type(0 gini, 1 entropy): '))]
c_type = ['gini', 'entropy'][1]
# dp = int(input('input max depth of tree(max 30): '))
dp = 30

p_name = 'Player' + player_num
print(p_name)

dr = DR.DataReader(p_name)
grouping_data = dr.get_grouping_data()
grouping_fts = dr.get_grouping_fts()

group_of_dis = grouping_data[['short', 'medium', 'long'][group_num_of_d]]
print('distance group: ' + ['short', 'medium', 'long'][group_num_of_d])
group_of_ft = grouping_fts[['features_col', 'features_opt', 'features_all', 'features_dir_dis'][group_num_of_ft]]
print('features group: ' + str(group_of_ft))
print('use ', c_type, 'as criterion', 'with max depth:', dp)

for i in range(1, 2):
    print('--------------------------------------------')
    print('data :', i+1)
    test_data = group_of_dis[i]
    training_data = pd.concat([group_of_dis[0], group_of_dis[2]])

    score_list = []
    for r in range(1, 101):
        clf = tree.DecisionTreeClassifier(criterion=c_type, max_depth=dp, class_weight='balanced', random_state=r)
        clf.fit(training_data[group_of_ft], training_data.action)
        predicted = clf.predict(test_data[group_of_ft])
        score_list.append(get_accuracy(predicted, test_data.action.values))
    A = np.array(score_list)
    print('accuracy of Decision Tree:')
    print(A.mean())
    B = []
    for one in test_data['Dir']:
        if one == 0.5:
            B.append('forward')
        elif one == 0:
            B.append('left')
        elif one == 1:
            B.append('right')
    print('accuracy of Toward Center:')
    print(get_accuracy(B, test_data.action.values))
