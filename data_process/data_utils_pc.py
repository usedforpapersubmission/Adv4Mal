import os
import numpy as np
import pickle as pickle
import pandas as pd
import random

random.seed(42)

def load_pcdata(encoding, filename='pc_fulldata.csv'):
    pc = pd.read_csv(filename, encoding=encoding)

    #######Temp processing
    max_num = {}
    for i in pc.id:
        api_list = list(pc.loc[pc.id == i, 'api_list'])
        items = api_list[0].split(',')[:-1]
        for api in items:
            api = int(api)
            max_num[api] = max_num.get(api, 0) + 1
    second_max = {}
    for key, value in max_num.items():
        if value > 2:
            second_max[key] = value
    idx_to_api = sorted(second_max.keys())
    api_to_idx = {}
    for idx, api in enumerate(idx_to_api):
        api_to_idx[api] = idx
    #print(api_to_idx)
    #######Temp processing
    
    malware_items = pc[pc['label'] == 1]
    benign_items = pc[pc['label'] == -1]
    malware_account = malware_items.shape[0]
    print("malware account: ", malware_account)
    benign_account = benign_items.shape[0]
    print("benign account: ", benign_account)
    malware_idx = list(malware_items.id)
    benign_idx = list(benign_items.id)
    random.shuffle(malware_idx)
    random.shuffle(benign_idx)
    train_malware = malware_idx[:int(malware_account * 0.8)]
    train_benign = benign_idx[:int(benign_account * 0.8)] 
    print("train account: ", len(train_malware) + len(train_benign))
    print(train_malware[1:3])
    print(train_benign[1:3])
    test_malware = malware_idx[int(malware_account * 0.8):]
    test_benign = benign_idx[int(benign_account * 0.8):]
    print("test account: ", len(test_malware) + len(test_benign))
    print(test_malware[1:3])
    print(test_benign[1:3])

    #train_dataset, test_dataset = {'train_x':[], 'train_y':[]}, {'test_x':[], 'test_y':[]}

    if not os.path.exists('../aux_files'):
        os.mkdir('../aux_files')
    
    print("generating train malware dataset...")
    train_x = []
    for i in train_malware:
        api_list = list(malware_items.loc[malware_items.id == i, 'api_list'])
        items = api_list[0].split(',')[:-1]
        apis = np.zeros(3503)
        for api in items:
            api = int(api)
            if api not in api_to_idx:
                continue
            apis[api_to_idx[api]] = 1
        #print(i, sum(apis))
        train_x += apis,
    print("generating train benign dataset...")
    for i in train_benign:
        api_list = list(benign_items.loc[benign_items.id == i, 'api_list'])
        items = api_list[0].split(',')[:-1]
        apis = np.zeros(3503)
        for api in items:
            api = int(api)
            if api not in api_to_idx:
                continue
            apis[api_to_idx[api]] = 1
        train_x += apis,

    train_y = [1] * len(train_malware) + [0] * len(train_benign)
    
    print(len(train_x), len(train_y))
    #train_dataset['train_x'] = train_x
    #train_dataset['train_y'] = train_y
    np.save('../aux_files/pc_train_x.npy', train_x)
    np.save('../aux_files/pc_train_y.npy', train_y)

    print("generating test malware dataset...")
    test_x = []
    for i in test_malware:
        api_list = list(malware_items.loc[malware_items.id == i, 'api_list'])
        items = api_list[0].split(',')[:-1]
        apis = np.zeros(3503)
        for api in items:
            api = int(api)
            if api not in api_to_idx:
                continue
            apis[api_to_idx[api]] = 1
        test_x += apis,
    print("generating test benign dataset...")
    for i in test_benign:
        api_list = list(benign_items.loc[benign_items.id == i, 'api_list'])
        items = api_list[0].split(',')[:-1]
        apis = np.zeros(3503)
        for api in items:
            api = int(api)
            if api not in api_to_idx:
                continue
            apis[api_to_idx[api]] = 1
        test_x += apis,

    test_y = [1] * len(test_malware) + [0] * len(test_benign)

    print(len(test_x), len(test_y))
    #test_dataset['test_x'] = test_x
    #test_dataset['test_y'] = test_y
    np.save('../aux_files/pc_test_x.npy', test_x)
    np.save('../aux_files/pc_test_y.npy', test_y)


if __name__ == '__main__':
    print("load pc data")
    load_pcdata('latin1')
    print("done")
    print("all set")
