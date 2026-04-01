cmake_minimum_required(VERSION 3.20)
project(budget_vr_tracker)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# OpenVR SDK
set(OPENVR_SDK_PATH "${CMAKE_SOURCE_DIR}/libraries/openvr" CACHE PATH "OpenVR SDK")
include_directories("${OPENVR_SDK_PATH}/headers")

# nlohmann/json
find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
    include(FetchContent)
    FetchContent_Declare(json
        GIT_REPOSITORY https://github.com/nlohmann/json.git
        GIT_TAG v3.11.3
        GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(json)
endif()

# Sources
add_library(driver_budget_vr_tracker SHARED
    src/main.cpp
    src/device_provider.cpp
    src/controller_device.cpp
    src/tracker_device.cpp
    src/pipe_server.cpp
)

target_link_libraries(driver_budget_vr_tracker 
    "${OPENVR_SDK_PATH}/lib/linux64/libopenvr_api.so"
    nlohmann_json::nlohmann_json
    pthread
)

set_target_properties(driver_budget_vr_tracker PROPERTIES
    OUTPUT_NAME "driver_budget_vr_tracker"
    PREFIX ""
    SUFFIX ".so"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin/linux64"
)
