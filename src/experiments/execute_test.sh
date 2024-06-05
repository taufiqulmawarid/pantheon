#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -ne 5 ]; then
    echo "Usage: $0 <schemes> <trace_file> <data_dir> <runtime> <run_times>"
    exit 1
fi

# Fetch the arguments
schemes="$1"
trace_file="$2"
data_dir="$3"
runtime="$4"
run_times="$5"

# Clear the data directory
rm -rf "$data_dir"

# Run the Python script with the additional arguments
python test.py local \
    --schemes "$schemes" \
    --uplink-trace "$trace_file" --downlink-trace "$trace_file" \
    --runtime "$runtime" \
    --run-times "$run_times" \
    --data-dir "$data_dir" && \

# Run the Python script for analysis
python ../analysis/analyze.py --data-dir="$data_dir"