#!/usr/bin/env python

import os
from os import path
from subprocess import check_call

import arg_parser
import context


def main():
    args = arg_parser.receiver_first()

    cc_repo = path.join(context.third_party_dir, 'aurora-udt')
    src_dir = path.join(cc_repo, 'src')
    lib_dir = path.join(src_dir, 'core')
    app_dir = path.join(src_dir, 'app')
    send_src = path.join(app_dir, 'pccclient')
    recv_src = path.join(app_dir, 'pccserver')

    pcc_rl_dir = path.join(context.third_party_dir, 'pcc-rl')
    pcc_rl_testing_dir = path.join(pcc_rl_dir, 'src', 'udt-plugins', 'testing')
    model_path = path.join(context.third_party_dir, 'enhanced-aurora', 'example', 'server_test', 'py_aurora', 'saved_models', 'icml_paper_model')
    
    if args.option == 'setup':
        check_call(['make'], cwd=src_dir)
        return

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = path.join(lib_dir)
        cmd = [recv_src, 'recv', args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(lib_dir)
        cmd = [send_src, 'send', args.ip, args.port, 
               '--pcc-rate-control=python',
               '-pyhelper=loaded_client',
               f'-pypath={pcc_rl_testing_dir}',
               '--history-len=10',
               '--pcc-utility-calc=linear',
               f'--model-path={model_path}'
            ]
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
