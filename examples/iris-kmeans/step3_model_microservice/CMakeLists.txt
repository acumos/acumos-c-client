cmake_minimum_required (VERSION 2.8)

project (iris-kmeans LANGUAGES CXX)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

execute_process(COMMAND protoc --cpp_out=. model.proto)
execute_process(COMMAND protoc --grpc_out=. --plugin=protoc-gen-grpc=/usr/local/bin/grpc_cpp_plugin model.proto)

execute_process(COMMAND protoc --python_out=. model.proto)
execute_process(COMMAND protoc --grpc_out=. --plugin=protoc-gen-grpc=/usr/local/bin/grpc_python_plugin model.proto)

add_executable(run-microservice run-microservice.cpp model.grpc.pb.cc model.pb.cc ../step2_serialize_model/centroids.pb.cc)
target_link_libraries(run-microservice protobuf grpc++ grpc++_reflection pthread)

