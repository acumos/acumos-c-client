.. ===============LICENSE_START=======================================================
.. Acumos CC-BY-4.0
.. ===================================================================================
.. Copyright (C) 2019 Fraunhofer Gesellschaft. All rights reserved.
.. ===================================================================================
.. This Acumos documentation file is distributed by <YOUR COMPANY NAME>
.. under the Creative Commons Attribution 4.0 International License (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..      http://creativecommons.org/licenses/by/4.0
..
.. This file is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
.. ===============LICENSE_END=========================================================
.. PLEASE REMEMBER TO UPDATE THE LICENSE ABOVE WITH YOUR COMPANY NAME AND THE CORRECT YEAR
.. If your component has a UI or needs to be configured, your component may need a User Guide.
.. Most Acumos components WILL NOT need a User Guide
.. User guide content guidelines:
.. if the guide contains sections on third-party tools, is it clearly stated why the Acumos platform is using .. .. those tools? are there instructions on how to install and configure each tool/toolset?
.. does the guide state who the target users are? for example, modeler/data scientist, Acumos platform admin, .. .. marketplace user, design studio end user, etc
.. if there are instructions, they are clear, correct, and fit for purpose
.. does the guide contain information more suited for a different guide?
.. a user guide should be how to use the component or system; it should not be a requirements document
.. a user guide should contain configuration, administration, management, using, and troubleshooting sections for .. the feature.

.. _user-guide-template:

============================
Acumos C++ Client User Guide
============================

Target Users
============
The target users of this guide are modelers with sufficient C++ to write and build C++ applications.

Overview
========

This guide will describe the steps needed to onboard a c++ model using a tutorial where the provided
example iris-classifier is prepared to be onboarded. Basically the following steps are needed:
1. Train the model
2. Create the serialized model
3. Define the gRPC service
4. Create service executable
5. Create the bundles for onboarding


Architecture
============
In Acumos a model is packed as a dockerized microservice exposing which is specified using Google protobuf.
In order to achieve that, the modeler must write a short C++ program that attaches the trained model with
the generated gRPC stub in order to build an executable that contains the gRPC webserver as well as the
trained model. This executable will then be started in the docker container.

The minimum C++ standard level is **C++11** and the recommended compiler is **gcc 7.4**


Tutorial
========

Onboarding the Iris Kmeans Classifier
---------------

Overview
^^^^^^^^

In the examples directory contains the complete steps to onboard the well known Iris Classifier using
a KMeans implementation

Prerequisites
^^^^^^^^^^^^^

The examples was developed in the following environment:
* Ubuntu 18.04
* g++ 7.4 (default version on Ubuntu 18.04)
* gRPC 1.20, should be installed from source (https://github.com/grpc/grpc) into /usr/local including all plugins
* python 3.6
* cmake

In the text all we assume that you are in the directory examples/iris-kmeans.

Step 1: Train model
^^^^^^^^^^^^^^^^^^^

The file **src/iris-kmeans.cpp** trains the iris classifier model by finding a centroid for each of the
three iris species. The classify method then finds the closest centroid to the given data point and returns
it as the most probable species. Thus in this case, the three centroids make up the trained model.

Step 2: Serialize trained model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The targeted microservice needs to load the serialized trained model at startup. It is completely up to the
developer how this is done. The example uses protobuf, because it fits in the technology lineup of the
whole example. To save and load the trained model, the example uses a protobuf definition the can be found in
**step2_serialize_model/centroids.proto**:

.. code:: java
    syntax = "proto3";
    package cppsample;

    message Centroid {
      float sepal_length = 1;
      float sepal_width = 2;
      float petal_length = 3;
      float petal_width = 4;
    }

    message CentroidList {
      repeated Centroid centroid = 1;
    }

Then, generate the respective c++ code using the protobuf compiler:

.. code:: bash

    protoc --cpp_out=. centroids.proto

An use a small code snippet to save the data to a file:

.. code:: c++

    string model_file="data/iris-model.bin";
    fstream output(model_file, ios::out | ios::binary);
    centroids.SerializePartialToOstream(&output);

The two examples to load and save the iris model must be run from the iris-kmeans directory
to get all file paths right: they expect the data directory in the cwd and will write the
model to data/iris-model.bin

Step 3: Create Microservice
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The microservice must be implemented and at first read the serialized model from step2. The example
implementation can be found in the file **run-microservice.cpp**.

Then, the service interface of the microservice must be specified using protobuf. In our example, it is the
classify method with its input and output parameters must be defined in a file that should be named **model.proro**:

.. code:: java

    syntax = "proto3";
    package cppservice;

    service Model {
      rpc classify (IrisDataFrame) returns (ClassifyOut);
    }

    message IrisDataFrame {
      repeated double sepal_length = 1;
      repeated double sepal_width = 2;
      repeated double petal_length = 3;
      repeated double petal_width = 4;
    }

    message ClassifyOut {
      repeated int64 value = 1;
    }

From this file, the necessary code fragments and gRPC stubs can the be generated like this:

.. code:: bash

    protoc --cpp_out=. model.proto
    protoc --grpc_out=. --plugin=protoc-gen-grpc=/usr/local/bin/grpc_cpp_plugin model.proto

After that, the gRPC service method has to be implemented:

.. code:: c++

    Status classify(ServerContext *context, const IrisDataFrame *input, ClassifyOut *response) override {
        cout << "enter classify service" << endl;
        std::array<float, 4> query;
        query[0]=input->sepal_length(0);
        query[1]=input->sepal_width(0);
        query[2]=input->petal_length(0);
        query[3]=input->petal_width(0);
        auto cluster_index = dkm::predict<float, 4>(means, query);
        cout << "data point classified as cluster " << cluster_index << endl;
        response->add_value(cluster_index);

        return Status::OK;
    }

And finally, the gRPC server has to be started:

.. code:: c++

    string server_address("0.0.0.0:"+port);
    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&iris_model);
    unique_ptr<Server> server(builder.BuildAndStart());
    cout << endl << "Server listening on " << server_address << endl;
    server->Wait();


To prepare for packaging, to specific folders will be expected:
1. the **data** folder, where all files of the serialized model are stored
2. the **lib** folder that should contain the shared libraries that are not part of the g++ base installation 

Step 4: Create Onboarding Bundle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the last step, the onboarding bundle for web-onboarding will be created using the **cpp-client.py** script.
It should be called from the model's base directory, in this case iris-kmeans. The script asks several questions
and please note that for files and paths, normal tab-completion is possible. The script generates all artefacts
into the **onboarding** directory and specifically the file ending with **-bundle.zip** is the one that is ready
for web onboarding.

Step 5: Onboarding by CLI
^^^^^^^^^^^^^^^^^^^^^^^^^

When onboarding by CLI with microservice creation is successfull, the Acumos model docker URI will
be displayed at the end of on-boarding. You can use it to load the docker image in your own docker repository.


