#!/usr/bin/make -f
# Waf Makefile wrapper
WAF_HOME=/Volumes/prj/gii/support/waf

all:
#@/Volumes/prj/gii/support/waf/waf build

all-debug:
	@/Volumes/prj/gii/support/waf/waf -v build

all-progress:
	@/Volumes/prj/gii/support/waf/waf -p build

install:
	/Volumes/prj/gii/support/waf/waf install --yes;

uninstall:
	/Volumes/prj/gii/support/waf/waf uninstall

clean:
	@/Volumes/prj/gii/support/waf/waf clean

distclean:
	@/Volumes/prj/gii/support/waf/waf distclean
	@-rm -rf build
	@-rm -f Makefile

check:
	@/Volumes/prj/gii/support/waf/waf check

dist:
	@/Volumes/prj/gii/support/waf/waf dist

.PHONY: clean dist distclean check uninstall install all

