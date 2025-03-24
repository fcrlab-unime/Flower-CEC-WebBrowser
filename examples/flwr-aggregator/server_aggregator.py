import flwr as fl
import os

FRACTION = float(os.environ['FRACTION'])
NUM_CLIENTS = int(os.environ['NUM_CLIENTS'])
NUM_ROUNDS = int(os.environ['NUM_ROUNDS'])

class CustomStrategy(fl.server.strategy.FedAvg):
    def on_conclude(self, server_state):
        metrics = server_state.metrics

        # Write logic here if you want to store the metrics
        
        super().on_conclude(server_state)

strategy = CustomStrategy(
    fraction_fit=FRACTION,  # Fraction of clients used during training
    min_fit_clients=NUM_CLIENTS,  # Minimum number of clients to be used for training
    min_available_clients=NUM_CLIENTS,  # Minimum number of total clients in the system
)

if __name__ == "__main__":
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        strategy=strategy,
        config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
    )
