import torch
import torchvision
from torch.utils.data import DataLoader, random_split, Dataset
from torchvision.transforms import Compose
from typing import Union

class MNISTCustomDataset(Dataset):
    def __init__(self, images, labels, transform=None):
        self.images = images
        self.labels = labels
        self.transform = transform

    def __getitem__(self, index):
        x = self.images[index]
        y = self.labels[index]

        if self.transform:
            x = self.transform(x)

        return x, y

    def __len__(self):
        return len(self.images)



def get_mnist_custom_dataset(images, labels):
    transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor(),
                            torchvision.transforms.Normalize((0.5,), (0.5,))
                            ]) 
    return MNISTCustomDataset(images, labels, transform=None)


def get_mnist():
    import torchvision
    transform = transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor(),
                            torchvision.transforms.Normalize((0.5,), (0.5,))
                            ])
    dataset = torchvision.datasets.MNIST(root="./data", download=True)
    return dataset, transform


def get_cifar10():
    import torchvision
    transform = torchvision.transforms.Compose([torchvision.transforms.ToTensor(
    ), torchvision.transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    dataset = torchvision.datasets.CIFAR10(root="./data", download=True)

    return dataset, transform


def get_dataset(dataset_name, images=None, labels=None):
    if dataset_name == "mnist":
        return get_mnist()
    elif dataset_name == "cifar10":
        return get_cifar10()
    elif dataset_name == "mnist_custom":
        return get_mnist_custom_dataset(images, labels)
    else:
        raise ValueError("Dataset not found")


def load_data(num_clients: int, batch_size: int, dataset: Dataset, train_size: float, test_size: float, transform: Union[Compose, None] = None) -> tuple[list[DataLoader], list[DataLoader], DataLoader]:
    if transform is not None:
        dataset.transform = transform
    lengths = [int(len(dataset) * train_size), int(len(dataset) * test_size)]
    print("Len Dataset", len(dataset))
    print("Lengths", lengths)

    trainset, testset = random_split(dataset, lengths)

    partition_size = len(trainset) // 50
    lengths = [partition_size] * 50

    datasets = random_split(
        trainset, lengths, torch.Generator().manual_seed(42))

    trainloaders = []
    valloaders = []

    for ds in datasets:
        len_val = len(ds) // 5
        len_train = len(ds) - len_val
        lengths = [len_train, len_val]
        ds_train, ds_val = random_split(
            ds, lengths, torch.Generator().manual_seed(42))
        trainloaders.append(DataLoader(
            ds_train, batch_size=batch_size, shuffle=True))
        valloaders.append(DataLoader(ds_val, batch_size=batch_size))
    testloader = DataLoader(testset, batch_size=batch_size)

    return trainloaders, valloaders, testloader