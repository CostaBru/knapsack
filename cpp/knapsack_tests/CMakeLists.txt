cmake_minimum_required(VERSION 3.19)
project(knapsack_tests CXX)

set(CMAKE_CXX_STANDARD 20)

set(SOURCE_FILES
        knapsack_tests.cpp
        )

set(HEADER_FILES
        ut.h
        paths.h)

add_executable(knapsack_tests ${SOURCE_FILES} ${HEADER_FILES})

target_link_libraries(knapsack_tests knapsack)

set(CMAKE_EXE_LINKER_FLAGS "-static")