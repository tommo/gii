import p2t

def triangulatePolygon( verts, holes = None ):
	polyline = []
	for i in range( 0, len( verts ), 2 ):
		polyline.append( p2t.Point( verts[i], verts[i+1] ) )

	cdt = p2t.CDT( polyline )
	if holes:
		for hole in holes:
			cdt.add_hole( hole )
	triangles = cdt.triangulate()
	result = []
	for t in triangles:
		result.append( t.a.x )
		result.append( t.a.y )
		result.append( t.b.x )
		result.append( t.b.y )
		result.append( t.c.x )
		result.append( t.c.y )
	return result