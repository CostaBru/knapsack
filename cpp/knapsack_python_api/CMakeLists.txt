cmake_minimum_required(VERSION 3.19)
set(CMAKE_CXX_STANDARD 20)

project(knapsack_python_api CXX)

set(PYTHON_EXECUTABLE "$ENV{USERPROFILE}/AppData/Local/Programs/Python/Python38/python.exe")
set(KNAPSACK_PYTHON_API_VERSION_INFO "0.0.1")

# from git root
#git submodule add -b stable ../../pybind/pybind11 cpp/knapsack_python_api/pybind11
#git submodule update --init

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(knapsack_python_api
        ../knapsack/API.hpp
        ../knapsack/defines.h
        ../knapsack/fast_map.h
        ../knapsack/knapsack_greedy_top_down_solver.hpp
        ../knapsack/knapsack_limits_solver.hpp
        ../knapsack/knapsack_pareto_solver.hpp
        ../knapsack/knapsack_solver.hpp
        ../knapsack/knapsack_superincreasing_solver.hpp
        ../knapsack/source_link.hpp
        ../knapsack/tools.hpp
        ../knapsack/w_point.hpp
        ../knapsack/w_point_dim1.hpp
        ../knapsack/w_point_dimN.hpp

        PythonAPI.cpp
        )

include_directories(SYSTEM ../knapsack)

target_compile_definitions(knapsack_python_api PRIVATE VERSION_INFO=${KNAPSACK_PYTHON_API_VERSION_INFO})