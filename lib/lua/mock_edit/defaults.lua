module 'mock_edit'

addColor( 'white', 1,1,1,1 )
addColor( 'black', 0,0,0,1 )

local alpha = 0.8
addColor( 'selection', 0,1,1, alpha )
addColor( 'handle-x',  1,0,0, alpha )
addColor( 'handle-y',  0,1,0, alpha )
addColor( 'handle-z',  0,0,1, alpha )
addColor( 'handle-all', 1,1,0, alpha )
addColor( 'handle-active', 1,1,0, alpha )

addColor( 'handle-previous', 1,0,0, .3 )

addColor( 'gizmo_trigger', hexcolor( '#6695ff', 0.1 ) )
addColor( 'gizmo_trigger_border', hexcolor( '#6695ff', 0.7 ) )

addColor( 'cp',  hexcolor( '#1c57ff', alpha ) )
addColor( 'cp-border', hexcolor( '#ffffff', alpha ) )


addColor( 'misc',  hexcolor( '#6695ff', 0.1 ) )
addColor( 'misc-transform',  hexcolor( '#b8ff00', 1 ) )

addColor( 'camera-bound', hexcolor( '#ffc900', alpha ) )

addColor( 'shape-line',  hexcolor( '#ff6cf9', 1 ))
addColor( 'shape-fill',  hexcolor( '#ffd371', .3 ))
