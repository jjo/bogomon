while ((typeset -a a=($(curl -s4 http://localhost:8000/stat/cpu));echo rrdupdate jjo.rrd -t cpurate ${a[2]}:${a[3]}) | bash -x);do sleep 1;done
