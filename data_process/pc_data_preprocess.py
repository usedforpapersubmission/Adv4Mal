import os
import pandas as pd
import numpy as np

def process_dataset(csv_folder, api_file, label_file, encoding):
    api_file = os.path.join(csv_folder, api_file)
    label_file = os.path.join(csv_folder, label_file)
    apis = pd.read_csv(api_file, encoding=encoding)
    labels = pd.read_csv(label_file, encoding=encoding)
    cnt = 0
    for id in labels.id:
        if cnt % 1000 == 0:
            print(cnt)
        api_list = list(apis.loc[apis.id == id]['api_list'])
        #print(api_list)
        #api_list = set(item[0].split(',')[:-1])
        #print(api_list)
        #for i in range(1, 3504):
        #    if i % 100 == 0:
        #        print(i)
        #    api = str(i)
        #    api_tag = 'api' + api
        #    if api in api_list:
        #        labels.loc[labels.id == id, api_tag] = str(1)
        #    else:
        #        labels.loc[labels.id == id, api_tag] = str(0)
        labels.loc[labels.id == id, 'api_list'] = api_list
        cnt += 1
    labels.to_csv(os.path.join(csv_folder, 'pc_fulldata.csv'), index=False)

if __name__ == '__main__':
    process_dataset('../data/', 'pc_api.csv', 'pc_label.csv', 'latin1')
    print("all set")
