cmake_minimum_required(VERSION 3.18)
project(pyyoga LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(FETCHCONTENT_QUIET OFF)
include(FetchContent)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11.git
    GIT_TAG v2.13.6
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(pybind11)

FetchContent_Declare(
    yoga
    GIT_REPOSITORY https://github.com/facebook/yoga.git
    GIT_TAG v3.2.1
    GIT_SHALLOW TRUE
)
FetchContent_MakeAvailable(yoga)

pybind11_add_module(_pyyoga
    src/bindings.cpp
)

target_include_directories(_pyyoga PRIVATE
    ${yoga_SOURCE_DIR}
)

target_link_libraries(_pyyoga PRIVATE yogacore)

target_compile_definitions(_pyyoga PRIVATE
    YG_EXPORT=
)

install(TARGETS _pyyoga LIBRARY DESTINATION pyyoga)
