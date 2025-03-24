import tensorflow as tf
import numpy as np
import requests
import json
import flwr as fl
import os
import time
import datetime


times = []
input_size = 784
hidden_size = 200
num_classes = 10
url = "http://flwr-cec-webserver:31013/dataset/mnist/train/iid/1000"

class DNN(tf.keras.Model):
    def __init__(self, input_size, hidden_size, num_classes):
        super(DNN, self).__init__()
        self.fc1 = tf.keras.layers.Dense(hidden_size, activation='relu')
        self.fc2 = tf.keras.layers.Dense(hidden_size, activation='relu')
        self.fc3 = tf.keras.layers.Dense(num_classes, activation=None)

    def call(self, inputs):
        x = self.fc1(inputs)
        x = self.fc2(x)
        output = self.fc3(x)
        return output

model = DNN(input_size, hidden_size, num_classes)

dummy_input = np.zeros((1, input_size))
model(dummy_input)

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

time.sleep(5)

def get_mnist_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 
        dataset = response.json()
        dataset = json.loads(dataset)
        images = np.array(dataset['data']['images']).astype(np.float32)
        labels = np.array(dataset['data']['labels']).astype(np.int32)
        return images, labels
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get data from {url}: {e}")

images, labels = get_mnist_data(url)
images = images / 255.0

def get_model_parameters():
    array = [tf.reshape(val, (-1, 1)).numpy().squeeze() for val in model.trainable_variables]
    for a in array:
        print(len(a))
    return array

def set_model_parameters(parameters):
    for var, param in zip(model.trainable_variables, parameters):
        param_array = np.array(param)
        reshaped_param = tf.reshape(param_array, var.shape)
        var.assign(reshaped_param)



class NumpyClient(fl.client.NumPyClient):
    def __init__(self, client_id, vpod_name):
        self.client_id = client_id
        self.vpod_name = vpod_name

    def get_parameters(self, config):
        parameters = get_model_parameters()
        return parameters

    def fit(self, parameters, config):
        start_time = datetime.datetime.now()
        set_model_parameters(parameters)
        model.fit(images, labels, epochs=5, batch_size=32, verbose=2)
        end_time = datetime.datetime.now()
        times.append((end_time - start_time).microseconds / 1000.0)
        return parameters, len(images), {}

    def evaluate(self, parameters, config):
        set_model_parameters(parameters)
        loss, accuracy = model.evaluate(images, labels, verbose=2)
        return loss, len(images), {"accuracy": accuracy}

server = os.environ.get("AGG_SERVER", "localhost")
port = os.environ.get("AGG_PORT", "8080")
client_id = os.environ.get("CLIENT_ID", "0")

client = NumpyClient(client_id=client_id, vpod_name=f"flwr-client_tf_{client_id}")
fl.client.start_client(server_address=f"{server}:{port}", client=client)

