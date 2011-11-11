BOGOMON_PORT=9000
BOGOMON_PY=web/bogomon.fcgi.py
BOGOMON_VAR_RUN=./var/run
BOGOMON_VAR_LIB=./var/lib

BOGOMON_PIDFILE=$(BORGMON_VAR_RUN)/bogomon.fcgi.pid
RRD_DIR=$(BOGOMON_VAR_LIB)/bogomon
RRD_FILE=$(RRD_DIR)/local.rrd
PNG_FILE=$(RRD_DIR)/local.png

REQ_PKGS=python-flup
REQ_BINS=spawn-fcgi rrdtool


help:
	@echo read the Makefile

norootplease:
	test `id -u` -ne 0

deps:
	@which $(REQ_BINS)
	@for i in $(REQ_PKGS);do dpkg -s $$i || exit 1;done | egrep ^Package:

prep:	
	test -d $(RRD_DIR) || mkdir -p $(RRD_DIR)
	test -d $(BOGOMON_VAR_RUN) || mkdir -p $(BOGOMON_VAR_RUN)
	test -f $(RRD_FILE) || \
		rrdtool create $(RRD_FILE) DS:cpurate:COUNTER:60:U:U RRA:AVERAGE:0.5:1:120 RRA:AVERAGE:0.5:10:60

run: norootplease deps prep $(BOGOMON_PY) 
	spawn-fcgi -n -P $(BOGOMON_PIDFILE) -d $(PWD)/$(BOGOMON_VAR_RUN) -a 127.0.0.1 -p $(BOGOMON_PORT) -- \
	       	$(PWD)/$(BOGOMON_PY)  $(PWD)/$(RRD_FILE) $(PWD)/$(PNG_FILE)

distclean: norootplease
	rm -rf $(BOGOMON_VAR_RUN) $(BOGOMON_VAR_LIB)

show_nginx_conf:
	@echo $$'server {\n  listen 8000;\n  location / {\n    include /etc/nginx/fastcgi_params;\n    fastcgi_pass 127.0.0.1:$(BOGOMON_PORT);\n  }\n}'
