cmake_minimum_required(VERSION 3.19)
set(CMAKE_CXX_STANDARD 20)

project(knapsack CXX)
add_library(knapsack knapsack_solver.h fast_map.h w_point_dim1.h defines.h w_point_dimN.h w_point.h tools.h source_link.h knapsack_limits_solver.h knapsack_pareto_solver.h knapsack_greedy_top_down_solver.h knapsack_superincreasing_solver.h API.h)
set_target_properties(knapsack PROPERTIES LINKER_LANGUAGE CXX)
set(CMAKE_EXE_LINKER_FLAGS "-static")