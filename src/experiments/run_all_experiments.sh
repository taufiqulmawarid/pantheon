#!/bin/bash

sudo sysctl -w net.ipv4.ip_forward=1 && sudo sysctl -w net.core.rmem_max=2500000

schemes="aqmss_ns3_lin aqmss aqmss_ns3_ori aqmss_ns3_exp aqmss_ns3_bool aqmss_ns3_fct aqmss_ns3_lin_inhouse aurora_udt"
runtime="60"
run_times="30"

rm -rf nohup_log/ data/
mkdir nohup_log data

nohup taskset -c 2 bash execute_test.sh \
    "$schemes" \
    "./12mbps.trace" \
    "./data/default_pantheon" \
    "$runtime" \
    "$run_times" \
    > ./nohup_log/defaul_pantheon.log 2>&1 &

sleep 5

nohup taskset -c 3 bash execute_test.sh \
    "$schemes" \
    "./additional_trace/trace-1553457194-ts-static" \
    "./data/static_movement" \
    "$runtime" \
    "$run_times" \
    > ./nohup_log/static_movement.log 2>&1 &

sleep 5

nohup taskset -c 4 bash execute_test.sh \
    "$schemes" \
    "./additional_trace/trace-1553455408-ts-walking" \
    "./data/walking_movement" \
    "$runtime" \
    "$run_times" \
    > ./nohup_log/walking_movement.log 2>&1 &

sleep 5

nohup taskset -c 5 bash execute_test.sh \
    "$schemes" \
    "./additional_trace/trace-1552767958-taxi1" \
    "./data/taxi" \
    "$runtime" \
    "$run_times" \
    > ./nohup_log/taxi.log 2>&1 &

sleep 5

nohup taskset -c 6 bash execute_test.sh \
    "$schemes" \
    "./additional_trace/trace-1553109898-bus" \
    "./data/bus" \
    "$runtime" \
    "$run_times" \
    > ./nohup_log/bus.log 2>&1 &

sleep 5

nohup taskset -c 7 bash execute_test.sh \
    "$schemes" \
    "./additional_trace/new-updated-movement125.csv.com-" \
    "./data/video_streaming" \
    "$runtime" \
    "$run_times" \
    > ./nohup_log/video_streaming.log 2>&1 &
