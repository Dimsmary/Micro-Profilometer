# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Initialise pico_sdk from installed location
# (note this can come from environment, CMake cache etc)

# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.1.1)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.1.1)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico2 CACHE STRING "Board type")

# Pull in Raspberry Pi Pico SDK (must be before project)
include(pico_sdk_import.cmake)

project(Table_Movement C CXX ASM)

# Initialise the Raspberry Pi Pico SDK
pico_sdk_init()

# Add executable. Default name is the project name, version 0.1

cmake_minimum_required(VERSION 3.13)

add_executable(Table_Movement
    Table_Movement.cpp
    lib/ad57x1/ad57x1.cpp
    lib/command_handle/command_handle.cpp
    usb_descriptors.c)

pico_set_program_name(Table_Movement "Table_Movement")
pico_set_program_version(Table_Movement "0.1")

# Modify the below lines to enable/disable output over UART/USB
pico_enable_stdio_uart(Table_Movement 0)
pico_enable_stdio_usb(Table_Movement 1)

# Add the standard library to the build
target_link_libraries(Table_Movement
        pico_stdlib hardware_spi)

# Add the standard include files to the build
target_include_directories(Table_Movement PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}
        ${CMAKE_CURRENT_LIST_DIR}lib/ad57x1
        ${CMAKE_CURRENT_LIST_DIR}lib/command_handle
)

# Add any user requested libraries
target_link_libraries(Table_Movement 
    pico_stdlib
    hardware_spi
    pico_unique_id
    tinyusb_device
    tinyusb_board
        )

pico_add_extra_outputs(Table_Movement)

