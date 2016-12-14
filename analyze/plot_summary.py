#!/usr/bin/env python

import os
import re
import sys
import math
import json
import pantheon_helpers
import matplotlib_agg
import matplotlib.pyplot as plt
import matplotlib.markers as markers
import matplotlib.ticker as ticker
from os import path
from time import strftime
from datetime import datetime
from helpers.pantheon_help import check_output, get_friendly_names, Popen, PIPE
from helpers.parse_arguments import parse_arguments


class PlotSummary:
    def __init__(self, args):
        self.data_dir = path.abspath(args.data_dir)
        analyze_dir = path.dirname(__file__)
        self.src_dir = path.abspath(path.join(analyze_dir, '../src'))

        # load pantheon_metadata.json as a dictionary
        metadata_fname = path.join(self.data_dir, 'pantheon_metadata.json')
        with open(metadata_fname) as metadata_file:
            metadata_dict = json.load(metadata_file)

        self.run_times = metadata_dict['run_times']
        self.cc_schemes = metadata_dict['cc_schemes'].split()
        self.flows = int(metadata_dict['flows'])
        self.timezone = None

    def parse_tunnel_log(self, cc, run_id):
        log_prefix = cc
        if self.flows == 0:
            log_prefix += '_mm'

        tput = None
        delay = None
        for_stats = None
        err_ret = (None, None, None)

        for link_t in ['datalink', 'acklink']:
            log_name = log_prefix + '_%s_run%s.log' % (link_t, run_id)
            log_path = path.join(self.data_dir, log_name)

            if not path.isfile(log_path):
                sys.stderr.write('Warning: %s does not exist\n' % log_path)
                return err_ret

            for metric_t in ['throughput', 'delay']:
                if metric_t == 'throughput':
                    cmd = ['mm-tunnel-throughput', '500', log_path]
                else:
                    cmd = ['mm-tunnel-delay', log_path]

                graph_name = cc + '_%s_%s_run%s.png' % (
                             link_t, metric_t, run_id)
                graph_path = path.join(self.data_dir, graph_name)
                graph_file = open(graph_path, 'w')

                try:
                    proc = Popen(cmd, stdout=graph_file, stderr=PIPE)
                    results = proc.communicate()[1]
                except:
                    sys.stderr.write('Warning: "%s" failed\n' % ' '.join(cmd))
                    return err_ret

                graph_file.close()

                if link_t == 'datalink' and metric_t == 'throughput':
                    for_stats = results

                    ret = re.search(r'Average throughput: (.*?) Mbit/s',
                                    results)
                    if ret and not tput:
                        tput = float(ret.group(1))

                    ret = re.search(r'95th percentile per-packet one-way '
                                    'delay: (.*?) ms', results)
                    if ret and not delay:
                        delay = float(ret.group(1))

        return (tput, delay, for_stats)

    def parse_stats_log(self, cc, run_id, for_stats):
        stats_log_path = path.join(
            self.data_dir, '%s_stats_run%s.log' % (cc, run_id))
        if not path.isfile(stats_log_path):
            sys.stderr.write('Warning: %s does not exist\n' % stats_log_path)
            return None

        ofst = None
        stats_log = open(stats_log_path, 'r+')

        for_stats_exists = False
        for line in stats_log:
            ret = re.match(r'Worst absolute clock offset: (.*?) ms', line)
            if ret and not ofst:
                ofst = float(ret.group(1))
                continue

            ret = re.match(r'# Datalink statistics (generated by *.py)', line)
            if ret:
                for_stats_exists = True
                break

        if not for_stats_exists and for_stats:
            stats_log.seek(0, os.SEEK_END)
            stats_log.write('\n# Datalink statistics (generated by %s)\n'
                            % path.basename(__file__))
            stats_log.write('%s' % for_stats)

        stats_log.close()
        return ofst

    def generate_data(self):
        self.data = {}
        self.worst_abs_ofst = None
        time_format = '%a, %d %b %Y %H:%M:%S'

        for cc in self.cc_schemes:
            self.data[cc] = []
            cc_name = self.friendly_names[cc]

            for run_id in xrange(1, 1 + self.run_times):
                (tput, delay, for_stats) = self.parse_tunnel_log(cc, run_id)
                ofst = self.parse_stats_log(cc, run_id, for_stats)

                if not tput or not delay:
                    continue

                self.data[cc].append((tput, delay))
                if ofst:
                    if not self.worst_abs_ofst or ofst > self.worst_abs_ofst:
                        self.worst_abs_ofst = ofst

    def plot_throughput_delay(self):
        min_delay = None
        color_i = 0
        marker_i = 0
        color_names = ['r', 'y', 'b', 'g', 'c', 'm', 'brown', 'orange', 'gray',
                       'gold', 'skyblue', 'olive', 'lime', 'violet', 'purple']
        marker_names = markers.MarkerStyle.filled_markers

        fig_raw, ax_raw = plt.subplots()
        fig_mean, ax_mean = plt.subplots()

        for cc, value in self.data.items():
            cc_name = self.friendly_names[cc]
            color = color_names[color_i]
            marker = marker_names[marker_i]
            y_data, x_data = zip(*value)

            # find min and max delay
            cc_min_delay = min(x_data)
            if not min_delay or cc_min_delay < min_delay:
                min_delay = cc_min_delay

            # plot raw values
            ax_raw.scatter(x_data, y_data, color=color, marker=marker,
                           label=cc_name, clip_on=False)

            # plot the average of raw values
            x_mean = sum(x_data) / len(x_data)
            y_mean = sum(y_data) / len(y_data)
            ax_mean.scatter(x_mean, y_mean, color=color, marker=marker,
                            clip_on=False)
            ax_mean.annotate(cc_name, (x_mean, y_mean))

            color_i = color_i + 1 if color_i < len(color_names) - 1 else 0
            marker_i = marker_i + 1 if marker_i < len(marker_names) - 1 else 0

        for fig, ax in [(fig_raw, ax_raw), (fig_mean, ax_mean)]:
            if min_delay > 0:
                ax.set_xscale('log', basex=2)
                ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
            ax.invert_xaxis()

            yticks = ax.get_yticks()
            if yticks[0] < 0:
                ax.set_ylim(bottom=0)

            xlabel = '95th percentile of per-packet one-way delay (ms)'
            if self.worst_abs_ofst:
                xlabel += ('\n(worst absolute clock offset: %s ms)' %
                           self.worst_abs_ofst)
            ax.set_xlabel(xlabel)
            ax.set_ylabel('Average throughput (Mbit/s)')
            ax.grid()

        # save pantheon_summary.png
        ax_raw.set_title('Summary of results')
        lgd = ax_raw.legend(scatterpoints=1, bbox_to_anchor=(1, 0.5),
                            loc='center left', fontsize=12)
        raw_summary = path.join(self.data_dir, 'pantheon_summary.png')
        fig_raw.savefig(raw_summary, dpi=300, bbox_extra_artists=(lgd,),
                        bbox_inches='tight', pad_inches=0.2)

        # save pantheon_summary_mean.png
        ax_mean.set_title('Summary of results (average of all runs)')
        mean_summary = path.join(
            self.data_dir, 'pantheon_summary_mean.png')
        fig_mean.savefig(mean_summary, dpi=300,
                         bbox_inches='tight', pad_inches=0.2)

    def autolabel(self, rects, ax, friendly_names):
        i = 0
        for rect in rects:
            ax.text(rect.get_x() + rect.get_width() / 2.0,
                    rect.get_height() + 0.2,
                    friendly_names[i], ha='center', va='bottom')
            i += 1

    def plot_summary(self):
        self.friendly_names = get_friendly_names(self.cc_schemes)
        self.generate_data()
        self.plot_throughput_delay()


def main():
    args = parse_arguments(path.basename(__file__))

    plot_summary = PlotSummary(args)
    plot_summary.plot_summary()


if __name__ == '__main__':
    DEVNULL = open(os.devnull, 'w')
    main()
    DEVNULL.close()
