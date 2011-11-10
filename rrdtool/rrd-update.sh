awk '/cpu /{ print "rrdupdate jjo.rrd -t cpurate N:"($2+$3+$4) }' /proc/stat
