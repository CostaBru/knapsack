cmake_minimum_required(VERSION 3.19)
project(knapsack_tests CXX)

set(CMAKE_CXX_STANDARD 20)

set(SOURCE_FILES
        knapsack_tests.cpp
        )

set(HEADER_FILES
        ut.h
        paths.h ../knapsack/w_point_dim1.hpp ../knapsack/w_point_dimN.hpp ../knapsack/tools.hpp)

add_executable(knapsack_tests ${SOURCE_FILES} ${HEADER_FILES} ../knapsack/w_point_dim1.hpp ../knapsack/w_point_dimN.hpp ../knapsack/tools.hpp)

target_link_libraries(knapsack_tests knapsack)

set(CMAKE_EXE_LINKER_FLAGS "-static")