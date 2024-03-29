#!/usr/bin/env python
# Author: JuanJo Ciarlante <juanjosec@gmail.com>
# License: GPLv3
#
# -*- coding: UTF-8 -*-
#
# TODO(jjo): improve doc
# TODO(jjo): un-prototype, make proper class(es) instead of funcs
"""
bogomon: self-contained Linux cpu monitor
"""

import os, re, time, rrdtool, thread, sys, subprocess
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

def stat_cpu_txt(txt_prefix):
  """Returns cumulative used (user+system) as integer milli-secs"""
  timestamp, cpu = _read_cpu()
  return "%s%s %s" % (txt_prefix, timestamp, cpu)
 
def save_cpu_sto(txt_prefix):
  """Samples local cpu and saves to local RRD db"""
  STATS['cpu_stos'] = STATS['cpu_stos'] + 1
  cpu = _read_cpu()
  rrdtool.update(CONFIG['RRD_FILE'], '-t', 'cpurate',
      '%s:%s' % (cpu[0], cpu[1]))
  return '%s%s saved' % (txt_prefix, cpu)

def save_cpu_png(txt_prefix):
  """Builds a PNG from the locally saved statistics"""
  STATS['cpu_pngs'] = STATS['cpu_pngs'] + 1
  STATS['png_timestamp'] = time.time()
  rrdtool.graph(CONFIG['PNG_FILE'],
      '-s', '-60min',
      'DEF:cpumsec=%s:cpurate:AVERAGE' % CONFIG['RRD_FILE'],
      'CDEF:cpu=cpumsec,1000,/',
      'LINE1:cpu#ff0000:cpu')
  return "%sgraph saved" % (txt_prefix)

def stat_cpu_png(_txt):
  """Returns the contents of saved PNG"""
  now = time.time()
  # Don't save more than 1 per PNG_CACHE_EXPIRE_SECS
  if STATS['png_timestamp'] + CONFIG['PNG_CACHE_EXPIRE_SECS'] < now:
    save_cpu_sto(_txt)
    save_cpu_png(_txt)
  return open(CONFIG['PNG_FILE']).read()

def stats_html(txt_prefix):
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

def ping(_txt):
  """ useful for blackbox monitoring """
  return "bogomon ok"

def _cron_save_cpu():
  """ Periodically save cpu state """
  while True:
    STATS['crons'] = STATS['crons'] + 1
    save_cpu_sto("")
    time.sleep(CONFIG['CPU_SAVE_PERIOD'])

def run_ab(_):
  """ DANGER: THIS SHOULD BE DISABLED :P
      Run ab (apache-benchmark) to do some local torture """
  pipe = subprocess.Popen('/usr/sbin/ab -n5000 -c10 '
      'http://127.0.0.1:80/ 2>&1',
      shell=True, bufsize=4096, stdout=subprocess.PIPE).stdout
  return pipe.read()


## "globals":
CONFIG = {
    # Kernel's TZ: pretty global :) 
    'JIFFIES': os.sysconf(os.sysconf_names['SC_CLK_TCK']),
    # Quick&dirty: 1st arg it RDD path
    'RRD_FILE': sys.argv[1],
    'PNG_FILE': sys.argv[2],
    'CPU_SAVE_PERIOD': 2,
    'PNG_CACHE_EXPIRE_SECS': 2,
}

STATS = {
    'hits': 0,
    'crons': 0,
    'cpu_stos': 0,
    'cpu_pngs': 0,
    'cpu_latest': 0,
    'png_timestamp': 0,
}

PATH_REGISTRY = {
    '/stats.html':      ["text/html",  stats_html ],
    '/r/ping':          ["text/plain", ping ],
    '/r/stat/cpu/txt':  ["text/plain", stat_cpu_txt ],
    '/r/stat/cpu/png':  ["image/png",  stat_cpu_png ],
    '/w/save/cpu/sto':  ["text/plain", save_cpu_sto ],
    '/w/save/cpu/png':  ["text/plain", save_cpu_png ],
    '/r/run/t0rtur3':   ["text/plain", run_ab ],
}

def app(environ, start_response):
  """main fcgi entry point"""
  path = environ.get('PATH_INFO')
  content_type, func = PATH_REGISTRY.get(path, [None, None])
  if func is not None:
    txt_prefix = "%s: %s " % (environ.get('SERVER_NAME'), path)
    start_response('200 OK', [('Content-Type', content_type)])
    yield func(txt_prefix)
  else:
    start_response('404 Not found', [('Content-Type', 'text/plain')])
    yield "Not found\n"

def main():
  """ main fcgi loop """
  thread.start_new_thread(_cron_save_cpu, ())
  if not os.path.exists(CONFIG['RRD_FILE']):
    rrdtool.create(CONFIG['RRD_FILE'], '-s', 5*CONFIG['CPU_SAVE_PERIOD'],
      'DS:cpurate:COUNTER:6:U:U', 'RRA:AVERAGE:0.5:1:360',
      'RRA:AVERAGE:0.5:10:36')
  WSGIServer(app).run()

if __name__ == "__main__":
  main()
