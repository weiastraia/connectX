#!/bin/sh
# Build portable shared libraries (no libstdc++ dependency, old glibc symbols only).
set -e
cd "$(dirname "$0")"
FLAGS="-O3 -std=c++17 -fPIC -shared -fno-exceptions -fno-rtti -fvisibility=hidden -static-libgcc -static-libstdc++ -Wl,--as-needed -Wl,-O1 -s"
g++ $FLAGS -march=x86-64 -mtune=generic -mpopcnt -o build/cx_solver_v2.so src/cx_api.cpp
g++ $FLAGS -march=x86-64 -mtune=generic        -o build/cx_solver_v1.so src/cx_api.cpp
