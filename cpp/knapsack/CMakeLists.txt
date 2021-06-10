cmake_minimum_required(VERSION 3.19)
set(CMAKE_CXX_STANDARD 20)

project(knapsack CXX)
add_library(knapsack knapsack_solver.hpp fast_map.h w_point_dim1.hpp defines.h w_point_dimN.hpp w_point.hpp tools.hpp source_link.hpp knapsack_limits_solver.hpp knapsack_pareto_solver.hpp knapsack_greedy_top_down_solver.hpp knapsack_superincreasing_solver.hpp API.hpp)
set_target_properties(knapsack PROPERTIES LINKER_LANGUAGE CXX)
set(CMAKE_EXE_LINKER_FLAGS "-static")