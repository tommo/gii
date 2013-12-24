from gii.core import app
import subprocess

def convertToWebP( src, dst = None, **option ):
	arglist = [
		app.getPath( 'support/webp/cwebp' ),
		'-quiet'
		# '-hint', 'photo'
	]
	quality = option.get( 'quality', 100 )
	if quality == 'lossless':
		arglist += ['-lossless']
	else:
		arglist += [ '-q', str(quality) ]
	if not dst:
		dst = src
	arglist += [
		src,
		'-o',
		dst
	 ]

	# print 'convert to webp %s -> %s' % ( src, dst )
	# if src == dst: return #SKIP
	return subprocess.call( arglist )
