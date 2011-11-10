#!/bin/bash -x
spawn-fcgi -n -P spawn-fcgi.pid -d /home/jjo/src/juanjo/web/ -f /home/jjo/src/juanjo/web/jjo.fcgi.py -a 127.0.0.1 -p 9000
