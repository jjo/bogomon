#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Implements foo"""

import os, re, time, rrdtool
from flup.server.fcgi import WSGIServer

def get_cpu(_):
  """Returns cumulative used milli-seconds"""
  cpu_string = open('/proc/stat').read()
  cpu_array = re.match('(cpu)\W+(\d+) (\d+) (\d+) (\d+)', cpu_string).groups()
  if cpu_array:
    user, nice, system = [int(x) for x in cpu_array[1:4]]
    used = user+nice+system
    return ('text/plain',
        '%d %d' % ( time.time(), int(used*1e3/JIFFIES)))
  
def sample_local(_):
  """short cut to update local rrd"""
  cpu = get_cpu(_)[1].split(" ")
  rrdtool.update('../rrdtool/jjo.rrd', '-t', 'cpurate',
      '%s:%s' % (cpu[0], cpu[1]))
  return ('text/plain', '%s saved' % cpu)

def graph_cpu(_):
  """return a png"""
  rrdtool.graph('../rrdtool/jjo.png',
      'DEF:cpu=../rrdtool/jjo.rrd:cpurate:AVERAGE',
      'LINE1:cpu#ff0000:cpu')
  return ('text/plain', 'graphed')

def graph_cpu_png(_):
  """return a png"""
  return ('image/png',
      open('../rrdtool/jjo.png').read())


PATH_REGISTRY = {
    '/stat/cpu': get_cpu,
    '/sample/local': sample_local,
    '/graph/cpu': graph_cpu,
    '/graph/cpu/png': graph_cpu_png,
    }

def app(environ, start_response):
  """main fcgi entry point"""
  func = PATH_REGISTRY.get(environ['PATH_INFO'])
  if func is not None:
    if callable(func):
      content_type, val = func(environ)
      start_response('200 OK', [('Content-Type', content_type)])
      yield val

JIFFIES = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
WSGIServer(app).run()
