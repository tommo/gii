from PIL import Image
import StringIO
from psd_tools import PSDImage, Group, Layer
from psd_tools.constants import ImageResourceID
from psd_tools.utils import read_fmt, read_unicode_string, read_pascal_string

##----------------------------------------------------------------##
def read_psd_string ( f ):
	l, = read_fmt("I", f)
	if l==0: l = 4;
	return f.read( l )

def read_psd_obj( f, vt = None ):
	if not vt: vt = f.read( 4 )
	if vt == 'long':
		v, = read_fmt('l', f)
		return v

	elif vt == 'bool':
		result, = read_fmt('b', f)
		return result != 0

	elif vt == 'doub':
		result, = read_fmt('d', f)
		return result

	elif vt == 'VlLs':
		count, = read_fmt('I', f)
		result = []
		for i in range( 0, count ):
			v = read_psd_obj( f )
			result.append (v)
		return result

	elif vt == 'Objc':
		nameLen, = read_fmt("I", f)
		f.seek( nameLen * 2, 1 ) #skip name
		classId = read_psd_string( f )
		count, = read_fmt("I", f)
		result = {}
		for i in range( 0, count ):
			key = read_psd_string( f )
			value = read_psd_obj( f )
			result[key] = value
		return result

	elif vt == 'enum':
		typeId = read_psd_string( f )
		value = read_psd_string( f )
		return ( typeId, value )

	elif vt == 'UntF':
		unit = f.read(4)
		value, = read_fmt('d', f)
		return (value, unit)
	
	elif vt == 'TEXT':
		size, = read_fmt("I", f)
		text = f.read( size * 2 ) #TODO: unicode?
		return text

	else:
		raise Exception('not implement: %s ' % vt )

def get_mlst( layer ):
	for md in layer._tagged_blocks['shmd']:
		if md.key == 'mlst':
			f = StringIO.StringIO( md.data )
			f.read(4)
			desc = read_psd_obj( f, 'Objc' )
			return desc
	return None

def get_mani( image ):
	for r in image.decoded_data.image_resource_blocks:
		if r.resource_id == 4000:
			f = StringIO.StringIO( r.data )		
			pluginName = f.read(4)
			assert pluginName == 'mani', pluginName 
			f.seek( 24, 1 )
			desc = read_psd_obj( f, 'Objc' )
			return desc
	return None
