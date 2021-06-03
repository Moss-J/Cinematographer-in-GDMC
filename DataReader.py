import pandas as pd
import numpy as np
from NewFeature import NewFeature


class DataReader:
    def __init__(self, player_name, num_of_data_sets=3, num_of_row=30):
        self.num_of_data_sets = num_of_data_sets
        self.num_of_row = num_of_row
        self.player_name = player_name
        self.max_opt = 0
        self.path = "data/" + player_name + "/Data_Set.xls"
        self.target_x = [-245.784687740458, -187.29806596758155, -221.62184328424001]
        self.target_z = [90.02881449401426, 42.56952920473027, 48.96858578599651]
        self.target_R = [69.88265252376814, 77.19521414720167, 77.54036814845725]
        if self.player_name == 'Player2':
            # print('data Liu_data')
            self.target_x = [-187.29806596758155, -221.62184328424001, -245.784687740458]
            self.target_z = [42.56952920473027, 48.96858578599651, 90.02881449401426]
            self.target_R = [77.19521414720167, 77.54036814845725, 69.88265252376814]
        elif self.player_name == 'Player3':
            # print('data Yu_data')
            self.target_x = [-221.62184328424001, -245.784687740458, -187.29806596758155]
            self.target_z = [48.96858578599651, 90.02881449401426, 42.56952920473027]
            self.target_R = [77.54036814845725, 69.88265252376814, 77.19521414720167]

        data_1 = pd.read_excel(self.path, sheet_name=0, nrows=self.num_of_row)
        data_2 = pd.read_excel(self.path, sheet_name=1, nrows=self.num_of_row)
        data_3 = pd.read_excel(self.path, sheet_name=2, nrows=self.num_of_row)
        self.data_set = [data_1, data_2, data_3]

        self.r_left = 30.0 * np.pi / 180
        self.r_right = 30.0 * np.pi / 180
        self.speed = 20.0

    def get_grouping_data(self):
        i = 0
        a = 0
        for one_data in self.data_set:
            b = max(max(one_data['O_left']), max(one_data['O_center']), max(one_data['O_right']))
            if a < b:
                a = b
        self.max_opt = a
        print('max value of optical flow: ', a)

        for one_data in self.data_set:
            g_point = np.array([self.target_x[i], self.target_z[i]])
            r_sin = ((360 - self.target_R[i]) * np.pi / 180)
            new_features = NewFeature(one_data.action.values, g_point, self.speed, r_sin, self.r_left)
            one_data.insert(0, "Dir", new_features.centre_directions, True)
            one_data.insert(0, "Dis", new_features.distance, True)
            one_data['H_left'] = one_data['H_left'] / 8
            one_data['H_center'] = one_data['H_center'] / 8
            one_data['H_right'] = one_data['H_right'] / 8

            one_data['O_left'] = one_data['O_left'] / a
            one_data['O_center'] = one_data['O_center'] / a
            one_data['O_right'] = one_data['O_right'] / a
            i += 1

        long = 1.0 / 3 * 2
        medium = 1.0 / 3

        data_set_long_distance = []
        data_set_medium_distance = []
        data_set_short_distance = []

        for d in self.data_set:
            data_set_long_distance.append(d.loc[d['Dis'] >= long])
            data_set_medium_distance.append(d.loc[(d['Dis'] >= medium) & (d['Dis'] < long)])
            data_set_short_distance.append(d.loc[d['Dis'] < medium])
        grouping_data = {'long': data_set_long_distance, 'medium': data_set_medium_distance,
                         'short': data_set_short_distance}
        return grouping_data

    def get_grouping_fts(self):
        features_dir_dis = list(self.data_set[0].columns[:2])
        features_col = list(self.data_set[0].columns[2:5])
        features_opt = list(self.data_set[0].columns[5:8])
        features_all = list(self.data_set[0].columns[:8])

        grouping_fts = {'features_dir_dis': features_dir_dis,
                        'features_col': features_col,
                        'features_opt': features_opt,
                        'features_all': features_all}
        return grouping_fts
