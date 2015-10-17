import os
import os.path
import platform
import sys

def isPythonFrozen():
	return hasattr( sys, "frozen" )

def _getMainModulePath():
		if isPythonFrozen():
			p = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
			if platform.system() == u'Darwin':
				return os.path.realpath( p + '/../../..' )
			elif platform.system() == u'Windows':
				return p
			else:
				return p
		if __name__ == 'main':
			mainfile = os.path.realpath( __file__ )
			return os.path.dirname( mainfile )
		else:
			import __main__
			if hasattr( __main__, "__gii_path__" ):
				return __main__.__gii_path__
			else:
				mainfile = os.path.realpath( __main__.__file__ )
				return os.path.dirname( mainfile )


def getMainModulePath( path = None ):
	base = _getMainModulePath()
	if not path: return base
	return base + '/' + path
