import time
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim import lr_scheduler
from models import DetectionNet, DetectionDataset, ToTensor
from sklearn.metrics import f1_score

#Training settings
epochs = 15
lr = 0.01
weight_decay = 5e-4
dropout = 0.5
batch_size = 64
feature_size = 329 #3503 #329
criterion = nn.CrossEntropyLoss()
#train_feature_file = 'aux_files/pc_train_x.npy' 
train_feature_file = 'aux_files/android_train_x.npy'
#train_label_file='aux_files/pc_train_y.npy' 
train_label_file= 'aux_files/android_train_y.npy'
#test_feature_file = 'aux_files/pc_test_x.npy' 
test_feature_file = 'aux_files/android_test_x.npy'
#test_label_file = 'aux_files/pc_test_y.npy' 
test_label_file = 'aux_files/android_test_y.npy'

#Load training data
train_dataset = DetectionDataset(feature_file=train_feature_file,
                                 label_file=train_label_file,
                                 transform=transforms.Compose([
                                     ToTensor()
                                 ]))

train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)

#Load testing data
test_dataset = DetectionDataset(feature_file=test_feature_file,
                                 label_file=test_label_file,
                                 transform=transforms.Compose([
                                     ToTensor()
                                 ]))

test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

#dataiter = iter(test_dataloader)
#samples = dataiter.next()
#print(samples['label'], samples['features'])
#print(samples['label'].dtype, samples['features'].dtype)

#Model and optimizer
model = DetectionNet(feature_size, dropout)
optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
#schedule = lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.1)
model.cuda()

#Train
def train(epoch):
    end_train = time.time()
    t = time.time()
    model.train()
    running_loss = 0.0
    train_total, train_correct = 0.0, 0.0
    y_true, y_pred = [], []
    for i, data in enumerate(train_dataloader):
        #data.cuda()
        labels, features = data['label'], data['features']
        labels = labels.cuda()
        features = features.cuda()
        optimizer.zero_grad()
        #forward, backward, optimize
        outputs = model(features)
        #print(outputs, labels.long())
        loss = criterion(outputs, labels.long())
        loss.backward()
        optimizer.step()
        #print statistics
        running_loss += loss.item()
        _, train_predicted = torch.max(outputs.data, 1)
        train_total += labels.size(0)
        train_correct += (train_predicted == labels.long()).sum().item()
        y_true += labels.tolist()
        y_pred += train_predicted.tolist()
        #if i % 20 == 19:
            #print('[%d, %5d] loss: %.3f time: %.4f' % (epoch, i + 1, running_loss/2000, time.time() - t))
        t = time.time()
    score = f1_score(y_true, y_pred)
    print("Train accuracy: %.4f, f1_score: %.4f, loss: %.3f, epoch (%d) time: %.4f" % (train_correct/train_total, score, running_loss/train_total, epoch, time.time() - end_train))

#Test
def test():
    end_test = time.time()
    model.eval()
    test_correct, test_total = 0.0, 0.0
    y_true, y_pred = [], []
    with torch.no_grad():
        for data in test_dataloader:
            #data.cuda()
            labels, features = data['label'], data['features']
            labels = labels.cuda()
            features = features.cuda()
            outputs = model(features)
            _, predicted = torch.max(outputs.data, 1)
            test_total += labels.size(0)
            test_correct += (predicted == labels.long()).sum().item()
            y_true += labels.tolist()
            y_pred += predicted.tolist()
    score = f1_score(y_true, y_pred)
    print('Test accuracy: %.4f, f1_score: %.4f, test time: %.4f' % (test_correct / test_total, score, time.time() - end_test))

#Train model
t_total = time.time()
for epoch in range(1, epochs + 1):
    #schedule.step()
    train(epoch)
print("Training finished using (%.4f)s" % (time.time() - t_total))

#Test
test()
