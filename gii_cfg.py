import logging
##----------------------------------------------------------------##
#CONFIG
LOG_LEVEL = logging.WARNING
# LOG_LEVEL = logging.INFO

##----------------------------------------------------------------##
##APPLY CONFIG

logging.basicConfig(
	format = '[%(levelname)s]\t%(message)s',
	level  = LOG_LEVEL
	)
