#!/bin/bash -x
spawn-fcgi -n -P ./var/lib/spawn-fcgi.pid -d $PWD/web -f $PWD/webbogomon.fcgi.py -a 127.0.0.1 -p ${1:?missing port}
