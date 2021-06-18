#ifndef PYBIND11_PYTHONAPI_H
#define PYBIND11_PYTHONAPI_H

#include "../knapsack/API.hpp"

namespace kb = kb_knapsack;

std::tuple<double, double, std::vector<double>, std::vector<double>, std::vector<int>>
solve_1d_double(double                                & constraint,
                std::vector<double>                   & dimensions,
                std::vector<double>                   & values,
                std::vector<int>                      & indexes)

{
    return kb::knapsack1<double, double>(constraint, dimensions, values, indexes);
}

std::tuple<int, int, std::vector<int>, std::vector<int>, std::vector<int>>
solve_1d_int(int                                   & constraint,
                std::vector<int>                   & dimensions,
                std::vector<int>                   & values,
                std::vector<int>                   & indexes)

{
    return kb::knapsack1<int, int>(constraint, dimensions, values, indexes);
}


std::tuple<long, long, std::vector<long>, std::vector<long>, std::vector<int>>
solve_1d_long(long                                 & constraint,
             std::vector<long>                     & dimensions,
             std::vector<long>                     & values,
             std::vector<int>                      & indexes)

{
    return kb::knapsack1<long, long>(constraint, dimensions, values, indexes);
}

#include <pybind11/numpy.h>
#include <pybind11/stl_bind.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>

namespace py = pybind11;

PYBIND11_MODULE(knapsack_python_api, mod) {

    mod.doc() = "knapsack_python_api: solve_1d_double, solve_1d_int, solve_1d_long";

    py::bind_vector<std::vector<int32_t>>(mod, "VectorInt32");
    py::bind_vector<std::vector<uint32_t>>(mod, "VectorUInt32");

    py::bind_vector<std::vector<int64_t>>(mod, "VectorInt64");
    py::bind_vector<std::vector<uint64_t>>(mod, "VectorUInt64");

    py::bind_vector<std::vector<float>>(mod, "VectorFloat");
    py::bind_vector<std::vector<double>>(mod, "VectorDouble");

    mod.def("solve_1d_double", &solve_1d_double, "Solves 1-0 knapsack for doubles.");
    mod.def("solve_1d_int", &solve_1d_int, "Solves 1-0 knapsack for integers.");
    mod.def("solve_1d_long", &solve_1d_long, "Solves 1-0 knapsack for long integers.");
}

#endif //PYBIND11_PYTHONAPI_H
