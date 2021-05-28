from pymclevel.player import nbt
import HeightMap
import numpy as np
import matplotlib.pyplot as plt
from functions import *
import math

displayName = "NBTEditor"


def normalization(data):
    sum = np.sum(data)
    return data / sum


def get_score(ids):
    dict = {}
    for key in ids:
        dict[key] = dict.get(key, 0) + 1
    score = 0
    for key in dict.keys():
        score += key * dict[key]
    return score


def perform(level, box, options):
    levelName = level.root_tag['Data']['LevelName'].value
    print(levelName)
    level.root_tag['Data']['DayTime'] = nbt.TAG_Long(6000)
    level.root_tag['Data']['clearWeatherTime'] = nbt.TAG_Int(1000)
    level.root_tag['Data']['raining'] = nbt.TAG_Byte(0)
    level.root_tag['Data']['thundering'] = nbt.TAG_Byte(0)
    level.root_tag['Data']['GameRules']['doDaylightCycle'] = nbt.TAG_String(u'false')
    level.root_tag['Data']['GameRules']['doWeatherCycle'] = nbt.TAG_String(u'false')
    level.root_tag['Data']['Player']['abilities']['flying'] = nbt.TAG_Byte(1)
    player_pos = [nbt.TAG_Double(0), nbt.TAG_Double(128), nbt.TAG_Double(0)]
    level.root_tag['Data']['Player']['Pos'] = player_pos

    min_z = 0
    while True:
        min_z -= 1
        y = 0
        for y in range(0, 256):
            if level.blockAt(0, y, min_z) != 0:
                break
        if y == 255:
            min_z += 1
            break

    max_z = 0
    while True:
        max_z += 1
        y = 0
        for y in range(0, 256):
            if level.blockAt(0, y, max_z) != 0:
                break
        if y == 255:
            max_z -= 1
            break

    min_x = 0
    while True:
        min_x -= 1
        y = 0
        for y in range(0, 256):
            if level.blockAt(min_x, y, 0) != 0:
                break
        if y == 255:
            min_x += 1
            break

    max_x = 0
    while True:
        max_x += 1
        y = 0
        for y in range(0, 256):
            if level.blockAt(max_x, y, 0) != 0:
                break
        if y == 255:
            max_x -= 1
            break




    if max_x == 0 or max_z == 0 or min_x == 0 or min_z == 0:
        print ("max_x:", max_x, "min_x:", min_x, "max_z", max_z, "min_z", min_z)
    # return
    max_x = 300
    min_x = -300
    max_z = 300
    min_z = -300
    print ("max_x:", max_x, "min_x:", min_x, "max_z", max_z, "min_z", min_z)

    w = (max_x-min_x)/10
    h = (max_z-min_z)/10
    print("w:", w, "h:", h)


    i = 0
    score_map = np.zeros((20, 20), dtype=float)
    maxHeightMap_map = np.zeros((20, 20), dtype=float)
    for x in range(min_x, max_x-w+1, w):
        j = 0
        for z in range(min_z, max_z-h+1, h):
            print("i, j =", i, j, "x, z = ", x, z)

            hm = HeightMap.HeightMap(level, x, z, x+w+1, z+h+1)  # Create height map
            # if x == 0 and z == 0:
            #     hm.showMap()
            print("max height: ", np.amax(hm.height_map))
            maxHeightMap_map[i][j] = np.amax(hm.height_map)
            ids = []
            for sx in range(x, x+w):
                for sz in range(z, z+h):
                    ids.append(level.blockAt(sx, hm.height_map[sx-x][sz-z], sz))
            score_map[i][j] = get_score(ids)

            print(score_map)
            j += 1
        i += 1
    print(maxHeightMap_map)
    np.save(levelName + "_maxHeightMap.npy", maxHeightMap_map)
    maxHeightMap_map = np.load(levelName + "_maxHeightMap.npy")
    np.save(levelName + ".npy", score_map)
    score_map = np.load(levelName + ".npy")
    score_map = normalization(score_map)
    print("score_map", score_map)
    print(np.median(score_map))
    print(np.std(score_map))
    mean = np.mean(score_map)
    meanAnd2std = mean + np.std(score_map) * 2
    print("meanAnd2std", meanAnd2std)

    sum_x = 0
    sum_z = 0
    sum = 0
    i = 0
    for x in range(min_x, max_x-w, w):
        j = 0
        for z in range(min_z, max_z-h, h):
            we = score_map[i][j]
            if we >= meanAnd2std:
                sum += we
            j += 1
        i += 1
    print("sum", sum)
    i = 0
    for x in range(min_x, max_x-w, w):
        j = 0
        for z in range(min_z, max_z-h, h):
            we = score_map[i][j]
            if we >= meanAnd2std:
                print(x, z, we)
                sum_x += (x+w/2) * we/sum
                sum_z += (z+h/2) * we/sum
            j += 1
        i += 1
    # print(sum_x, sum_z)
    # t_x, t_z = int(w * sum_x) + min_x, int(h * sum_z) + min_z
    # print(t_x, t_z)
    a = math.atan2(-sum_x, sum_z) * (180 / math.pi)
    if a < 0:
        a = 360 + a
    print("x:",  sum_x, "z:", sum_z, " angle:", a)

    # path_list = []
    # hm = HeightMap.HeightMap(level, 0, 0, 1, 1)
    # # print hm.height_map
    # n_height = hm.height_map[0][0]
    # n = float(t_x)/t_z
    # m = float(t_z)/t_x
    # sign = 1
    # if t_z < 0:
    #     sign = -1
    # for z in range(t_z, sign):
    #     path_pair = (int(z*n), z)
    #     if path_pair not in path_list:
    #         path_list.append(path_pair)
    # sign = 1
    # if t_x < 0:
    #     sign = -1
    # for x in range(0, t_x, sign):
    #     path_pair = (x, int(x * m))
    #     if path_pair not in path_list:
    #         path_list.append(path_pair)
    # # print(path_list)
    # for one in path_list:
    #     if level.blockAt(one[0], n_height, one[1]):
    #         while level.blockAt(one[0], n_height, one[1]) != 0:
    #             n_height += 1
    #         n_height += 10
    o_i = 300//30
    o_j = 300//30
    i_height = maxHeightMap_map[o_i][o_j] + 10
    print("Initial height :", i_height)

    player_rotation = [nbt.TAG_Float(a), nbt.TAG_Float(0)]
    level.root_tag['Data']['Player']['Rotation'] = player_rotation
    player_pos = [nbt.TAG_Double(0), nbt.TAG_Double(i_height), nbt.TAG_Double(0)]
    level.root_tag['Data']['Player']['Pos'] = player_pos
