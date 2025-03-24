#!/bin/bash

NUM_CLIENTS=${NUM_CLIENTS:-1}

for i in $(seq 1 $NUM_CLIENTS); do
    NODE_LABEL="puppeteer-client-$$-$i"
    node headless/script.js http://localhost:31013/flwr-cec/client --name $NODE_LABEL &
done

wait