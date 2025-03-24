import flwr as fl
import torch
import os
import requests
import numpy as np
from numpy import ndarray
import json
from train import train_local, evaluate_model 
from model import get_model
from dataset import get_mnist_custom_dataset
from torch.utils.data import random_split
import requests
import json

times = []

def numpyclient_fn(client_id, trainloader, valloader, net, epochs, criterion, optimizer, webserver_url, dataset_size):

    class FlowerClient(fl.client.NumPyClient):
        def __init__(self, cid, trainloader, valloader, net, epochs, criterion, optimizer, webserver_url, dataset_size) -> None:
            self.cid = cid
            self.trainloader = trainloader
            self.valloader = valloader
            self.net = net
            self.epochs = epochs
            self.criterion = criterion
            self.optimizer = optimizer
            self.webserver = webserver_url
            self.local_dataset_size =  dataset_size
            self.batch_size = 64
            self.init_datasets()

        def init_datasets(self):
            self.local_dataset = self.get_local_dataset()
            lengths = [int(len(self.local_dataset) * 0.8), int(len(self.local_dataset) * 0.2)]
            trainset, testset = random_split(self.local_dataset, lengths)

            trainloader = torch.utils.data.DataLoader(trainset, batch_size=self.batch_size, shuffle=True)
            valloader = torch.utils.data.DataLoader(testset, batch_size=self.batch_size, shuffle=False)

            self.set_train_loader(trainloader)
            self.set_val_loader(valloader)


        def set_local_dataset_size(self, dataset_size):
            self.local_dataset_size = dataset_size

        def get_local_dataset_size(self):
            return self.local_dataset_size    

        def get_train_loader(self) -> torch.utils.data.DataLoader:
            return self.trainloader

        def set_train_loader(self, trainloader):
            self.trainloader = trainloader

        def get_val_loader(self) -> torch.utils.data.DataLoader:
            return self.valloader

        def set_val_loader(self, valloader):
            self.valloader = valloader

        def get_local_dataset(self) -> torch.utils.data.Dataset:
            response = requests.get(f"http://{self.webserver}:31013/dataset/mnist/train/iid/300")
            dataset_dict_str = json.loads(response.text)
            dataset_dict = json.loads(dataset_dict_str)
            datas = dataset_dict["data"]

            images_tensor = [torch.Tensor(image) for image in datas['images']]

            dataset = get_mnist_custom_dataset(images_tensor, datas['labels'])
            return dataset

        def get_parameters(self, config: torch.Dict[str, bool | bytes | float | int | str]) -> torch.List[ndarray[torch.Any, np.dtype[torch.Any]]]:
            params_array = [param.cpu().detach().numpy() for param in model.parameters()]

            new_params_array = []
            for param in params_array:
                new_params_array.append(param.T.reshape(-1, 1).squeeze())

            return new_params_array

        def set_parameters(self, parameters):
            new_state_dict = {}
            old_state_dict = self.net.state_dict()
            for param, dict_keys in zip(parameters, old_state_dict.keys()):
                new_state_dict[dict_keys] = torch.Tensor(param.reshape(old_state_dict[dict_keys].shape))

            self.net.load_state_dict(new_state_dict)

        def fit(self, parameters, config):
            self.init_datasets()

            self.set_parameters(parameters)
            train_local(self.net, self.trainloader, self.epochs,
                    self.criterion, self.optimizer, torch.device("cpu"))

            parameters = self.get_parameters({})
            return parameters, len(self.trainloader), {}

        def evaluate(self, parameters, config):
            accuracy, loss = evaluate_model(self.net, self.valloader, self.criterion, torch.device("cpu"))
            diz = {"accuracy": accuracy}
            return loss, len(self.valloader), diz

    return FlowerClient(client_id, trainloader, valloader, net, epochs, criterion, optimizer, webserver_url, dataset_size)

def new_client_flwr(client_id, model_used, trainloaders, valloaders):     
    epochs = 5
    criterion = torch.nn.CrossEntropyLoss
    optimizer = torch.optim.Adam(model_used.parameters(), lr=0.001)

    fl_client = numpyclient_fn(client_id, None, None, model_used, epochs, criterion, optimizer, webserver, 300)
    return fl_client



if __name__ == "__main__":
    server = os.environ.get("AGG_SERVER")
    port = os.environ.get("AGG_PORT")
    model_used = os.environ.get("MODEL")
    dataset_used = os.environ.get("DATASET")
    dataset_size = os.environ.get("DATASET_SIZE")
    epochs = os.environ.get("EPOCHS")
    client_id = int(os.environ.get("CLIENT_ID"))
    webserver = os.environ.get("WEBSERVER")

    model = get_model(model_used)
    fl_client = new_client_flwr(client_id, model, None, None)
    fl.client.start_client(server_address=f"{server}:{port}",
                           client=fl_client)

