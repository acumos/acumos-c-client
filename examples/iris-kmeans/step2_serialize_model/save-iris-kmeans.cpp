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
#include "centroids.pb.h"

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
using namespace cppsample;

// split a line on commas
vector<string> split_commas(const string& line) {
	vector<string> split;
	regex reg(",");
	copy(sregex_token_iterator(line.begin(), line.end(), reg, -1),
		sregex_token_iterator(),
		back_inserter(split));
	return split;
}


// load data from csv file
template <typename T, size_t N>
vector<array<T, N>> load_csv(const string& path) {
	ifstream file(path);
	vector<array<T, N>> data;
	for (auto line = istream_iterator<string>(file); line != istream_iterator<string>(); ++line) {
		auto split = split_commas(*line);
		assert(split.size() == N); // number of values must match rows in file
		array<T, N> row;
		transform(split.begin(), split.end(), row.begin(), [](const string& in) -> T {
			return static_cast<T>(stod(in));
		});
		data.push_back(row);
	}

	return data;
}

void print_centroid(Centroid *centroid) {
	cout << "sepal_length: " << centroid->sepal_length() << endl;
	cout << "sepal_width: " << centroid->sepal_width() << endl;
	cout << "petal_length: " << centroid->petal_length() << endl;
	cout << "petal_width: " << centroid->petal_width() << endl;
	cout << endl;
}

int main(int argc, char **argv) {
	// train with 4d dataset
	cout << "begin training" << endl;
	// float data T, 4 dims N, 3 clusters k
	auto data = load_csv<float, 4>("data/iris-data-4d.csv");
	cout << "data size: " << data.size() << endl;
	auto means = dkm::kmeans_lloyd<float, 4>(data, 3);
	cout << "training finished" << endl;

	// cluster order: Iris-setosa, Iris-versicolor, Iris-virginica
	CentroidList centroids;
	for(int i=0; i<3; i++) {
		Centroid *cluster=centroids.add_centroid();
		cluster->set_sepal_length(get<0>(means)[i][0]);
		cluster->set_sepal_width(get<0>(means)[i][1]);
		cluster->set_petal_length(get<0>(means)[i][2]);
		cluster->set_petal_width(get<0>(means)[i][3]);
		print_centroid(cluster);
	}

	string model_file="data/iris-model.bin";
	fstream output(model_file, ios::out | ios::binary);
	centroids.SerializePartialToOstream(&output);
	cout << "model successfully written to " << model_file << endl;

	return 0;
}
