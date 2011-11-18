## THIS FILE IS NOT PART OF THE DEPLOYMENT
## ... just a quick hack-all-together, for quick devel
NGINX_PORT=8000
BOGOMON_PORT=9000
BOGOMON_PY=usr/lib/bogomon/bogomon.fcgi.py
BOGOMON_VAR_RUN=./var/run
BOGOMON_VAR_LIB=./var/lib

BOGOMON_PIDFILE=$(BORGMON_VAR_RUN)/bogomon.fcgi.pid
RRD_DIR=$(BOGOMON_VAR_LIB)/bogomon
RRD_FILE=$(RRD_DIR)/local.rrd
PNG_FILE=$(RRD_DIR)/local.png

REQ_PKGS=python-flup python-rrdtool
REQ_BINS=spawn-fcgi rrdtool


help:
	@echo read the Makefile

norootplease:
	test `id -u` -ne 0

check-dependencies:
	which $(REQ_BINS)
	$(foreach pkg, $(REQ_PKGS), dpkg -s $(pkg) | egrep "^Package:";)

prep:	
	test -d $(RRD_DIR) || mkdir -p $(RRD_DIR)
	test -d $(BOGOMON_VAR_RUN) || mkdir -p $(BOGOMON_VAR_RUN)

help-banner:
	@echo -e '\n********\nUse: http://127.0.0.1:$(NGINX_PORT)/stats.html\n\nYou should have done:\nmake show_nginx_conf | sudo tee /etc/nginx/sites-enabled/bogomon && sudo /etc/init.d/nginx reload\n\n********\n'

run: norootplease check-dependencies prep $(BOGOMON_PY) help-banner
	spawn-fcgi -n -P $(BOGOMON_PIDFILE) -d $(PWD)/$(BOGOMON_VAR_RUN) -a 127.0.0.1 -p $(BOGOMON_PORT) -- \
	       	$(PWD)/$(BOGOMON_PY)  $(PWD)/$(RRD_FILE) $(PWD)/$(PNG_FILE)

distclean: norootplease
	rm -rf $(BOGOMON_VAR_RUN) $(BOGOMON_VAR_LIB)

show_nginx_conf:
	@echo -e 'server {\n  listen $(NGINX_PORT);\n  location / {\n    include /etc/nginx/fastcgi_params;\n    fastcgi_pass 127.0.0.1:$(BOGOMON_PORT);\n  }\n}'
