import argparse
import os

network = os.environ.get("NETWORK")

total_clients = os.environ.get("SERVER_SIDE_CLIENTS")
server = os.environ.get("AGG_SERVER")
server_port = os.environ.get("SERVER_PORT")
dataset = os.environ.get("DATASET")
model = os.environ.get("MODEL")
epochs = os.environ.get("EPOCHS")

argparser = argparse.ArgumentParser()
argparser.add_argument("--output", type=str, default=".")

def create_docker_compose():
    docker_compose_content = f"""
version: '3'
services:
"""
    for i in range(1, int(total_clients) + 1):
        docker_compose_content += f"""
  client{i}:
    container_name: flwr-cec-pytorch-client-{i}
    image: flwr-cec-client-pytorch
    volumes:
      - .:/app
    environment:
      container_name: flwr-cec-pytorch-client-{i}
      AGG_SERVER: {server}
      WEBSERVER: flwr-cec-webserver
      AGG_PORT: {server_port}
      MODEL: {model}
      DATASET: {dataset}
      EPOCHS: {epochs}
      CLIENT_ID: {i}
    
    networks:
      - {network}
"""

    docker_compose_content += f"networks:\n  {network}:\n    external: true\n"

    path_docker_compose = argparser.parse_args().output

    with open(f"{path_docker_compose}/docker-compose.yml", "w") as file:
        file.write(docker_compose_content)


if __name__ == "__main__":
    create_docker_compose() 