# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)
set(BOARD esp32c3_luatos_core)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(peripheral_hr)
board_runner_args(esp32 "--esp-device=/dev/ttyACM0")

FILE(GLOB app_sources src/*.c)
target_sources(app PRIVATE
  ${app_sources}
  )

zephyr_library_include_directories(${ZEPHYR_BASE}/samples/bluetooth)
