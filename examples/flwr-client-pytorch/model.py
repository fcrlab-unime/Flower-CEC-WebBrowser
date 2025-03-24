import torch

class CNN(torch.nn.Module):
    def __init__(self,input_channel,output_channel, num_classes):
        super(CNN, self).__init__()
        self.conv1 = torch.nn.Conv2d(input_channel, output_channel, kernel_size=3, padding=1)
        self.relu1 = torch.nn.ReLU()
        self.conv2 = torch.nn.Conv2d(output_channel, output_channel*2, kernel_size=3, padding=1)
        self.relu2 = torch.nn.ReLU()
        self.conv3 = torch.nn.Conv2d(output_channel*2, output_channel*4, kernel_size=3, padding=1)
        self.relu3 = torch.nn.ReLU()
        self.pool = torch.nn.MaxPool2d(2, 2)
        self.flatten = torch.nn.Flatten()
        self.fc1 = torch.nn.Linear(output_channel*4 * 4 * 4, 512)
        self.fc2 = torch.nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.conv1(x)   
        x = self.relu1(x)
        x = self.pool(x)
        x = self.conv2(x)
        x = self.relu2(x)
        x = self.pool(x)
        x = self.conv3(x)
        x = self.relu3(x)
        x = self.pool(x)
        x = self.flatten(x)
        x = self.relu1(x)
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)

class DNN(torch.nn.Module): # McMahan et al., 2016; 199,210 parameters
    def __init__(self):
        super(DNN, self).__init__()
        self.in_features = 28**2
        self.num_hiddens = 200
        self.num_classes = 10

        self.features = torch.nn.Sequential(
            torch.nn.Linear(in_features=self.in_features, out_features=self.num_hiddens, bias=True, dtype=torch.float32),
            torch.nn.ReLU(True),
            torch.nn.Linear(in_features=self.num_hiddens, out_features=self.num_hiddens, bias=True, dtype=torch.float32),
            torch.nn.ReLU(True)
        )
        self.classifier = torch.nn.Linear(in_features=self.num_hiddens, out_features=self.num_classes, bias=True, dtype=torch.float32)

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def get_model(model_name):
    if model_name == "cnn":
        input_size, hidden_size, output_size = 3, 32, 10
        return CNN(input_size, hidden_size, output_size)
    elif model_name == "dnn":
        return DNN()
    else:
        raise ValueError(f"Model {model_name} not supported")