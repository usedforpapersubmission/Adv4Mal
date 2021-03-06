import time
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torchvision.models as models
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim import lr_scheduler
from models import AdvRepDataset, ToTensor
from sklearn.metrics import f1_score

#GPU device
device = torch.device("cuda:0")
device_ids = [0,1,2]

#Training settings
epochs = 40
lr = 0.01
weight_decay = 5e-4
dropout = 0.5
batch_size = 120
epsilon = 0.3
feature_size = 329 #3503 #329
criterion = nn.CrossEntropyLoss()
#train_feature_file = 'aux_files/pc_train_x.npy' 
train_feature_file = 'aux_files/android_train_x.npy'
#train_label_file = 'aux_files/pc_train_y.npy' 
train_label_file = 'aux_files/android_train_y.npy'
#test_feature_file = 'aux_files/pc_test_x.npy' 
test_feature_file = 'aux_files/android_test_x.npy'
#test_label_file = 'aux_files/pc_test_y.npy' 
test_label_file = 'aux_files/android_test_y.npy'

#Load training data
train_dataset = AdvRepDataset(feature_file=train_feature_file,
                              label_file=train_label_file,
                              transform=transforms.Compose([
                                  ToTensor()
                              ]),
                              feature_len=feature_size,
                              opt='train')

train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=3)

#Load testing data
test_dataset = AdvRepDataset(feature_file=test_feature_file,
                             label_file=test_label_file,
                             transform=transforms.Compose([
                                 ToTensor()
                             ]),
                             feature_len=feature_size,
                             opt='test')

test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=3)

#Model and optimizer
pre_train_time = 0.0
#model = AdvRepNet_Transfer(feature_size, pre_train_time) 

#DenseNet
model = models.densenet161(pretrained=True)
num_ftrs = model.classifier.in_features
model.classifier = nn.Linear(num_ftrs, 2)

#ResNet
#model = models.resnet101(pretrained=True)
#num_ftrs = model.fc.in_features
#model.fc = nn.Linear(num_ftrs, 2)

parameter_to_update = model.parameters()

optimizer = optim.Adam(parameter_to_update, lr=lr, weight_decay=weight_decay)
schedule = lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.1)
mask = np.load('aux_files/mask_%d.npy' % (feature_size))
mask = torch.FloatTensor(mask)
#mask = mask.cuda()
mask = mask.to(device)
#model.cuda()
model = nn.DataParallel(model, device_ids=device_ids)
model.to(device)
t_bf, t_af = 0.0, 0.0

#Train
def train(epoch):
    global t_bf
    global t_af
    global pre_train_time
    end_train = time.time()
    t = time.time()
    model.train()
    running_loss = 0.0
    train_total, train_correct = 0.0, 0.0
    y_true, y_pred = [], []
    for i, data in enumerate(train_dataloader):
        labels, features = data['label'], data['features']
        labels = labels.to(device)
        features = features.to(device)
        optimizer.zero_grad()
        t1 = time.time()
        outputs = model(features)
        t2 = time.time()
        t3 = t2 - t1
        pre_train_time += t3
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
    t_bf = t_af
    t_af = pre_train_time 
    print("Train accuracy: %.4f, f1_score: %.4f, loss: %.3f, epoch (%d) time: %.4f, time excluding pre_trained: %.4f" % (train_correct/train_total, score, running_loss/train_total, epoch, time.time() - end_train, time.time() - end_train - (t_af - t_bf)))

#Test
def test():
    global t_af
    global pre_train_time
    end_test = time.time()
    model.eval()
    test_correct, test_total = 0.0, 0.0
    y_true, y_pred = [], []
    with torch.no_grad():
        for data in test_dataloader:
            labels, features = data['label'], data['features']
            labels = labels.to(device)
            features = features.to(device)
            t1 = time.time()
            outputs = model(features)
            t2 = time.time()
            t3 = t2 - t1
            pre_train_time += t3
            _, predicted = torch.max(outputs.data, 1)
            test_total += labels.size(0)
            test_correct += (predicted == labels.long()).sum().item()
            y_true += labels.tolist()
            y_pred += predicted.tolist()
    #print("true:", y_true)
    #print("pred:", y_pred)
    score = f1_score(y_true, y_pred)
    print('Test accuracy: %.4f, f1_score: %.4f, test time: %.4f, time excluding pre_trained: %.4f' % (test_correct / test_total, score, time.time() - end_test, time.time() - end_test - (pre_train_time - t_af)))

#Train model
t_total = time.time()
for epoch in range(1, epochs + 1):
    #schedule.step()
    train(epoch)
    schedule.step()
print("Training finished using (%.4f)s, excluding pre_train using (%.4f)s" % (time.time() - t_total, time.time() - t_total - t_af))

#Test
test()

#for p in model.parameters():
#    print(p, p.requires_grad)
