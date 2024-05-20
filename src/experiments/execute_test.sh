#!/bin/bash

# Check if the number of arguments is correct
if [ $# -ne 1 ]; then
    echo "Usage: $0 <trace_file>"
    exit 1
fi

# Get the input argument
trace_file=$1

# Run the Python script with the additional argumentss
python test.py local --schemes "enhanced_aurora cubic pcc" --uplink-trace "$trace_file" --downlink-trace "$trace_file" --runtime 60 && \

# Run the Python script for analysis
python ../analysis/analyze.py