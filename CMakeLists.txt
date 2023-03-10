cmake_minimum_required(VERSION 3.4...3.18)
project(iohook)

add_subdirectory(extern/pybind11)
add_subdirectory(extern/libuiohook)

pybind11_add_module(iohook src/main.cpp src/hook.c)
target_link_libraries(iohook PRIVATE uiohook)

# EXAMPLE_VERSION_INFO is defined by setup.py and passed into the C++ code as a

# define (VERSION_INFO) here.
target_compile_definitions(iohook
                           PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})