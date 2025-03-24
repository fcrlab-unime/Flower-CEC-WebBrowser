import flwr as fl
import os
import requests
import numpy as np
import json

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
    
def http_remote_call(client_id, vpod_name, function, data):
    url = f"http://{vpod_name}/{function}"
    headers = {
                "Content-Type": "application/json",
                "X-Target-Url" : url,
                "X-Target-Path": f"/{function}",
                "X-Kleint-Sender": "flwr-vpod",
                "X-Kleint-Destination": vpod_name,
                "X-Kleint-Session-Destination": client_id
            }
    
    response = requests.request("POST", f"http://flwr-cec-kleint-gateway:11355/{function}", 
                                headers=headers,
                                data=json.dumps(data, cls=NumpyEncoder)
                                )
    return response.json()['Message']['Body']

def numpyclient_fn(client_id, vpod_name):
    
    class NumpyClient(fl.client.NumPyClient):
        def __init__(self, client_id, vpod_name):
            self.client_id = client_id
            self.vpod_name = vpod_name

        def get_parameters(self, config):
            response = http_remote_call(self.client_id, self.vpod_name, "getParameters", {})
            params = response['params']
            list_params = np.asarray(params, dtype="object")
            return list_params

        def fit(self, parameters, config):
            data = {
                "modelWeights": parameters,
            }   
            response_fit = http_remote_call(self.client_id, self.vpod_name, "fit", data)

            parameters_response = response_fit["weights"]
            length = response_fit["length"]
            return parameters_response, int(length), {}

        def evaluate(self, parameters, config):
            response = http_remote_call(self.client_id, self.vpod_name, "evaluate", {})
            return response['loss'], response['length'], {}

    return NumpyClient(client_id, vpod_name)

def new_client_flwr(client_id): 
    server = os.environ.get("AGG_SERVER")
    port = os.environ.get("AGG_PORT")
    vpod_name = "flwr-client"
    
    fl_client = numpyclient_fn(client_id, vpod_name)
    fl.client.start_client(server_address=f"{server}:{port}",
                           client=fl_client)
    