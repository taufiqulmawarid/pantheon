#!/usr/bin/env python

import os
from os import path
from subprocess import check_call

import arg_parser
import context
from helpers import utils


def main():
    args = arg_parser.receiver_first()

    pcc_rl_repo = '/home/haidlir/PCCProject/PCC-RL'
    pcc_uspace_repo = '/home/haidlir/PCCProject/PCC-Uspace-DL-Branch/'
    model_name = '2022-03-22-09:00'
    # model_name = 'icml_paper_model'
    model_path = f'{pcc_rl_repo}/src/gym/pcc_saved_models/{model_name}'
    cc_repo = path.join(context.third_party_dir, 'pcc')
    recv_dir = path.join(cc_repo, 'receiver')
    send_dir = path.join(cc_repo, 'sender')
    recv_src = path.join(pcc_uspace_repo, 'src', 'app', 'pccserver')
    send_src = path.join(pcc_uspace_repo, 'src', 'app', 'pccclient')

    if args.option == 'setup':
        # apply patch to reduce MTU size
        utils.apply_patch('pcc.patch', cc_repo)

        check_call(['make'], cwd=recv_dir)
        check_call(['make'], cwd=send_dir)
        return

    if args.option == 'receiver':
        os.environ['LD_LIBRARY_PATH'] = path.join(pcc_uspace_repo, 'src', 'core')
        cmd = [recv_src, 'recv', args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        os.environ['LD_LIBRARY_PATH'] = path.join(pcc_uspace_repo, 'src', 'core')
        rl_args = f'--pcc-rate-control=python -pyhelper=loaded_client'\
                       f' -pypath={pcc_rl_repo}/src/udt-plugins/testing/'\
                       f' --history-len=10 --pcc-utility-calc=linear'\
                       f' --model-path="{model_path}"'
        cmd = [send_src, 'send', args.ip, args.port, rl_args]
        # suppress debugging output to stderr
        with open(os.devnull, 'w') as devnull:
            check_call(cmd, stderr=devnull)
        return


if __name__ == '__main__':
    main()
