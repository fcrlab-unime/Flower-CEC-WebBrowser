import torch 
from torch.utils.data import DataLoader
import torch.nn as nn

def train_local(net: nn.Module, 
                trainloader: DataLoader, 
                epochs: int, criterion: nn.Module, 
                optimizer: torch.optim.Optimizer, 
                DEVICE: torch.device):

    """Train the network on the training set."""
    criterion = torch.nn.CrossEntropyLoss()
    net.train()
    for epoch in range(epochs):
        correct, total, epoch_loss = 0, 0, 0.0
        for batch_idx,(images, labels) in enumerate(trainloader):
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()

            outputs = net(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss
            total += labels.size(0)
            correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
            if batch_idx % 100 == 0:
                print(f"Image number {total} of {len(trainloader.dataset)}", end="\r", flush=True)

            epoch_loss /= len(trainloader.dataset)
            epoch_acc = correct / total
        print(f"Epoch {epoch+1}: train loss {epoch_loss}, accuracy {epoch_acc}", end="\r", flush=True)


def evaluate_model(model: torch.nn.Module, testloader: DataLoader, criterion: torch.nn.Module, device: torch.device) -> tuple[float, float]:
    model.eval()
    correct = 0
    total = 0
    running_loss = 0.0
    criterion_instance = criterion()
    with torch.no_grad():
        for data in testloader:
            images, labels = data
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion_instance(outputs, labels)
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    accuracy = correct / total
    loss = running_loss / len(testloader)
    return accuracy, loss