/*
Test cases for dkm.hpp

This is just simple test harness without any external dependencies.
*/

#include "../dkm/include/dkm.hpp"

#include <vector>
#include <array>
#include <tuple>
#include <string>
#include <iterator>
#include <fstream>
#include <iostream>
#include <chrono>
#include <numeric>
#include <regex>

// Split a line on commas, making it simple to pull out the values we need
std::vector<std::string> split_commas(const std::string& line) {
	std::vector<std::string> split;
	std::regex reg(",");
	std::copy(std::sregex_token_iterator(line.begin(), line.end(), reg, -1),
		std::sregex_token_iterator(),
		std::back_inserter(split));
	return split;
}

template <typename T, size_t N>
void print_result_dkm(std::tuple<std::vector<std::array<T, N>>, std::vector<uint32_t>>& result) {
	std::cout << "centers: ";
	for (const auto& c : std::get<0>(result)) {
		std::cout << "(";
		for (auto v : c) {
			std::cout << v << ",";
		}
		std::cout << "), ";
	}
	std::cout << std::endl;
}


template <typename T, size_t N>
std::vector<std::array<T, N>> load_dkm(const std::string& path) {
	std::ifstream file(path);
	std::vector<std::array<T, N>> data;
	for (auto it = std::istream_iterator<std::string>(file); it != std::istream_iterator<std::string>(); ++it) {
		auto split = split_commas(*it);
		assert(split.size() == N); // number of values must match rows in file
		std::array<T, N> row;
		std::transform(split.begin(), split.end(), row.begin(), [](const std::string& in) -> T {
			return static_cast<T>(std::stod(in));
		});
		data.push_back(row);
	}
	return data;
}


template <typename T, size_t N>
std::chrono::duration<double> profile_dkm(const std::vector<std::array<T, N>>& data, int k) {
	auto start = std::chrono::high_resolution_clock::now();
	// run the bench 10 times and take the average
	for (int i = 0; i < 10; ++i) {
		std::cout << "." << std::flush;
		auto result = dkm::kmeans_lloyd(data, k);
		(void)result;
	}
	auto end = std::chrono::high_resolution_clock::now();
	return (end - start) / 10.0;
}


template <typename T, size_t N>
void bench_dataset(const std::string& path, uint32_t k) {
	std::cout << "## Dataset " << path << " ##" << std::endl;

	auto dkm_data = load_dkm<T, N>(path);
	auto time_dkm = profile_dkm(dkm_data, k);
	std::cout << "\n";
	std::cout << "DKM: " << std::chrono::duration_cast<std::chrono::duration<double, std::milli>>(time_dkm).count()
			  << "ms" << std::endl;
	std::cout << "---";
	std::cout << "\n" << std::endl;
}

int main() {
	std::cout << "# BEGINNING PROFILING #\n" << std::endl;

	// float data T, 4 dims N, 3 clusters k
	bench_dataset<float, 4>("data/iris-data-4d.csv", 3);


	return 0;
}
