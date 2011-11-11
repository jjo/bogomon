#rrdtool graph jjo.png DEF:cpu=jjo.rrd:cpurate:AVERAGE LINE1:cpu#ff0000:Cpu
rrdtool graph -s -10min jjo.png DEF:cpumsec=var/lib/bogomon/local.rrd:cpurate:AVERAGE CDEF:cpu=cpumsec,1000,/ LINE1:cpu#ff0000:cpu
