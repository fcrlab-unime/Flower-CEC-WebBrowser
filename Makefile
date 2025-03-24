.PHONY: help docker-deploy docker-restart docker-remove k8s-generate-cm k8s-deploy k8s-restart k8s-remove build flwr-cec flwr-cec-aggregator flwr-cec-clients flwr-cec-evaluator datasets-server download-datasets download-mnist download-cifar10 models models-dnn models-cnn

DOWNLOAD_PATH=$${PWD}/datasets/download

define gen_cm
	sed -E 's/[[:space:]]+$$//g' $(3) > /tmp/$(5); \
	kubectl create cm $(1) --from-file=/tmp/$(5) --dry-run=client -n=flwr-cec -o yaml > /tmp/$(1).1.flwr-cec.tmp && \
	kubectl annotate --local -f /tmp/$(1).1.flwr-cec.tmp  use-subpath="true" --dry-run=client -o yaml > /tmp/$(1).2.flwr-cec.tmp && \
	kubectl label --local -f /tmp/$(1).2.flwr-cec.tmp  app=$(2) --dry-run=client -o yaml > $(4) && \
	rm /tmp/$(5); \
	rm /tmp/*.flwr-cec.tmp
endef

help:
	@printf "\n"
	@printf "%-25s %-25s\n" "flwr-cec - Federated Learning Across Tabs" ""
	@printf "%-25s %-25s\n" "_____________________________________" ""
	@printf "\n"
	@printf "%-25s %-25s\n" "Usage: make [command]" ""
	@printf "\n"
	@printf "%-25s %-25s\n" "Commands:" ""
	@printf "\n"
	@printf "%-25s %-25s\n" "build" "Build all flwr-cec architecture services"
	@printf "\n"
	@printf "%-25s %-25s\n" "run" "Deploy flwr-cec architecture"
	@printf "%-25s %-25s\n" "restart" "Restart flwr-cec architecture"
	@printf "%-25s %-25s\n" "stop" "Remove flwr client vpod and aggregator"
	@printf "%-25s %-25s\n" "remove" "Remove flwr-cec architecture"
	@printf "\n"
	@printf "%-25s %-25s\n" "deploy-clients" "Deploy server-side Flower Clients"
	@printf "%-25s %-25s\n" "remove-clients" "Remove server-side Flower Clients"
	@printf "%-25s %-25s\n" "restart-clients" "Restart server-side Flower Clients"
	@printf "\n"
	@printf "%-25s %-25s\n" "flwr-cec-clients" "Build Flower Client CEC"
	@printf "\n"
	@printf "%-25s %-25s\n" "download-datasets" "Download MNIST and CIFAR-10 datasets"
	@printf "\n"
	@printf "%-2s %-22s %-25s\n" "" "download-mnist" "Download MNIST dataset"
	@printf "\n"
	@printf "%-25s %-25s\n" "datasets-server" "Build datasets-server Docker image"
	@printf "\n"
	@printf "%-25s %-25s\n" "models" "Build models"
	@printf "\n"
	@printf "%-2s %-22s %-25s\n" "" "models-dnn" "Build DNN models"
	@printf "\n"


run:
	@echo "\033[0;32m[DOCKER-COMPOSE] Deploying Flower CEC architecture\033[0m"
	DOCKER_COMPOSE=deploy/docker-compose.yml; \
	DOCKER_COMPOSE_FL_FEDAVG=deploy/docker-compose.flwr-cec.yml; \
	docker compose -f $$DOCKER_COMPOSE -f $$DOCKER_COMPOSE_FL_FEDAVG up -d && \
	make deploy-clients && \
	echo "\033[0;32m[DOCKER-COMPOSE] Deploy completed successfully\033[0m" || \
	echo "\033[0;31m[DOCKER-COMPOSE] Deploy failed\033[0m"

restart:
	@echo "\033[0;32m[DOCKER-COMPOSE] Restarting Flower CEC architecture\033[0m"
	DOCKER_COMPOSE=deploy/docker-compose.yml; \
	DOCKER_COMPOSE_FL_FEDAVG=deploy/docker-compose.flwr-cec.yml; \
	docker compose -f $$DOCKER_COMPOSE -f $$DOCKER_COMPOSE_FL_FEDAVG restart && \
	make deploy-restart && \
	echo "\033[0;32m[DOCKER-COMPOSE] Restarting completed successfully\033[0m" || \
	echo "\033[0;31m[DOCKER-COMPOSE] Restarting failed\033[0m"

remove:
	@echo "\033[0;32m[DOCKER-COMPOSE] Removing Flower CEC architecture\033[0m"
	DOCKER_COMPOSE=deploy/docker-compose.yml; \
	DOCKER_COMPOSE_FL_FEDAVG=deploy/docker-compose.flwr-cec.yml; \
	docker compose -f $$DOCKER_COMPOSE -f $$DOCKER_COMPOSE_FL_FEDAVG down -t 0 && \
	make remove-clients && \
	echo "\033[0;32m[DOCKER-COMPOSE] Removing completed successfully\033[0m" || \
	echo "\033[0;31m[DOCKER-COMPOSE] Removing failed\033[0m"

stop:
	@echo "\033[0;32m[DOCKER-COMPOSE] Removing Flower CEC architecture\033[0m"
	DOCKER_COMPOSE_FL_FEDAVG=deploy/docker-compose.flwr-cec.yml; \
	docker compose -f $$DOCKER_COMPOSE_FL_FEDAVG down -t 0 && \
	make remove-clients && \
	echo "\033[0;32m[DOCKER-COMPOSE] Removing completed successfully\033[0m" || \
	echo "\033[0;31m[DOCKER-COMPOSE] Removing failed\033[0m"

deploy-clients:
	@echo "\033[0;32m[GENERATE-SCRIPT] Generation Docker Compose Manifest\033[0m"
	set -a; . examples/flwr-client-pytorch/.env; set +a; \
	set -a; . ./.env; set +a; \
	PYTHON_GENERATION=examples/flwr-client-pytorch/generate_docker_compose.py; \
	DOCKER_COMPOSE_PATH=examples/flwr-client-pytorch; \
	python3 $$PYTHON_GENERATION --output $$DOCKER_COMPOSE_PATH && \
	DOCKER_COMPOSE=examples/flwr-client-pytorch/docker-compose.yml; \
	docker compose -f $$DOCKER_COMPOSE up -d --remove-orphans && \
	echo "\033[0;32m[DOCKER-COMPOSE] Deploy completed successfully\033[0m" || \
	echo "\033[0;31m[DOCKER-COMPOSE] Deploy failed\033[0m"

remove-clients:
	@echo "\033[0;32m[DOCKER-COMPOSE] Removing Flower Clients\033[0m"
	DOCKER_COMPOSE=examples/flwr-client-pytorch/docker-compose.yml; \
	docker compose -f $$DOCKER_COMPOSE down -t 0 && \
	rm $$DOCKER_COMPOSE && \
	echo "\033[0;32m[DOCKER-COMPOSE] Removing completed successfully\033[0m" || \
	echo "\033[0;31m[DOCKER-COMPOSE] Removing failed\033[0m"

restart-clients:
	@echo "\033[0;32m[DOCKER-COMPOSE] Restarting Flower Clients\033[0m"
	DOCKER_COMPOSE=examples/flwr-client-pytorch/docker-compose.yml; \
	docker compose -f $$DOCKER_COMPOSE restart && \
	echo "\033[0;32m[DOCKER-COMPOSE] Restarting completed successfully\033[0m" || \
	echo "\033[0;31m[DOCKER-COMPOSE] Restarting failed\033[0m"

build: datasets-server flwr-cec-aggregator flwr-vpod flwr-cec-clients

flwr-vpod:
	@echo "\033[0;32m[BUILD] Building Flower-Client VPod container image\033[0m"
	docker build -t flwr-vpod ./src/flwr-vpod

flwr-cec-aggregator:
	@echo "\033[0;32m[BUILD] Building Flower-Client VPod container image\033[0m"
	docker build -t flwr-cec-aggregator ./examples/flwr-aggregator

flwr-cec-clients: flwr-cec-client-ort flwr-cec-client-tf flwr-cec-client-pytorch

flwr-cec-client-ort:
	DIRECTORY=examples/flwr-cec-web; \
	CONTAINER_NAME=flwr-cec-build-client-$$(date +%s) && \
	docker run -it --name $$CONTAINER_NAME --rm \
		-v $${PWD}/examples/flwr-cec-web/src/microservices:/app \
		-v $${PWD}/examples/flwr-cec-web/dist/microservices:/dist \
		node:18 /bin/sh -c "cd app/ && make build-client-ort"

flwr-cec-client-tf:
	DIRECTORY=examples/flwr-cec-web; \
	CONTAINER_NAME=flwr-cec-build-client-$$(date +%s) && \
	docker run -it --name $$CONTAINER_NAME --rm \
		-v $${PWD}/examples/flwr-cec-web/src/microservices:/app \
		-v $${PWD}/examples/flwr-cec-web/dist/microservices:/dist \
		node:18 /bin/sh -c "cd app/ && make build-client-tf"

flwr-cec-client-pytorch:
	@echo "\033[0;32m[BUILD] Building Flower-Client Pytorch image \033[0m"
	docker build -t flwr-cec-client-pytorch ./examples/flwr-client-pytorch

download-datasets: download-mnist download-cifar10

download-mnist:
	@echo "\033[0;32m[DATASETS] Downloading MNIST dataset\033[0m"
	@mkdir -p $(DOWNLOAD_PATH)/mnist
	@wget https://ossci-datasets.s3.amazonaws.com/mnist/train-images-idx3-ubyte.gz -O $(DOWNLOAD_PATH)/mnist/train-images-idx3-ubyte.gz
	@wget https://ossci-datasets.s3.amazonaws.com/mnist/train-labels-idx1-ubyte.gz -O $(DOWNLOAD_PATH)/mnist/train-labels-idx1-ubyte.gz
	@wget https://ossci-datasets.s3.amazonaws.com/mnist/t10k-images-idx3-ubyte.gz -O $(DOWNLOAD_PATH)/mnist/t10k-images-idx3-ubyte.gz
	@wget https://ossci-datasets.s3.amazonaws.com/mnist/t10k-labels-idx1-ubyte.gz -O $(DOWNLOAD_PATH)/mnist/t10k-labels-idx1-ubyte.gz
	@gunzip $(DOWNLOAD_PATH)/mnist/*.gz

datasets-server:
	@echo "\033[0;32m[DATASETS-SERVER] Building Docker image\033[0m"
	IMAGE_NAME=ghcr.io/fcrlab-unime/flwr-cec-datasets-server:latest; \
	DOCKERFILE_PATH=extra/datasets-server/Dockerfile; \
	CONTEXT_DIR=extra/datasets-server; \
	docker build --platform=linux/amd64 -t $$IMAGE_NAME -f $$DOCKERFILE_PATH $$CONTEXT_DIR && \
	echo "\033[0;32m[DATASETS-SERVER] Build completed successfully\033[0m" || \
	echo "\033[0;31m[DATASETS-SERVER] Build failed\033[0m"

models:
	DIRECTORY=examples/flwr-cec-web; \
	CONTAINER_NAME=flwr-cec-onnx-builder && \
	docker build -t $$CONTAINER_NAME $${PWD}/examples/flwr-cec-web/src/models && \
	docker run --platform=linux/amd64 -it --name $$CONTAINER_NAME --rm \
		-v $${PWD}/examples/flwr-cec-web/src/models:/app \
		-v $${PWD}/examples/flwr-cec-web/dist/models:/dist \
		$$CONTAINER_NAME /bin/sh -c "make build"

models-dnn:
	DIRECTORY=examples/flwr-cec-web; \
	CONTAINER_NAME=flwr-cec-onnx-builder && \
	docker build -t $$CONTAINER_NAME $${PWD}/examples/flwr-cec-web/src/models && \
	docker run --platform=linux/amd64 -it --name $$CONTAINER_NAME --rm \
		-v $${PWD}/examples/flwr-cec-web/src/models:/app \
		-v $${PWD}/examples/flwr-cec-web/dist/models:/dist \
		$$CONTAINER_NAME /bin/sh -c "make build-dnn"