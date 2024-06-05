#!/usr/bin/env python

# from os import path
import os
from subprocess import check_call, CalledProcessError

import arg_parser
import context


def main():
    # use 'arg_parser' to ensure a common test interface
    args = arg_parser.sender_first()

    model_name = './py_aurora/saved_models/train-12Mbps-lognormal-bool-reward-2023-02-24-16:04'


    # paths to the sender and receiver executables, etc.
    cc_repo = os.path.join(context.third_party_dir, 'enhanced-aurora')
    client_dir = os.path.join(cc_repo, 'example', 'client_test')
    client_src = os.path.join(client_dir, 'main') # client executable filename
    server_dir = os.path.join(cc_repo, 'example', 'server_test')
    server_src = os.path.join(server_dir, 'main') # server executable filename

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
        cmd = [client_src, '-insecure', get_arg]
        # Void the stdout and stderr of the client
        with open(os.devnull, 'w') as devnull:
            # Retry when client failed to connect to the server
            while True:
                try:
                    check_call(cmd, cwd=client_dir, stdout=devnull, stderr=devnull, shell=False)
                    break
                except CalledProcessError:
                    pass
            # check_call(cmd, cwd=client_dir, stdout=devnull, stderr=devnull, shell=False)
        return
        # Print out the stdout and stderr of the client
        # check_call(cmd, cwd=client_dir)

    # [required] run the other side to connect to the first side on 'args.ip'
    if args.option == 'sender':
        bind_arg = f'0.0.0.0:{args.port}'
        cmd = [server_src, '-bind', bind_arg, '-aurora-model', model_name, '-interval-rtt-n', '2.0', '-interval-rtt-estimator', '1']
        # Void the stdout and stderr of the server
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, cwd=server_dir, stdout=devnull, stderr=devnull, shell=False)
        return
        # Print out the stdout and stderr of the server
        # check_call(cmd, cwd=server_dir)
        


if __name__ == '__main__':
    main()
