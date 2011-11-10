#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Implements foo"""

import os, re, time
from flup.server.fcgi import WSGIServer

def get_cpu(_):
  """Returns cumulative used milli-seconds"""
  cpu_string = open('/proc/stat').read()
  cpu_array = re.match('(cpu)\W+(\d+) (\d+) (\d+) (\d+)', cpu_string).groups()
  if cpu_array:
    user, nice, system = [int(x) for x in cpu_array[1:4]]
    used = user+nice+system
    return "%d %d" % ( time.time(), int(used*1e3/JIFFIES))
  return None
  
PATH_REGISTRY = {
    '/stat': '',
    '/stat/cpu': get_cpu,
    }

def app(environ, start_response):
  """main fcgi entry point"""
  start_response('200 OK', [('Content-Type', 'text/plain')])
  func = PATH_REGISTRY.get(environ['PATH_INFO'])
  if func is not None:
    if callable(func):
      val = func(environ)
    else:
      val = func
    yield '%s %s %s\n' % (
        environ['SERVER_NAME'], environ['PATH_INFO'], val)

JIFFIES = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
WSGIServer(app).run()
