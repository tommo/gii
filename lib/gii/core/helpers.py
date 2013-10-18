import traceback
def printTraceBack():
	try:
		1/0
	except Exception as e:
		traceback.print_stack()
