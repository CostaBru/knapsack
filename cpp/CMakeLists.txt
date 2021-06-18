cmake_minimum_required(VERSION 3.19)
set(CMAKE_CXX_STANDARD 20)

project(KB_knapsack_partition_solution CXX)

add_subdirectory(knapsack)
add_subdirectory(knapsack_python_api)
include_directories(knapsack)
include_directories(knapsack_python_api)
add_subdirectory(partition)
include_directories(partition)

add_subdirectory(knapsack_tests)
add_subdirectory(partition_tests)