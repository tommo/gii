module 'mock'

CLASS: TiledTextureRect ( RenderComponent )
	:MODEL{
		Field 'shader' :asset( 'shader' ) :no_edit();

		Field 'texture'  :asset('texture;framebuffer') :getset( 'Texture' );
		Field 'size'     :type('vec2') :getset('Size');
		Field 'tileSize' :type('vec2') :getset('TileSize');
		'----';
		Field 'resetSize' :action( 'resetSize' );
	}

registerComponent( 'TiledTextureRect', TiledTextureRect )

local _tileTextureShaderProgram

local function buildShader()
	if not _tileTextureShaderProgram then
		local prog = ShaderProgram()

		prog.vsh = [[
				attribute vec4 position;
				attribute vec2 uv;
				attribute vec4 color;

				varying MEDP vec2 uvVarying;
				varying LOWP vec4 colorVarying;

				void main () {
					gl_Position = position;
					uvVarying = uv;
					colorVarying = color;
				}
			]]

		prog.fsh = [[				
				varying LOWP vec4 colorVarying;
				varying MEDP vec2 uvVarying;
				uniform sampler2D sampler;
				uniform float hueOffset;

				vec3 rgb2hsv(vec3 c)
				{
				    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
				    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
				    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

				    float d = q.x - min(q.w, q.y);
				    float e = 1.0e-10;
				    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
				}

				vec3 hsv2rgb(vec3 c)
				{
				    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
				    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
				    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
				}

				void main () {
					LOWP vec4 tex = texture2D ( sampler, uvVarying );
					LOWP vec3 hsv = rgb2hsv( tex.rgb );
					if( hsv.x>0.5 && hsv.x<0.7)
					{
						hsv.x = hueOffset;
						LOWP vec3 rgb = hsv2rgb( hsv );
						tex.r = mix( tex.r, rgb.r, 0.5);
						tex.g = mix( tex.g, rgb.g, 0.5);
						tex.b = mix( tex.b, rgb.b, 0.5);
					}
					gl_FragColor = tex * colorVarying;
				}
			]]

		prog.uniforms   = { 
			{ type = 'float', name = 'hueOffset', value = 0 }
		}
		prog:build()
		_tileTextureShaderProgram = prog
	end
	return _tileTextureShaderProgram:requestShader()
end

function TiledTextureRect:__init()
	self.texture = false
	self.w = 100
	self.h = 100
	self.tw = 50
	self.th = 50
	self.deck = mock.Quad2D()
	self.deck:setSize( 100, 100 )
	self.prop = MOAIProp.new()
	self.prop:setDeck( self.deck:getMoaiDeck() )
	local shader = buildShader()
	self.prop:setShader( shader:getMoaiShader() )
end

function TiledTextureRect:onAttach( ent )
	ent:_attachProp( self.prop )
end

function TiledTextureRect:onDetach( ent )
	ent:_detachProp( self.prop )
end

function TiledTextureRect:getTexture()
	return self.texture
end

function TiledTextureRect:setTexture( t )
	self.texture = t
	self.deck:setTexture( t, false ) --dont resize
	self.deck:update()
	self.prop:forceUpdate()
end

function TiledTextureRect:getSize()
	return self.w, self.h
end

function TiledTextureRect:setSize( w, h )
	self.w = w
	self.h = h
	self.deck:setSize( w, h )
	self.deck:update()
	self.prop:forceUpdate()
end


function TiledTextureRect:getTileSize()
	return self.tw, self.th
end

function TiledTextureRect:setTileSize( w, h )
	self.tw = w
	self.th = h	
end

function TiledTextureRect:setBlend( b )
	self.blend = b
	mock.setPropBlend( self.prop, b )
end

function TiledTextureRect:setScissorRect( s )
	self.prop:setScissorRect( s )
end

function TiledTextureRect:resetSize()
	if self.texture then
		local tex = mock.loadAsset( self.texture )
		self:setSize( tex:getSize() )
	end
end

