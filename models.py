import os
import torch
import math
import time
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torch.nn.parameter import Parameter

np.random.seed(42)

#Define an adversarial reprogramming neural network - other than Inception V3
class AdvRepNet(nn.Module):
    def __init__(self, feature_size, counter):
        super(AdvRepNet, self).__init__()
        self.counter = counter
        self.perturbation = Parameter(torch.FloatTensor(3, 224, 224))
        self.reset_parameter()
        self.pretrained_model = models.resnet50(pretrained=True)
        self.pretrained_model.eval()
        for param in self.pretrained_model.parameters():
            param.requires_grad = False

    def reset_parameter(self):
        stdv = 1. / math.sqrt(self.perturbation.size(1))
        self.perturbation.data.uniform_(-stdv, stdv)

    def forward(self, x, epsilon, mask):
        x = x + epsilon * self.perturbation * mask
        x = torch.clamp(x, -1.8, 1.8)
        t1 = time.time()
        #x = F.dropout(x, 0.5, training=self.training)
        x = self.pretrained_model(x)
        t2 = time.time()
        x = x.reshape((x.shape[0], 2, 500))
        x = torch.sum(x, dim=2, keepdim=True)
        x = x.reshape((x.shape[0], 2))
        t = t2 - t1
        self.counter[0] += t
        return x

#Define an adversarial reprogramming neural network - other than Inception V3, hard coded mapping
class AdvRepNet_HardCoded(nn.Module):
    def __init__(self, feature_size, counter):
        super(AdvRepNet_HardCoded, self).__init__()
        self.counter = counter
        self.hard_coded_idx = [0, 1]
        self.perturbation = Parameter(torch.FloatTensor(3, 224, 224))
        self.reset_parameter()
        self.pretrained_model = models.densenet121(pretrained=True)
        self.pretrained_model.eval()   #comment for transfer learning
        for param in self.pretrained_model.parameters():
            param.requires_grad = False

    def reset_parameter(self):
        stdv = 1. / math.sqrt(self.perturbation.size(1))
        self.perturbation.data.uniform_(-stdv, stdv)

    def forward(self, x, epsilon, mask):
        x = x + epsilon * self.perturbation * mask
        x = torch.clamp(x, -1.8, 1.8)
        t1 = time.time()
        x = self.pretrained_model(x)
        t2 = time.time()
        x = x[:, self.hard_coded_idx]
        t = t2 - t1
        self.counter[0] += t
        return x

#Define an adversarial reprogramming neural network - Inception V3
class InceptionNet(nn.Module):
    def __init__(self, feature_size, counter):
        super(InceptionNet, self).__init__()
        self.counter = counter
        self.perturbation = Parameter(torch.FloatTensor(3, 299, 299))
        self.reset_parameter()
        self.pretrained_model = models.inception_v3(pretrained=True)
        self.pretrained_model.eval()
        for param in self.pretrained_model.parameters():
            param.requires_grad = False

    def reset_parameter(self):
        stdv = 1. / math.sqrt(self.perturbation.size(1))
        self.perturbation.data.uniform_(-stdv, stdv)

    def forward(self, x, epsilon, mask):
        x = x + epsilon * self.perturbation * mask
        x = torch.clamp(x, -1.8, 1.8)
        t1 = time.time()
        if self.training:
            x1, x2 = self.pretrained_model(x)
            t2 = time.time()
            x1 = x1.reshape((x1.shape[0], 2, 500))
            x1 = torch.sum(x1, dim=2, keepdim=True)
            x1 = x1.reshape((x1.shape[0], 2))
            x2 = x2.reshape((x2.shape[0], 2, 500))
            x2 = torch.sum(x2, dim=2, keepdim=True)
            x2 = x2.reshape((x2.shape[0], 2))
            t = t2 - t1
            self.counter[0] += t
            return x1, x2
        else:
            x = self.pretrained_model(x)
            t2 = time.time()
            x = x.reshape((x.shape[0], 2, 500))
            x = torch.sum(x, dim=2, keepdim=True)
            x = x.reshape((x.shape[0], 2))
            t = t2 - t1
            self.counter[0] += t
            return x

#Define an adversarial reprogramming neural network - Inception V3, hard coded mapping
class InceptionNet_HardCoded(nn.Module):
    def __init__(self, feature_size, counter):
        super(InceptionNet_HardCoded, self).__init__()
        self.counter = counter
        self.hard_coded_idx = [0, 1]
        self.perturbation = Parameter(torch.FloatTensor(3, 299, 299))
        self.reset_parameter()
        self.pretrained_model = models.inception_v3(pretrained=True)
        self.pretrained_model.eval()
        for param in self.pretrained_model.parameters():
            param.requires_grad = False

    def reset_parameter(self):
        stdv = 1. / math.sqrt(self.perturbation.size(1))
        self.perturbation.data.uniform_(-stdv, stdv)

    def forward(self, x, epsilon, mask):
        x = x + epsilon * self.perturbation * mask
        x = torch.clamp(x, -1.8, 1.8)
        t1 = time.time()
        if self.training:
            x1, x2 = self.pretrained_model(x)
            t2 = time.time()
            x1 = x1[:, self.hard_coded_idx]
            x2 = x2[:, self.hard_coded_idx]
            t = t2 - t1
            self.counter[0] += t
            return x1, x2
        else:
            x = self.pretrained_model(x)
            t2 = time.time()
            x = x[:, self.hard_coded_idx]
            t = t2 - t1
            self.counter[0] += t
            return x

class InceptionNet_Transfer(nn.Module):
    def __init__(self, counter):
        super(InceptionNet_Transfer, self).__init__()
        #self.hard_coded_idx = [0, 1]
        self.counter = counter
        self.pretrained_model = models.inception_v3(pretrained=True)
        num_ftrs = self.pretrained_model.AuxLogits.fc.in_features
        self.pretrained_model.AuxLogits.fc = nn.Linear(num_ftrs, 2)
        num_ftrs = self.pretrained_model.fc.in_features
        self.pretrained_model.fc = nn.Linear(num_ftrs, 2)

    def forward(self, x):
        t1 = time.time()
        if self.training:
            x1, x2 = self.pretrained_model(x)
            t2 = time.time()
            #x1 = x1[:, self.hard_coded_idx]
            #x2 = x2[:, self.hard_coded_idx]
            t = t2 - t1
            self.counter[0] += t
            return x1, x2
        else:
            x = self.pretrained_model(x)
            t2 = time.time()
            #x = x[:, self.hard_coded_idx]
            t = t2 - t1
            self.counter[0] += t
            return x

#Define a deep neural network
class DetectionNet(nn.Module):
    def __init__(self, init_features, dropout=0.5):
        super(DetectionNet, self).__init__()
        self.fc1 = nn.Linear(init_features, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
        self.fc4 = nn.Linear(10, 2)
        self.dropout = dropout

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.dropout(x, self.dropout, training=self.training)
        x = F.relu(self.fc2(x))
        x = F.dropout(x, self.dropout, training=self.training)
        x = F.relu(self.fc3(x))
        #x = F.dropout(x, self.dropout, training=self.training)
        x = self.fc4(x)
        return x

class DetectionDataset(Dataset):
    def __init__(self, feature_file='aux_files/android_train_x.npy', label_file='aux_files/android_train_y.npy', transform=None):
        self.features = np.load(feature_file)
        self.labels = np.load(label_file)
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        features = self.features[idx]
        label = self.labels[idx]
        sample = {'label': label, 'features': features}

        if self.transform:
            sample = self.transform(sample)

        return sample

class ToTensor(object):
    def __call__(self, sample):
        label, features = sample['label'], sample['features']
        label = np.array(label)
        return {'label': torch.from_numpy(label),
                'features': torch.from_numpy(features).float()}

class AdvRepDataset(Dataset):
    def __init__(self, feature_file='aux_files/android_train_x.npy', label_file='aux_files/android_train_y.npy', host_image='aux_files/selected_images.npy', transform=None, feature_len=329, opt='train'):
        self.features = np.load(feature_file)
        self.labels = np.load(label_file)
        host_images = np.load(host_image)
        self.host_image = host_images[0]
        if opt == 'train':
            self.mask = np.ones_like(self.host_image)
            #self.mask = self.mask.transpose((1, 2, 0))
            #self.mask = self.mask.reshape(3 * 224 * 224)
            #ones = np.ones(feature_len)
            #self.mask[:feature_len] += ones
            #self.mask = self.mask.reshape(224, 224, 3)
            #self.mask = self.mask.transpose((2, 0, 1))
            self.mask = self.mask.reshape(3 * 224 * 224)
            self.indices = np.random.choice(3 * 224 * 224, feature_len, replace=False)
            self.mask[self.indices] = 0
            self.mask = self.mask.reshape((3, 224, 224))
            np.save('aux_files/mask_%d.npy' % (feature_len), self.mask)
            np.save('aux_files/indices_%d.npy' % (feature_len), self.indices)
        elif opt == 'test':
            self.indices = np.load('aux_files/indices_%d.npy' % (feature_len))
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        features = self.features[idx]
        label = self.labels[idx]
        host = self.host_image
        features = np.where(features == 0, features - 1.8, features + 0.8)
        host = host.reshape(3 * 224 * 224)
        host[self.indices] = features
        host = host.reshape((3, 224, 224))
        sample = {'label': label, 'features': host}

        if self.transform:
            sample = self.transform(sample)

        return sample

class InceptionDataset(Dataset):
    def __init__(self, feature_file='aux_files/android_train_x.npy', label_file='aux_files/android_train_y.npy', host_image='aux_files/selected_images_inception.npy', transform=None, feature_len=329, opt='train'):
        self.features = np.load(feature_file)
        self.labels = np.load(label_file)
        host_images = np.load(host_image)
        self.host_image = host_images[4]
        if opt == 'train':
            #self.mask = np.ones_like(self.host_image)
            self.mask = np.ones(3 * 299 * 299)
            self.indices = np.random.choice(3 * 299 * 299, feature_len, replace=False)
            self.mask[self.indices] = 0
            self.mask = self.mask.reshape((3, 299, 299))
            np.save('aux_files/mask_inception_%d.npy' % (feature_len), self.mask)
            np.save('aux_files/indices_inception_%d.npy' % (feature_len), self.indices)
        elif opt == 'test':
            self.indices = np.load('aux_files/indices_inception_%d.npy' % (feature_len))
        self.transform = transform

    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        features = self.features[idx]
        label = self.labels[idx]
        inception_host = self.host_image
        features = np.where(features == 0, features - 1.8, features + 0.8)
        #inception_host = np.zeros((3, 299, 299))
        #for i in range(3):
        #    inception_host[i] = np.pad(inception_host[i], (37, 38), 'constant', constant_values=(0, 0))
        inception_host = inception_host.reshape(3 * 299 * 299)
        inception_host[self.indices] = features
        inception_host = inception_host.reshape((3, 299, 299))
        sample = {'label': label, 'features': inception_host}

        if self.transform:
            sample = self.transform(sample)

        return sample
