# ===================================================================================
# Copyright (C) 2019 Fraunhofer Gesellschaft. All rights reserved.
# ===================================================================================
# This Acumos software file is distributed by Fraunhofer Gesellschaft
# under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============LICENSE_END=========================================================

cmake_minimum_required (VERSION 2.8)

SET(EXECUTABLE_OUTPUT_PATH bin)
project (iris-kmeans)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
add_executable (iris-kmeans src/iris-kmeans.cpp)
add_executable (bench src/bench.cpp)
add_executable (simple src/simple.cpp)
# destination is relative to CMAKE_INSTALL_PREFIX
install (TARGETS iris-kmeans DESTINATION bin)

