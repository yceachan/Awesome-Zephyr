# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
board_runner_args(esp32 "--esp-device=/dev/ttyACM0")
project(threads)

target_sources(app PRIVATE src/main.c)
