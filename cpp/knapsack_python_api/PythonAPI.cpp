#ifndef PYBIND11_PYTHONAPI_H
#define PYBIND11_PYTHONAPI_H

#include "../knapsack/API.hpp"

namespace kb = kb_knapsack;

#define DEF_KNAPSACK_1D(T)                                                                                                                                                           \
  std::tuple<T, T, std::vector<T>, std::vector<T>, std::vector<int>> solve_1d_##T(T & constraint, std::vector<T> & dimensions,  std::vector<T> & values, std::vector<int> & indexes)                                                                                \
  {                                                                                                                                                                                                    \
      return kb::knapsack1<T, T>(constraint, dimensions, values, indexes);                                                                                                                                                                 \
  }

DEF_KNAPSACK_1D(double);
DEF_KNAPSACK_1D(int);
DEF_KNAPSACK_1D(long);

#define GENERATE_SOLVER_NAME(X, Y, Z) X##Y ## Z

#define DEF_KNAPSACK_ND(T, N)                                                                                                                                                           \
  std::tuple<T, std::array<T, N>, std::vector<std::array<T, N>>, std::vector<T>, std::vector<int>> GENERATE_SOLVER_NAME(solve_, N##d_, T) (std::array<T, N> & constraint, std::vector<std::array<T, N>> & dimensions,  std::vector<T> & values, std::vector<int> & indexes)                                                                                \
  {                                                                                                                                                                                                    \
      return kb::knapsackN<T, T, N>(constraint, dimensions, values, indexes);                                                                                                                                                                 \
  }

#define GENERATE_DEF_KNAPSACK_ND(T)                                                                                                                                                       \
  DEF_KNAPSACK_ND(T, 2); \
  DEF_KNAPSACK_ND(T, 3); \
  DEF_KNAPSACK_ND(T, 4); \
  DEF_KNAPSACK_ND(T, 5); \
  DEF_KNAPSACK_ND(T, 6); \
  DEF_KNAPSACK_ND(T, 7); \
  DEF_KNAPSACK_ND(T, 8); \
  DEF_KNAPSACK_ND(T, 9); \
  DEF_KNAPSACK_ND(T, 10); \

GENERATE_DEF_KNAPSACK_ND(double);
GENERATE_DEF_KNAPSACK_ND(int);
GENERATE_DEF_KNAPSACK_ND(long);

#define REGISTER_KNAPSACK_API(NAME, N, DESC)           \
  mod.def("solve_"#N"d_"#NAME, &GENERATE_SOLVER_NAME(solve_, N##d_, NAME), DESC); \

#define GENERATE_REGISTER_KNAPSACK_API(T) \
  REGISTER_KNAPSACK_API(T, 1, "Solves 1-0 knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 2, "Solves 1-0 2d knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 3, "Solves 1-0 3d knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 4, "Solves 1-0 4d knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 5, "Solves 1-0 5d knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 6, "Solves 1-0 6d knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 7, "Solves 1-0 7d knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 8, "Solves 1-0 8d knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 9, "Solves 1-0 9d knapsack for ##NAME"); \
  REGISTER_KNAPSACK_API(T, 10, "Solves 1-0 10d knapsack for ##NAME");\

#define DEF_GREEDY_KNAPSACK_ND(T, N)                                                                                                                                                           \
  std::tuple<T, std::array<T, N>, std::vector<std::array<T, N>>, std::vector<T>, std::vector<int>> GENERATE_SOLVER_NAME(solve_greedy_, N##d_, T) (std::array<T, N> & constraint, std::vector<std::array<T, N>> & dimensions,  std::vector<T> & values, std::vector<int> & indexes)                                                                                \
  {                                                                                                                                                                                                    \
      return kb::greedyKnapsackN<T, T, N>(constraint, dimensions, values, indexes);                                                                                                                                                                 \
  }

#define GENERATE_DEF_GREEDY_KNAPSACK_ND(T)                                                                                                                                                       \
  DEF_GREEDY_KNAPSACK_ND(T, 2); \
  DEF_GREEDY_KNAPSACK_ND(T, 3); \
  DEF_GREEDY_KNAPSACK_ND(T, 4); \
  DEF_GREEDY_KNAPSACK_ND(T, 5); \
  DEF_GREEDY_KNAPSACK_ND(T, 6); \
  DEF_GREEDY_KNAPSACK_ND(T, 7); \
  DEF_GREEDY_KNAPSACK_ND(T, 8); \
  DEF_GREEDY_KNAPSACK_ND(T, 9); \
  DEF_GREEDY_KNAPSACK_ND(T, 10);                                                                                                                                                                 \

GENERATE_DEF_GREEDY_KNAPSACK_ND(double);
GENERATE_DEF_GREEDY_KNAPSACK_ND(int);
GENERATE_DEF_GREEDY_KNAPSACK_ND(long);

#define REGISTER_GREEDY_KNAPSACK_API(NAME, N, DESC)           \
  mod.def("solve_greedy_"#N"d_"#NAME, &GENERATE_SOLVER_NAME(solve_greedy_, N##d_, NAME), DESC); \

#define GENERATE_REGISTER_GREEDY_KNAPSACK_API(T) \
  REGISTER_GREEDY_KNAPSACK_API(T, 2, "Solves greedy 1-0 2d knapsack for ##NAME"); \
  REGISTER_GREEDY_KNAPSACK_API(T, 3, "Solves greedy 1-0 3d knapsack for ##NAME"); \
  REGISTER_GREEDY_KNAPSACK_API(T, 4, "Solves greedy 1-0 4d knapsack for ##NAME"); \
  REGISTER_GREEDY_KNAPSACK_API(T, 5, "Solves greedy 1-0 5d knapsack for ##NAME"); \
  REGISTER_GREEDY_KNAPSACK_API(T, 6, "Solves greedy 1-0 6d knapsack for ##NAME"); \
  REGISTER_GREEDY_KNAPSACK_API(T, 7, "Solves greedy 1-0 7d knapsack for ##NAME"); \
  REGISTER_GREEDY_KNAPSACK_API(T, 8, "Solves greedy 1-0 8d knapsack for ##NAME"); \
  REGISTER_GREEDY_KNAPSACK_API(T, 9, "Solves greedy 1-0 9d knapsack for ##NAME"); \
  REGISTER_GREEDY_KNAPSACK_API(T, 10, "Solves greedy 1-0 10d knapsack for ##NAME");\

#include <pybind11/numpy.h>
#include <pybind11/stl_bind.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>

namespace py = pybind11;

PYBIND11_MODULE(knapsack_python_api, mod) {

    mod.doc() = "The knapsack python api for 1-0 and greedy solvers up to 10 dimensions, for int, double and long int types.";

    py::bind_vector<std::vector<int32_t>>(mod, "VectorInt32");
    py::bind_vector<std::vector<uint32_t>>(mod, "VectorUInt32");

    py::bind_vector<std::vector<int64_t>>(mod, "VectorInt64");
    py::bind_vector<std::vector<uint64_t>>(mod, "VectorUInt64");

    py::bind_vector<std::vector<float>>(mod, "VectorFloat");
    py::bind_vector<std::vector<double>>(mod, "VectorDouble");

    GENERATE_REGISTER_KNAPSACK_API(double);
    GENERATE_REGISTER_KNAPSACK_API(int);
    GENERATE_REGISTER_KNAPSACK_API(long);

    GENERATE_REGISTER_GREEDY_KNAPSACK_API(double);
    GENERATE_REGISTER_GREEDY_KNAPSACK_API(int);
    GENERATE_REGISTER_GREEDY_KNAPSACK_API(long);
}

#endif //PYBIND11_PYTHONAPI_H
