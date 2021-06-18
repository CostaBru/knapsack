cmake_minimum_required(VERSION 3.19)
project(partition_tests CXX)

set(CMAKE_CXX_STANDARD 20)

set(SOURCE_FILES
        partition_tests.cpp
        )

set(HEADER_FILES
        ut.h
        )

add_executable(partition_tests ${SOURCE_FILES} ${HEADER_FILES})

set(CMAKE_EXE_LINKER_FLAGS "-static")