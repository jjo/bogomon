rrdtool create jjo.rrd DS:cpurate:COUNTER:60:U:U RRA:AVERAGE:0.5:1:120 RRA:AVERAGE:0.5:10:60
