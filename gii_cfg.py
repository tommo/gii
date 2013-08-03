import logging
##----------------------------------------------------------------##
#CONFIG
LOG_LEVEL = logging.WARNING
LOG_LEVEL = logging.INFO

##----------------------------------------------------------------##
##APPLY CONFIG
logging.addLevelName( logging.INFO, 'STATUS' )
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = "\033[1m"

logging.basicConfig(
	format = '[%(levelname)s]\t%(message)s',
	level  = LOG_LEVEL
	)
