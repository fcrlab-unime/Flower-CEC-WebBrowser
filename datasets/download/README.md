# Download Datasets

 ```
# Alternative source for MNIST dataset
wget https://ossci-datasets.s3.amazonaws.com/mnist/train-images-idx3-ubyte.gz -O train-images-idx3-ubyte.gz
wget https://ossci-datasets.s3.amazonaws.com/mnist/train-labels-idx1-ubyte.gz -O train-labels-idx1-ubyte.gz
wget https://ossci-datasets.s3.amazonaws.com/mnist/t10k-images-idx3-ubyte.gz -O t10k-images-idx3-ubyte.gz
wget https://ossci-datasets.s3.amazonaws.com/mnist/t10k-labels-idx1-ubyte.gz -O t10k-labels-idx1-ubyte.gz

gunzip *.gz
 ```