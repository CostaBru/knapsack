cmake_minimum_required(VERSION 3.19)
set(CMAKE_CXX_STANDARD 20)

project(knapsack CXX)
add_library(knapsack knapsack.h fast_map.h BloomFilter.h)
set_target_properties(knapsack PROPERTIES LINKER_LANGUAGE CXX)
set(CMAKE_EXE_LINKER_FLAGS "-static")