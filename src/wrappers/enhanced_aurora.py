#!/usr/bin/env python

# from os import path
import os
from subprocess import check_call

import arg_parser
import context


def main():
    # use 'arg_parser' to ensure a common test interface
    args = arg_parser.sender_first()

    model_name = './py_aurora/saved_models/icml_paper_model'


    # paths to the sender and receiver executables, etc.
    cc_repo = os.path.join(context.third_party_dir, 'enhanced-aurora')
    recv_src = os.path.join(cc_repo, 'example', 'client_test', 'main')
    send_src = os.path.join(cc_repo, 'example', 'server_test', 'main')

    if args.option == 'setup_after_reboot':
        # Increase UDP Receive Buffer Size
        check_call(['sudo', 'sysctl', '-w', 'net.core.rmem_max=2500000'])
        # Mahimahi setup
        check_call(['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=1'])
        return

    # [required] run the first side on port 'args.port'
    if args.option == 'receiver':
        body_size = 200000000
        get_arg = f'https://{args.ip}:{args.port}/{body_size}'
        cmd = [recv_src, '-insecure', get_arg]
        check_call(cmd)

    # [required] run the other side to connect to the first side on 'args.ip'
    if args.option == 'sender':
        listener_arg = f'0.0.0.0:{args.port}'
        cmd = [send_src, '-bind', listener_arg, '-aurora-model', model_name, '-interval-rtt-n', '2.0', '-interval-rtt-estimator', '1']
        check_call(cmd)


if __name__ == '__main__':
    main()
