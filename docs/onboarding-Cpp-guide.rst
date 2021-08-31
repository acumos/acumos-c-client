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
The target users of this guide are modelers with sufficient C++ knowledge to write and build C++ applications.

Overview
========

This guide will describe the steps needed to onboard a c++ model. Basically the following steps are needed:

1. Train the model
2. Serialized trained model
3. Create Microservice
4. Define the gRPC service
5. Use the onboaridng-cpp client to save model_bundle locally or to onboard it to Acumos by CLI

The model_bundle is a package that contains all the necessary materials required by Acumos to on-board the
model and use it in acumos. At the end you can follow a tutorial where the provided example iris-classifier
is prepared to be onboarded.

Architecture
============

In Acumos a model is packed as a dockerized microservice exposing which is specified using Google protobuf.

In order to achieve that, the modeler must write a short C++ program that attaches the trained model with
the generated gRPC stub in order to build an executable that contains the gRPC webserver as well as the
trained model. This executable will then be started in the docker container.

The minimum C++ standard level is **C++11** and the recommended compiler is **gcc 7.4**

Prerequisites
^^^^^^^^^^^^^

The examples was developed in the following environment:

1. Ubuntu 18.04
2. g++ 7.4 (default version on Ubuntu 18.04)
3. gRPC 1.20, should be installed from source (https://github.com/grpc/grpc) into /usr/local including all plugins
4. python 3.6
5. cmake

set the two following environment variables

.. code:: bash

    export ACUMOS_HOST = my.acumos.instance.org
    export ACUMOS_PORT = my acumos port

These values can be found in the installation folder of Acumos : **system-integration/AIO/acumos_env.sh**. Please look at the
following Acumos local environement variable : ACUMOS_DOMAIN, ACUMOS_PORT or ACUMOS_ORIGIN

Tutorial : Onboard the Iris Kmeans Classifier
================================================

To perform the following steps you have to clone the repository acumos-c-client from gerrit (https://gerrit.acumos.org).
Browse the repositories to acumos-c-client then retrieve the SSH or HTTPS commands. You can clone it also from Github
(https://github.com/acumos/acumos-c-client)

In acumos-c-client repository, the "examples" directory contains the complete steps to onboard the well known Iris
Classifier using a KMeans implementation.

Add Kmeans clustering in acumos-c-client repo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After cloning the acumos-c-client repository, do the following :

.. code:: bash

    cd acumos-c-client
    git submodule update --init

This will add the DKM algorithm (A generic K-means clustering written in C++) in /examples/iris-kmeans/dkm folder.

Then you have to build basic executables

.. code:: bash

    cmake .
    make

Train the model and save it in serialized format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The targeted microservice needs to load the serialized trained model at startup. It is completely up to the
developer how this is done. The example uses protobuf, because it fits in the technology lineup of the
whole example.

First, create the protobuf model definition that will be used to save and load the trained model

.. code:: bash

    cd examples/iris-kmeans/step2_serialize_model/
    protoc --cpp_out=. centroids.proto

Then build the training binary

.. code:: bash

    cmake .
    make

and finally Train the model ans save it in serialized format

.. code:: bash

    cd ..
    ./step2_serialize_model/bin/save-iris-kmeans

The file **iris-kmeans/src/iris-kmeans.cpp** trains the iris classifier model by finding a centroid for each of the
three iris species. The classify method then finds the closest centroid to the given data point and returns
it as the most probable species. Thus in this case, the three centroids make up the trained model.

Now the model is serialized and the binary is saved in **/iris-kmeans/data/**

Create protobuf Microservice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create the protobuf Microservice do the following :

.. code:: bash

    cd step3_model_microservice/
    cmake .
    make

The microservice must be implemented and at first read the serialized model from step2. The example implementation can be found
in the file **iris-kmeans/step3_model_microservice/run-microservice.cpp**. Then, the service interface of the microservice
must be specified using protobuf. In our example, it is the classify method with its input and output parameters are defined in
**iris-kmeans/step3_model_microservice/model.proto**

launch the Acumos on-boarding cpp client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a lib directory

.. code:: bash

    cd ..
    mkdir lib

and launch the cpp client by command line if you want or with your prefered Python IDE. It is recommended to call the onboarding
script from /examples/iris-kmeans folder. You must set up an ACUMOS_TOKEN variable in cpp-client.py to be authenticated by Acumos.

.. code:: bash
   os.environ['ACUMOS_TOKEN']= 'your_acumos_login:your_Api_Token'

Your Api_token can be retrieved in your Acumos account settings by clicking on you name in the right up corner of the acumos home page.

.. code:: bash

    python3 ../../cpp-client.py



The Acumos on-boarding cpp client will ask you the follwing question :

- Name of the model
- Path to model.proto
- Path to data, lib and executable(bin) directories
- name of the dump directory (where you want to save the model bundle)
- CLI onboarding ? [yes/no]

* if no, the model bundle will be save locally in the dump directory and then you will be able to on-board it later by Web-onboarding
* if yes you must ask the following questions (if environment variable haven't been set previously, as requested in prerequisites, the cpp client will ask you to fill the values at this step)

- Do you want to create a microservice ?

* if yes, you will be prompted to answer to the following question : Do you want to deploy the microservice ? [yes/no]:
  * if yes, please refer to the appropriate documentation on Acumos Wiki to deploy the microservice.

- Do you want to add license ?

* if yes, you will be prompted to answer to the follwoing question : path to licence file :
 
- User Name (your Acumos login)
- Password (your Acumos password)

Then the on-boarding start, it will take more or less time depending if you choose to create the microservice during on-boaring or not.
Once the onboarding is finished you can retrieve your model in Acumos.


How to on-board your own model
==============================

In the follwing we describe all the steps we followed to build the previous tutorial. You must follow these steps to be able to on-board
in acumos your own C++ model.

Step 1: Train model
^^^^^^^^^^^^^^^^^^^

We assume that you have a cpp file like  **src/iris-kmeans.cpp** to train you own model.

The **src/iris-kmeans.cpp** trains the iris classifier model by finding a centroid for each of the
three iris species. The classify method then finds the closest centroid to the given data point and returns
it as the most probable species. Thus in this case, the three centroids make up the trained model.

Step 2: Serialize trained model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The targeted microservice needs to load the serialized trained model at startup. It is completely up to the
developer how this is done. The example uses protobuf, because it fits in the technology lineup of the
whole example. To save and load the trained model, the tutorial use a protobuf definition the can be found in
**step2_serialize_model/centroids.proto**:

.. code:: bash

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

In the tutotrial, the two examples to load and save the iris model must be run from the iris-kmeans directory
to get all file paths right: they expect the data directory in the cwd and will write the model to data/iris-model.bin

Step 3: Create Microservice
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The microservice must be implemented and at first read the serialized model from step2. The example
implementation can be found in the file **run-microservice.cpp**.

Then, the service interface of the microservice must be specified using protobuf. In our example, it is the
classify method with its input and output parameters must be defined in a file that should be named **model.proto**:


.. code:: bash

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


Step 4: Define gRPC service
^^^^^^^^^^^^^^^^^^^^^^^^^^^

From model.proto, the necessary code fragments and gRPC stubs can be generated like this:

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


To prepare for packaging, specific folders will be expected:

1. the **data** folder, where all files of the serialized model are stored
2. the **lib** folder that should contain the shared libraries that are not part of the g++ base installation

Step 5 : Use the onboarding-cpp client to save model_bundle locally or to onboard it to Acumos by CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please refers to tutorial to use the onboarding-cpp client.

