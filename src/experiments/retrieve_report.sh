#!/bin/bash

rm -rf report/
mkdir report

mv data/default_pantheon/pantheon_report.pdf report/pantheon_report_default_pantheon.pdf
mv data/static_movement/pantheon_report.pdf report/pantheon_report_static_movement.pdf
mv data/walking_movement/pantheon_report.pdf report/pantheon_report_walking_movement.pdf
mv data/taxi/pantheon_report.pdf report/pantheon_report_taxi.pdf
mv data/bus/pantheon_report.pdf report/pantheon_report_bus.pdf
mv data/video_streaming/pantheon_report.pdf report/pantheon_report_video_streaming.pdf