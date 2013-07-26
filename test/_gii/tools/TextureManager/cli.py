import argparse
import sys

_top = argparse.ArgumentParser( description = 'Texture Manager' )
_top.add_argument( '-u', '--update', action = 'store_true', help = 'update modified textures and texture packs' )
_top.add_argument( '-v', '--verbose', action = 'store_true', help = 'show process log' )

def parse( argv = None ):
	if argv is None: argv = sys.argv
	return _top.parse_args( argv[1:] )