#!/usr/bin/env python
# Author: JuanJo Ciarlante <juanjosec@gmail.com>
#
# -*- coding: UTF-8 -*-
#
# TODO(jjo): improve doc
# TODO(jjo): un-prototype, make proper class(es) instead of funcs
"""
bogomon: self-contained Linux cpu monitor
"""

import os, re, time, rrdtool, thread, sys
from flup.server.fcgi import WSGIServer

def _read_cpu():
  """ Returns cpu usage from /proc/stat as integer millisecs,
      prefixed by epoch timestamp"""
  cpu_string = open('/proc/stat').read()
  cpu_array = re.match('(cpu)\W+(\d+) (\d+) (\d+) (\d+)', cpu_string).groups()
  user, user_nice, system = [int(x) for x in cpu_array[1:4]]
  used = user+user_nice+system
  STATS['cpu_latest'] = used
  return ( time.time(), int(used*1e3/CONFIG['JIFFIES']))

def stat_cpu_txt(_, txt_prefix):
  """Returns cumulative used (user+system) as integer milli-secs"""
  timestamp, cpu = _read_cpu()
  return "%s%s %s" % (txt_prefix, timestamp, cpu)
 
def save_cpu_sto(_, txt_prefix):
  """Samples local cpu and saves to local RRD db"""
  STATS['cpu_stos'] = STATS['cpu_stos'] + 1
  cpu = _read_cpu()
  rrdtool.update(CONFIG['RRD_FILE'], '-t', 'cpurate',
      '%s:%s' % (cpu[0], cpu[1]))
  return '%s%s saved' % (txt_prefix, cpu)

def save_cpu_png(_, txt_prefix):
  """Builds a PNG from the locally saved statistics"""
  STATS['cpu_pngs'] = STATS['cpu_pngs'] + 1
  STATS['png_timestamp'] = time.time()
  rrdtool.graph(CONFIG['PNG_FILE'],
      'DEF:cpu=%s:cpurate:AVERAGE' % CONFIG['RRD_FILE'], 'LINE1:cpu#ff0000:cpu')
  return "%sgraph saved" % (txt_prefix)

def graph_cpu_png(_env, _txt):
  """Returns the contents of saved PNG"""
  now = time.time()
  # Don't save more than 1 each 10sec
  if STATS['png_timestamp'] + 10 < now:
    save_cpu_sto(_env, _txt)
    save_cpu_png(_env, _txt)
  return open(CONFIG['PNG_FILE']).read()

def stats_html(_, txt_prefix):
  """Returns an HTML page pointing to self's PNG"""
  STATS['hits'] = STATS['hits'] + 1
  return """
  <meta http-equiv="refresh" content="10">
  <html>
    <head><title>%(title)s</title></head>
    <body>
      hits: %(hits)s<br>
      crons: %(crons)s<br>
      cpu_stos: %(cpu_stos)s<br>
      cpu_pngs: %(cpu_pngs)s<br>
      cpu_latest: %(cpu_latest)s<br>
      <img src="%(img)s"/>
    </body>
  </html>
  """ % {
      'title': txt_prefix,
      'img': "/r/stat/cpu/png",
      'hits': STATS['hits'],
      'crons': STATS['crons'],
      'cpu_stos': STATS['cpu_stos'],
      'cpu_pngs': STATS['cpu_pngs'],
      'cpu_latest' : STATS['cpu_latest'],
  }

def _cron_save_cpu():
  """ Periodically save cpu state """
  while True:
    STATS['crons'] = STATS['crons'] + 1
    save_cpu_sto([], "")
    time.sleep(10)

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

## "globals":
CONFIG = {
    # Kernel's TZ: pretty global :) 
    'JIFFIES': os.sysconf(os.sysconf_names['SC_CLK_TCK']),
    # Quick&dirty: 1st arg it RDD path
    'RRD_FILE': sys.argv[1],
    'PNG_FILE': sys.argv[2],
}

STATS = {
    'hits': 0,
    'crons': 0,
    'cpu_stos': 0,
    'cpu_pngs': 0,
    'cpu_latest': 0,
    'png_timestamp': time.time(),
}

PATH_REGISTRY = {
    '/stats.html':      ["text/html",  stats_html ],
    '/r/stat/cpu/txt':  ["text/plain", stat_cpu_txt ],
    '/r/stat/cpu/png':  ["image/png",  graph_cpu_png ],
    '/w/save/cpu/sto':  ["text/plain", save_cpu_sto ],
    '/w/save/cpu/png':  ["text/plain", save_cpu_png ],
}

def main():
  """ main fcgi loop """
  thread.start_new_thread(_cron_save_cpu, ())
  WSGIServer(app).run()

if __name__ == "__main__":
  main()
