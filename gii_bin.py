##----------------------------------------------------------------##
#find gii library
import os
import os.path
import platform
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
			mainfile = os.path.realpath( __main__.__file__ )
			return os.path.dirname( mainfile )

giipath = getMainModulePath() + '/lib'
thirdPartyPathBase = getMainModulePath() + '/lib/3rdparty'
thirdPartyPathCommon = thirdPartyPathBase + '/common'
if platform.system() == u'Darwin':
	thirdPartyPathNative = thirdPartyPathBase + '/osx'
else:
	thirdPartyPathNative = thirdPartyPathBase + '/windows'
sys.path.insert( 0, giipath )
sys.path.insert( 2, thirdPartyPathNative )
sys.path.insert( 1, thirdPartyPathCommon )

##----------------------------------------------------------------##
import gii_cfg
import gii
##----------------------------------------------------------------##
DO_PROFILE = False
gii.MODULEPATH=[
	giipath,
	thirdPartyPathNative,
	thirdPartyPathCommon,
]

PYTHONPATH0 = os.getenv( 'PYTHONPATH' )
PYTHONPATH1 = (PYTHONPATH0 and PYTHONPATH0 + ':' or '') + ( ':'.join( gii.MODULEPATH ) )
os.putenv('PYTHONPATH', PYTHONPATH1)

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
	if isPythonFrozen():
		sys.argv = ['gii', 'stub']
	main()
