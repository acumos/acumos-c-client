cmake_minimum_required (VERSION 2.6)

project (iris-kmeans LANGUAGES CXX)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_executable(iris-kmeans src/iris-kmeans.cpp)

add_executable(bench src/bench.cpp)

add_executable(simple src/simple.cpp)
