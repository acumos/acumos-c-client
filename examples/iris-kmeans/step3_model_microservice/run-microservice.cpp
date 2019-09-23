/* ===================================================================================
 * Copyright (C) 2019 Fraunhofer Gesellschaft. All rights reserved.
 * ===================================================================================
 * This Acumos software file is distributed by Fraunhofer Gesellschaft
 * under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * This file is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ===============LICENSE_END=========================================================
 */
#include "../dkm/include/dkm.hpp"
#include "../dkm/include/dkm_utils.hpp"
#include "model.grpc.pb.h"
#include "model.pb.h"
#include "../step2_serialize_model/centroids.pb.h"

#include <grpcpp/server_builder.h>
#include <grpcpp/server.h>
#include <grpcpp/security/server_credentials.h>
#include <vector>
#include <array>
#include <tuple>
#include <string>
#include <iterator>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <chrono>
#include <numeric>
#include <regex>
using namespace std;
using namespace cppservice;
using namespace cppsample;
using namespace grpc;


class IrisModelImpl final : public cppservice::Model::Service {

	vector<array<float, 4>> means=vector<array<float, 4>>(3);

public:

	// deserialize model from step 2
	void load_model() {
		string model_file = "data/iris-model.bin";
		fstream input(model_file, ios::in | ios::binary);
		CentroidList centroids;
		centroids.ParseFromIstream(&input);
		for (int i = 0; i < 3; i++) {
			Centroid centroid = centroids.centroid(i);
			means[i][0] = centroid.sepal_length();
			means[i][1] = centroid.sepal_width();
			means[i][2] = centroid.petal_length();
			means[i][3] = centroid.petal_width();

			print_centroid(centroid);
		}
		cout << "model successfully loaded from " << model_file << endl;

		// check if model is working
		auto cluster_index = dkm::predict<float, 4>(means, { 5.1, 3.5, 1.4, 0.2 });
		cout << "data point classified as cluster " << cluster_index << endl;
	}

	// implement/override service method from generated grpc stub
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

private:

	void print_centroid(Centroid centroid) {
		cout << "sepal_length: " << centroid.sepal_length() << endl;
		cout << "sepal_width: " << centroid.sepal_width() << endl;
		cout << "petal_length: " << centroid.petal_length() << endl;
		cout << "petal_width: " << centroid.petal_width() << endl;
		cout << endl;
	}


};



char* getCmdOption(char ** begin, char ** end, const string & option) {
    char ** itr = find(begin, end, option);
    if (itr != end && ++itr != end) {
        return *itr;
    }
    return 0;
}


int main(int argc, char **argv) {
	cout << "loading model..." << endl;
	IrisModelImpl iris_model;
	iris_model.load_model();

	string port("8334");
	char* portptr=getCmdOption(argv, argv + argc, "-p");
	if(portptr) { port=portptr; }
	string server_address("0.0.0.0:"+port);
	ServerBuilder builder;
	builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
	builder.RegisterService(&iris_model);
	unique_ptr<Server> server(builder.BuildAndStart());
	cout << endl << "Server listening on " << server_address << endl;
	server->Wait();

	return 0;
}

