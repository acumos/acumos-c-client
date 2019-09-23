first, grpc must be installed like this (possibly as root)

git clone -b $(curl -L https://grpc.io/release) https://github.com/grpc/grpc
git submodule update --init

this example was build with grpc 1.20 and assumes all grpc files have been imstalled under in /usr/local

further, it is assumed that step2 has been completed and run successfully

the modeler must write the model.proto file for her service.

then run "cmake ." which also calls the protoc to generate the grpc stubs  

the microservice is implemented in run-microservice.cpp which loads the model and starts the grpc service. the modeler has to implement the method classify from the generated grpc service. in this example, the executbale should be run from the example base directory like this:  ./step3_model_microservice/bin/run-microservice

the python is script optional to test the grpc service
  


