cmake_minimum_required (VERSION 2.8)

project (iris-kmeans LANGUAGES CXX)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_executable(save-iris-kmeans save-iris-kmeans.cpp centroids.pb.cc)
target_link_libraries(save-iris-kmeans protobuf)

add_executable(load-iris-kmeans load-iris-kmeans.cpp centroids.pb.cc)
target_link_libraries(load-iris-kmeans protobuf)
