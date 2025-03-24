.PHONY: build build-client-ort build-client-tf

CLIENT_DIR=/app/flwr-client-web-ort
CLIENT_TF_DIR=/app/flwr-client-web-tf
TEMP_DIR=/tmp

build-client-ort:
	@echo "Building client..."
	@cp -rT $(CLIENT_DIR) $(TEMP_DIR)/client
	@cd $(TEMP_DIR)/client && npm install && npm run build
	@cp -rT $(TEMP_DIR)/client/dist /dist/flwr-client-web-ort

build-client-tf:
	@echo "Building client TF..."
	@cp -rT $(CLIENT_TF_DIR) $(TEMP_DIR)/client
	@cd $(TEMP_DIR)/client && npm install && npm run build
	@cp -rT $(TEMP_DIR)/client/dist /dist/flwr-client-web-tf
