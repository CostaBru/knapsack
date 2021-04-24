cmake_minimum_required(VERSION 3.19)
set(CMAKE_CXX_STANDARD 20)

project(partition CXX)
add_library(partition partition.h fast_map.h)
set_target_properties(partition PROPERTIES LINKER_LANGUAGE CXX)
set(CMAKE_EXE_LINKER_FLAGS "-static")