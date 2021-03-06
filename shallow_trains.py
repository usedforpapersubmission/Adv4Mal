import time
import numpy as np
from sklearn.metrics import f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

#Data files
#train_feature_file = 'aux_files/pc_train_x.npy' 
train_feature_file = 'aux_files/android_train_x.npy'
#train_label_file = 'aux_files/pc_train_y.npy' 
train_label_file = 'aux_files/android_train_y.npy'
#test_feature_file = 'aux_files/pc_test_x.npy' 
test_feature_file = 'aux_files/android_test_x.npy'
#test_label_file = 'aux_files/pc_test_y.npy' 
test_label_file = 'aux_files/android_test_y.npy'

#Load training data
train_features = np.load(train_feature_file)
train_labels = np.load(train_label_file)

#Load testing data
test_features = np.load(test_feature_file)
test_labels = np.load(test_label_file)

#Random Forest
train_end = time.time()
model = RandomForestClassifier(random_state=0)
model.fit(train_features, train_labels)
print("Train time: %.4f" % (time.time() - train_end))
test_end = time.time()
predictions = model.predict(test_features)
f1 = f1_score(test_labels, predictions)
accuracy = accuracy_score(test_labels, predictions)
print("Test accuracy: %.4f, f1_score: %.4f, test time: %.4f" % (accuracy, f1, time.time() - train_end))

#SVM
train_end = time.time()
model = make_pipeline(StandardScaler(), LinearSVC(random_state=0, tol=1e-5))
model.fit(train_features, train_labels)
print("Train time: %.4f" % (time.time() - train_end))
test_end = time.time()
predictions = model.predict(test_features)
f1 = f1_score(test_labels, predictions)
accuracy = accuracy_score(test_labels, predictions)
print("Test accuracy: %.4f, f1_score: %.4f, test time: %.4f" % (accuracy, f1, time.time() - train_end))

#Logistic Regression
train_end = time.time()
model = LogisticRegression(random_state=0)
model.fit(train_features, train_labels)
print("Train time: %.4f" % (time.time() - train_end))
test_end = time.time()
predictions = model.predict(test_features)
f1 = f1_score(test_labels, predictions)
accuracy = accuracy_score(test_labels, predictions)
print("Test accuracy: %.4f, f1_score: %.4f, test time: %.4f" % (accuracy, f1, time.time() - train_end))

#Naive Bayes
train_end = time.time()
model = GaussianNB()
model.fit(train_features, train_labels)
print("Train time: %.4f" % (time.time() - train_end))
test_end = time.time()
predictions = model.predict(test_features)
f1 = f1_score(test_labels, predictions)
accuracy = accuracy_score(test_labels, predictions)
print("Test accuracy: %.4f, f1_score: %.4f, test time: %.4f" % (accuracy, f1, time.time() - train_end))

#K-NN
train_end = time.time()
model = KNeighborsClassifier(n_neighbors=5)
model.fit(train_features, train_labels)
print("Train time: %.4f" % (time.time() - train_end))
test_end = time.time()
predictions = model.predict(test_features)
f1 = f1_score(test_labels, predictions)
accuracy = accuracy_score(test_labels, predictions)
print("Test accuracy: %.4f, f1_score: %.4f, test time: %.4f" % (accuracy, f1, time.time() - train_end))

