import torch
from torchvision import datasets, transforms
import torchvision.models as models
from imagenet_preprocessing import parse_devkit_archive, parse_val_archive
import matplotlib.pyplot as plt
import numpy as np

#parse_devkit_archive('../aux_files/imagenet')
#parse_val_archive('../aux_files/imagenet')

model = models.inception_v3(pretrained=True)
model.eval()
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                   std=[0.229, 0.224, 0.225])
transform = transforms.Compose([transforms.Resize(299), transforms.CenterCrop(299), transforms.ToTensor(), normalize])
imagenet_data = datasets.ImageNet('../aux_files/imagenet', split='val', transform=transform)
data_loader = torch.utils.data.DataLoader(imagenet_data,
                                          batch_size=1,
                                          shuffle=True,
                                          num_workers=2)
#dataiter = iter(data_loader)
#image, label = dataiter.next()
#print(image.shape)
#image = image * std + mean
#print(image)
#exit()
#npimg = image[0].numpy()
#plt.imshow(np.transpose(npimg, (1, 2, 0)))
#plt.show()

for param in model.parameters():
    param.requires_grad = False

correct = 0.0
total = 0.0
selected_image = []
selected_label = []
model.cuda()
for i, (input, target) in enumerate(data_loader):
    input = input.cuda()
    target = target.cuda()
    #print(input.shape)
    #exit()
    output = model(input)
    _, predicted = torch.max(output.data, 1)
    total += target.size(0)
    correct += (predicted == target).sum().item()
    if (predicted == target).sum().item() == 1:
        print(input.shape)
        #print(target, predicted)
        #print(output)
        selected_image += input.tolist()
        selected_label += target.tolist()
    if correct == 5:
        break
print('Accuracy: %.4f' % (correct/total))

np.save('../aux_files/selected_images_inception.npy', selected_image)
np.save('../aux_files/selected_labels_inception.npy', selected_label)

