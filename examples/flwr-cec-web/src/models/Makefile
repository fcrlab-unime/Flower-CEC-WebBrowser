.PHONY: build build-dnn

DNN_DIR=/app/mnist
TEMP_DIR=/tmp

build: build-dnn

build-dnn:
	@echo "Building DNN..."
	@cp -rT $(DNN_DIR) $(TEMP_DIR)/mnist
	@cd $(TEMP_DIR)/mnist && python3 compile.py --output_dir dist
	@cp -rT $(TEMP_DIR)/mnist/dist /dist/mnist