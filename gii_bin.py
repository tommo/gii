##----------------------------------------------------------------##
#find gii library
import os
import os.path
import sys

try:
	import faulthandler
	faulthandler.enable()
except Exception, e:
	pass

def isPythonFrozen():
	return hasattr( sys, "frozen" )

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

giipath = getMainModulePath() + '/lib'
thirdPartyPath = getMainModulePath() + '/lib/3rdparty'
sys.path.insert( 0, giipath )
sys.path.insert( 1, thirdPartyPath )

##----------------------------------------------------------------##
import gii_cfg
import gii
##----------------------------------------------------------------##
DO_PROFILE = False

def main():
 	if DO_PROFILE:
		import cProfile, pstats, io
		pr = cProfile.Profile()
		pr.enable()

		gii.startup()

		pr.disable()
		ps = pstats.Stats(pr)
		ps.sort_stats( 'calls', 'time' )
		ps.print_stats()
	else:
		gii.startup()

if __name__ == '__main__':
	main()
