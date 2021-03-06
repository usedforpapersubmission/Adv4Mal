import time
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim import lr_scheduler
from models import InceptionNet_HardCoded, InceptionDataset, ToTensor
from sklearn.metrics import f1_score

#GPU device
device = torch.device("cuda:0")
device_ids = [0,1,2]

#Training settings
epochs = 8
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
train_dataset = InceptionDataset(feature_file=train_feature_file,
                              label_file=train_label_file,
                              transform=transforms.Compose([
                                  ToTensor()
                              ]),
                              feature_len=feature_size,
                              opt='train')

train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=3)

#Load testing data
test_dataset = InceptionDataset(feature_file=test_feature_file,
                             label_file=test_label_file,
                             transform=transforms.Compose([
                                 ToTensor()
                             ]),
                             feature_len=feature_size,
                             opt='test')

test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=3)

#dataiter = iter(test_dataloader)
#samples = dataiter.next()
#print(samples['label'], samples['features'])
#cnt_0, cnt_1, cnt_2, cnt_3 = 0, 0, 0, 0
#temp = samples['features'][0].reshape(3*224*224)
#for i in temp:
#    if i == -1.8:
#        cnt_0 += 1
#    elif i == 1.8:
#        cnt_1 += 1
#    elif i < -2:
#        cnt_2 += 1
#    elif i > 2:
#        cnt_3 += 1
#print(cnt_0, cnt_1, cnt_2, cnt_3)
#exit()

#Model and optimizer
pre_train_time = torch.FloatTensor([0.0])
model = InceptionNet_HardCoded(feature_size, pre_train_time)
parameter_to_update = []
for p in model.parameters():
    if p.requires_grad:
        parameter_to_update.append(p)
        break
#print(parameter_to_update)
#exit()
optimizer = optim.Adam(parameter_to_update, lr=lr, weight_decay=weight_decay)
schedule = lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.1)
mask = np.load('aux_files/mask_inception_%d.npy' % (feature_size))
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
    end_train = time.time()
    t = time.time()
    model.train()
    running_loss = 0.0
    train_total, train_correct = 0.0, 0.0
    y_true, y_pred = [], []
    for i, data in enumerate(train_dataloader):
        #data.cuda()
        labels, features = data['label'], data['features']
        #labels = labels.cuda()
        labels = labels.to(device)
        #features = features.cuda()
        features = features.to(device)
        optimizer.zero_grad()
        #forward, backward, optimize
        #print(features.shape)
        outputs1, outputs2 = model(features, epsilon, mask)
        #print(outputs, labels.long())
        #print(outputs.shape, labels.shape)
        loss1 = criterion(outputs1, labels.long())
        loss2 = criterion(outputs2, labels.long())
        loss = loss1 + loss2
        loss.backward()
        optimizer.step()
        #print statistics
        running_loss += loss.item()
        _, train_predicted = torch.max(outputs1.data, 1)
        train_total += labels.size(0)
        train_correct += (train_predicted == labels.long()).sum().item()
        y_true += labels.tolist()
        y_pred += train_predicted.tolist()
        #if i % 20 == 19:
            #print('[%d, %5d] loss: %.3f time: %.4f' % (epoch, i + 1, running_loss/2000, time.time() - t))
        t = time.time()
    score = f1_score(y_true, y_pred)
    t_bf = t_af
    t_af = pre_train_time[0].item() 
    print("Train accuracy: %.4f, f1_score: %.4f, loss: %.3f, epoch (%d) time: %.4f, time excluding pre_trained: %.4f" % (train_correct/train_total, score, running_loss/train_total, epoch, time.time() - end_train, time.time() - end_train - (t_af - t_bf)))

#Test
def test():
    global t_af
    end_test = time.time()
    model.eval()
    test_correct, test_total = 0.0, 0.0
    y_true, y_pred = [], []
    with torch.no_grad():
        for data in test_dataloader:
            #data.cuda()
            labels, features = data['label'], data['features']
            #labels = labels.cuda()
            labels = labels.to(device)
            #features = features.cuda()
            features = features.to(device)
            outputs = model(features, epsilon, mask)
            _, predicted = torch.max(outputs.data, 1)
            test_total += labels.size(0)
            test_correct += (predicted == labels.long()).sum().item()
            y_true += labels.tolist()
            y_pred += predicted.tolist()
    score = f1_score(y_true, y_pred)
    print('Test accuracy: %.4f, f1_score: %.4f, test time: %.4f, time excluding pre_trained: %.4f' % (test_correct / test_total, score, time.time() - end_test, time.time() - end_test - (pre_train_time[0].item() - t_af)))

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
