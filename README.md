# Malware datasets
Three malware datasets: Windows PE files, Android apps, and Drebin apps

Windows PE files (pc_api.csv and pc_label.csv): 10,000 files with 5,000 malware (+1) and 5,000 benign files (-1)

Android apps (app_feature_matrix.csv and app_labels.csv): 7,670 apps with 3,303 malware (+1) and 4,367 benign apps (-1)

Drebin apps (drebin.csv): 15,036 apps with 9,476 malware (S) and 5,560 benign apps (B)

# Data process
data_utils.py (_android, _pc, _drebin): generate random data splits for training and testing

# Training and testing
adv_trains.py and inception_trains.py: perform model training and testing (accuracy, F1-score, training time, and testing time)
