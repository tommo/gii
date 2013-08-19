import os
import os.path
import sys

def isPythonFrozen():
	return hasattr(sys, "frozen")

def _getMainModulePath():
		if isPythonFrozen():
			return os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
		if __name__ == 'main':
			mainfile = os.path.realpath( __file__ )
			return os.path.dirname( mainfile )
		else:
			import __main__
			mainfile = os.path.realpath( __main__.__file__ )
			return os.path.dirname( mainfile )


def getMainModulePath( path = None ):
	base = _getMainModulePath()
	if not path: return base
	return base + '/' + path
