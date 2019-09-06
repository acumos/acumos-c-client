1. build and install protobuf
- download latest protof 3 distribution from https://github.com/protocolbuffers/protobuf/releases
- unzip and cd into it
- then as root do

./configure --disable-shared
make install
ldconfig

now you have a protobuf install under /usr/local

2. define the dataformat of your trained model 
- create a protobuf definition like in centroids.proto and generate cpp

protoc --cpp_out=. centroids.proto 

3. extend your training program to write the trained model to a file

the two examples to load and save the iris model must be run from the iris-kmeans directory 
to get all file paths right: they expect the data directory in the cwd and will write the
model to data/iris-model.bin

