import os
import numpy as np
import pickle as pickle
import pandas as pd
import random

#random.seed(42)

def load_androiddata(encoding, filename='./drebin.csv'):
    trans = pd.read_csv(filename, encoding=encoding)
    fraud_items = trans[trans['class'] == 'S']
    valid_items = trans[trans['class'] == 'B']
    fraud_account = fraud_items.shape[0]
    print("malware account: ", fraud_account)
    valid_account = valid_items.shape[0]
    print("benign account: ", valid_account)
    fraud_idx = list(fraud_items.id)
    valid_idx = list(valid_items.id)
    random.shuffle(fraud_idx)
    random.shuffle(valid_idx)
    train_fraud = fraud_idx[:int(fraud_account * 0.8)]
    train_valid = valid_idx[:int(valid_account * 0.8)] 
    print("train account: ", len(train_fraud) + len(train_valid))
    #print(train_malware[1:3])
    #print(train_benign[1:3])
    test_fraud = fraud_idx[int(fraud_account * 0.8):]
    test_valid = valid_idx[int(valid_account * 0.8):]
    print("test account: ", len(test_fraud) + len(test_valid))
    #print(test_malware[1:3])
    #print(test_benign[1:3])

    #train_dataset, test_dataset = {'train_x':[], 'train_y':[]}, {'test_x':[], 'test_y':[]}

    if not os.path.exists('aux_files'):
        os.mkdir('aux_files')
    
    print("generating train malware dataset...")
    train_x = []
    for i in train_fraud:
        features = fraud_items.loc[fraud_items.id == i, 'f1':'f215'].as_matrix()
        #print(i, features)
        features = np.squeeze(features.astype('float'))
        train_x += features,
    print("generating train benign dataset...")
    for i in train_valid:
        features = valid_items.loc[valid_items.id == i, 'f1':'f215'].as_matrix()
        features = np.squeeze(features.astype('float'))
        train_x += features,

    train_y = [1] * len(train_fraud) + [0] * len(train_valid)
    
    print(len(train_x), len(train_y))
    #train_dataset['train_x'] = train_x
    #train_dataset['train_y'] = train_y
    np.save('aux_files/drebin_train_x.npy', train_x)
    np.save('aux_files/drebin_train_y.npy', train_y)

    print("generating test malware dataset...")
    test_x = []
    for i in test_fraud:
        features = fraud_items.loc[fraud_items.id == i, 'f1':'f215'].as_matrix()
        features = np.squeeze(features.astype('float'))
        test_x += features,
    print("generating test benign dataset...")
    for i in test_valid:
        features = valid_items.loc[valid_items.id == i, 'f1':'f215'].as_matrix()
        features = np.squeeze(features.astype('float'))
        test_x += features,

    test_y = [1] * len(test_fraud) + [0] * len(test_valid)

    print(len(test_x), len(test_y))
    #test_dataset['test_x'] = test_x
    #test_dataset['test_y'] = test_y
    np.save('aux_files/drebin_test_x.npy', test_x)
    np.save('aux_files/drebin_test_y.npy', test_y)


if __name__ == '__main__':
    print("load drebin data")
    load_androiddata('latin1')
    print("done")
    print("all set")
