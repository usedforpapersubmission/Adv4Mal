import os
import numpy as np
import pickle as pickle
import pandas as pd
import random

#random.seed(42)

def load_drebindata(encoding, filename='../data/drebin.csv'):
    files = pd.read_csv(filename, encoding=encoding)
    malware_items = files[files['class'] == 'S']
    benign_items = files[files['class'] == 'B']
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
    #print(train_malware[1:3])
    #print(train_benign[1:3])
    test_malware = malware_idx[int(malware_account * 0.8):]
    test_benign = benign_idx[int(benign_account * 0.8):]
    print("test account: ", len(test_malware) + len(test_benign))
    #print(test_malware[1:3])
    #print(test_benign[1:3])

    #train_dataset, test_dataset = {'train_x':[], 'train_y':[]}, {'test_x':[], 'test_y':[]}

    if not os.path.exists('../aux_files'):
        os.mkdir('../aux_files')
    
    print("generating train malware dataset...")
    train_x = []
    for i in train_malware:
        features = malware_items.loc[malware_items.id == i, 'f1':'f215'].as_matrix()
        #print(i, features)
        features = np.squeeze(features.astype('float'))
        train_x += features,
    print("generating train benign dataset...")
    for i in train_benign:
        features = benign_items.loc[benign_items.id == i, 'f1':'f215'].as_matrix()
        features = np.squeeze(features.astype('float'))
        train_x += features,

    train_y = [1] * len(train_malware) + [0] * len(train_benign)
    
    print(len(train_x), len(train_y))
    #train_dataset['train_x'] = train_x
    #train_dataset['train_y'] = train_y
    np.save('../aux_files/drebin_train_x.npy', train_x)
    np.save('../aux_files/drebin_train_y.npy', train_y)

    print("generating test malware dataset...")
    test_x = []
    for i in test_malware:
        features = malware_items.loc[malware_items.id == i, 'f1':'f215'].as_matrix()
        features = np.squeeze(features.astype('float'))
        test_x += features,
    print("generating test benign dataset...")
    for i in test_benign:
        features = benign_items.loc[benign_items.id == i, 'f1':'f215'].as_matrix()
        features = np.squeeze(features.astype('float'))
        test_x += features,

    test_y = [1] * len(test_malware) + [0] * len(test_benign)

    print(len(test_x), len(test_y))
    #test_dataset['test_x'] = test_x
    #test_dataset['test_y'] = test_y
    np.save('../aux_files/drebin_test_x.npy', test_x)
    np.save('../aux_files/drebin_test_y.npy', test_y)


if __name__ == '__main__':
    print("load drebin data")
    load_androiddata('latin1')
    print("done")
    print("all set")
