cmake_minimum_required(VERSION 3.13)
project(totk C CXX ASM)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_USE_RESPONSE_FILE_FOR_OBJECTS ON)
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    add_compile_options(-fcolor-diagnostics)
    add_compile_options(-Wno-unused-command-line-argument)
endif ()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(totk)
target_include_directories(totk PRIVATE src include)
target_compile_definitions(totk PRIVATE NON_MATCHING)
target_compile_options(totk PRIVATE -Wall -Wextra -Wno-unused-parameter)

add_subdirectory(src)
