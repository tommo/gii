import os
import os.path
import sys

def isPythonFrozen():
	return hasattr(sys, "frozen")

def getMainModulePath():
		if isPythonFrozen():
			return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
		if __name__ == 'main':
			mainfile = os.path.realpath( __file__ )
			return os.path.dirname( mainfile )
		else:
			import __main__
			mainfile = os.path.realpath( __main__.__file__ )
			return os.path.dirname( mainfile )


