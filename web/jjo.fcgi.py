#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Implements foo"""

import os, re, time, rrdtool
from flup.server.fcgi import WSGIServer

def _read_cpu():
  """ returns cpu usage from /proc/stat in millisecs,
      prefixed by epoch timestamp"""
  cpu_string = open('/proc/stat').read()
  cpu_array = re.match('(cpu)\W+(\d+) (\d+) (\d+) (\d+)', cpu_string).groups()
  user, user_nice, system = [int(x) for x in cpu_array[1:4]]
  used = user+user_nice+system
  return ( time.time(), int(used*1e3/JIFFIES))

def stat_cpu_txt(_, txt_prefix):
  """Returns cumulative used (user+system) milli-seconds"""
  timestamp, cpu = _read_cpu()
  return "%s%s %s" % (txt_prefix, timestamp, cpu)
 
def save_cpu_sto(_, txt_prefix):
  """short cut to update local rrd"""
  cpu = _read_cpu()
  rrdtool.update('../rrdtool/jjo.rrd', '-t', 'cpurate',
      '%s:%s' % (cpu[0], cpu[1]))
  return '%s%s saved' % (txt_prefix, cpu)

def save_cpu_png(_, txt_prefix):
  """return a png"""
  rrdtool.graph('../rrdtool/jjo.png',
      'DEF:cpu=../rrdtool/jjo.rrd:cpurate:AVERAGE',
      'LINE1:cpu#ff0000:cpu')
  return "%sgraph saved" % (txt_prefix)

def graph_cpu_png(_env, _txt):
  """return a png"""
  now = time.time()
  if STATS['png_timestamp'] + 1 < now:
    save_cpu_sto(_env, _txt)
    save_cpu_png(_env, _txt)
  return open('../rrdtool/jjo.png').read()

def stats_html(_, txt_prefix):
  """return an HTML page pointing to self"""
  STATS['hits'] = STATS['hits'] + 1
  return """
  <meta http-equiv="refresh" content="10">
  <html>
    <head><title>%(title)s</title></head>
    <body>
      hits: %(hits)s<br>
      <img src="%(img)s"/>
    </body>
  </html>
  """ % {
      'title': txt_prefix,
      'img': "/r/stat/cpu/png",
      'hits': STATS['hits']
  }

STATS = {
    'hits': 0,
    'png_timestamp': time.time(),
}

PATH_REGISTRY = {
    '/stats.html':      ["text/html",  stats_html ],
    '/r/stat/cpu/txt':  ["text/plain", stat_cpu_txt ],
    '/r/stat/cpu/png':  ["image/png",  graph_cpu_png ],
    '/w/save/cpu/sto':  ["text/plain", save_cpu_sto ],
    '/w/save/cpu/png':  ["text/plain", save_cpu_png ],
}

def app(environ, start_response):
  """main fcgi entry point"""
  path = environ.get('PATH_INFO')
  content_type, func = PATH_REGISTRY.get(path, [None, None])
  if func is not None:
    txt_prefix = "%s: %s " % (environ.get('SERVER_NAME'), path)
    start_response('200 OK', [('Content-Type', content_type)])
    yield func(environ, txt_prefix)
  else:
    start_response('404 Not found', [('Content-Type', 'text/plain')])
    yield "Not found\n"

JIFFIES = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
WSGIServer(app).run()
