BOGOMON_PORT=9000
BOGOMON_PY=web/bogomon.fcgi.py
BOGOMON_PIDFILE=./var/lib/bogomon.fcgi.pid
BOGOMON_VAR_RUN=./var/run
help:
	@echo read the Makefile
deps:
	@which spawn-fcgi
run: deps $(BOGOMON_PY) 
	spawn-fcgi -n -P $(BOGOMON_PIDFILE) -d $(PWD)/$(BOGOMON_VAR_RUN) -f $(PWD)/$(BOGOMON_PY)  -a 127.0.0.1 -p $(BOGOMON_PORT)

