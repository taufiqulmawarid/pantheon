#!/usr/bin/python

import os, sys, time
from subprocess import check_call, Popen
import usage

def main():
    usage.check_args(sys.argv, os.path.basename(__file__), usage.SEND_FIRST)
    option = sys.argv[1]
    src_dir = os.path.abspath(os.path.dirname(__file__))
    submodule_dir = os.path.abspath(os.path.join(src_dir,
                                    '../third_party/webrtc'))
    src_file = os.path.join(submodule_dir, 'app.js')
    video_file = os.path.abspath('/tmp/video.y4m')

    # build dependencies
    if option == 'deps':
        deps_list = 'chromium-browser nodejs npm xvfb xfonts-100dpi xfonts-75dpi ' \
                    'xfonts-cyrillic xorg dbus-x11'
        print deps_list

    # build
    if option == 'build':
        cmd = 'cd %s && npm install' % submodule_dir
        check_call(cmd, shell=True)

    # commands to be run after building and before running
    if option == 'initialize':
        video_url = 'https://media.xiph.org/video/derf/y4m/blue_sky_1080p25.y4m'
        cmd = ['wget', '-O', video_file, video_url]
        check_call(cmd)

    # who goes first
    if option == 'who_goes_first':
        print 'Sender first'

    # sender
    if option == 'sender':
        cmd = ['Xvfb', ':1']
        xvfb = Popen(cmd)
        os.environ['DISPLAY']=':1'
        cmd = ['nodejs', src_file]
        signaling_server = Popen(cmd)
        print 'Listening on port: 3000' # XXX we want to run multiple flows
        sys.stdout.flush()
        cmd = 'chromium-browser --app=http://localhost:3000/sender ' \
              '--use-fake-ui-for-media-stream ' \
              '--use-fake-device-for-media-stream ' \
              '--use-file-for-fake-video-capture=%s ' \
              '--user-data-dir=/tmp/nonexistent$(date +%%s%%N)' % video_file
        check_call(cmd, shell=True)

    # receiver
    if option == 'receiver':
        cmd = ['Xvfb', ':2']
        xvfb = Popen(cmd)
        os.environ['DISPLAY']=':2'
        ip = sys.argv[2]
        port = sys.argv[3]
        time.sleep(3) # at least wait until the sender is ready
        cmd = 'chromium-browser --app=http://%s:%s/receiver ' \
              '--user-data-dir=/tmp/nonexistent$(date +%%s%%N)' % (ip, port)
        check_call(cmd, shell=True)

if __name__ == '__main__':
    main()
