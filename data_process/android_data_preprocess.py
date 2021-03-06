import os
import pandas as pd
import numpy as np

def process_dataset(csv_folder, api_file, label_file, encoding):
    api_file = os.path.join(csv_folder, api_file)
    label_file = os.path.join(csv_folder, label_file)
    apis = pd.read_csv(api_file, encoding=encoding)
    labels = pd.read_csv(label_file, encoding=encoding)
    #cnt = 0
    for id in apis.id:
        label = list(labels.loc[labels.id == id]['label'])
        #print(label)
        #print(len(label), type(label))
        if len(label) == 1:
            apis.loc[apis.id == id, 'label'] = int(label[0])
        #cnt += 1
        #if cnt == 10:
        #    break
    apis.to_csv(os.path.join(csv_folder, 'android_fulldata.csv'), index=False)

if __name__ == '__main__':
    process_dataset('../data/', 'app_feature_matrix.csv', 'app_labels.csv', 'latin1')
    print("all set")
