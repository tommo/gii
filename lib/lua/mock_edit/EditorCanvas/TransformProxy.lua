module 'mock_edit'

--------------------------------------------------------------------
--Transform Proxy
--------------------------------------------------------------------
CLASS: TransformProxy( mock.Entity )

function TransformProxy:__init()
	self.updateNode = MOAIScriptNode.new()
	self.updateNode:setCallback( function() self:onUpdate() end )
	self.updateNode:setNodeLink( self._prop )
end

function TransformProxy:setTargets( targets )
	self.targets = targets
	local proxies = {}
	self.proxies = proxies
	local count = 0

	local trans = self._prop

	local totalX, totalY = 0, 0
	for e in pairs( targets ) do
		e:forceUpdate()
		local x1,y1 = e:modelToWorld( e:getPiv() )
		totalX = totalX + x1
		totalY = totalY + y1
		count = count + 1
		local proxy = MOAITransform.new()
		proxies[e] = proxy
		inheritTransform( proxy, trans )
	end

	self:setLoc( totalX/count, totalY/count, 0 )
	self.rot0 = 0
	if count == 1 then
		self.rot0 = next(targets):getRotZ()
		self:setRotZ( self.rot0 )
	end
	trans:forceUpdate()
	self:syncFromTarget()
end

function TransformProxy:syncFromTarget()
	for e, proxy in pairs( self.proxies ) do
		e:forceUpdate()
		local px, py, pz = e:getPiv()
		local x, y, z = self:worldToModel( e:modelToWorld( px,py,pz ) )
		proxy:setLoc( x, y, z )
		local rx,ry,rz = e:getRot()
		proxy:setRot( rx, ry, rz )
		proxy.rz0 = rz
		proxy:setScl( e:getScl() )
	end
	self:forceUpdate()
end

local function syncWorldLoc( e, proxy )
	local x,y,z = proxy:modelToWorld( 0,0,0 )
	local p = e.parent
	local x0,y0,z0 = e:getLoc()
	if p then
		x, y, z = p:worldToModel( x, y, z )
		e:setLoc( x, y, z0 )
	else
		e:setLoc( x, y, z0 )
	end
end

local function getWorldRot( e )

end

local function setWorldRot( e )

end

function TransformProxy:onUpdate()
	local sx,sy,sz = self:getScl()
	local rx,ry,rz = self:getRot()
	for e, proxy in pairs( self.proxies ) do
		proxy:forceUpdate()
		syncWorldLoc( e, proxy )
		local sx1,sy1,sz1 = proxy:getScl()
		local rx1,ry1,rz1 = proxy:getRot()
		e:setScl( sx*sx1, sy*sy1, sz1 )
		e:setRot( rx+rx1, ry+ry1, rz + rz1 - self.rot0 )
		gii.emitPythonSignal( 'entity.modified', e )
	end
end
