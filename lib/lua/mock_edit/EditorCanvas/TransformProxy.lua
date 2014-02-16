module 'mock_edit'

--------------------------------------------------------------------
--Transform Proxy
--------------------------------------------------------------------
CLASS: TransformProxy( EditorEntity )

function TransformProxy:__init()
	self.updateNode = MOAIScriptNode.new()	
	self.syncing = false
end

function TransformProxy:setTargets( targets )
	self.targets = targets
	local proxies = {}
	self.proxies = proxies

	local count = 0
	local prop  = self._prop
	for e in pairs( targets ) do		
		local proxy = MOAITransform.new()
		proxies[e] = proxy
		inheritTransform( proxy, prop )
		count = count + 1
	end
	self.targetCount = count
	self:updatePivot()
	self:syncFromTarget()
	self.updateNode:setCallback( function() self:onUpdate() end )
	self.updateNode:setNodeLink( self._prop )
end

function TransformProxy:preTransform()
	self:syncFromTarget()
	self.scl0 = {self:getScl()}
	self.rot0 = {self:getRot()}
end

function TransformProxy:updatePivot()
	local totalX, totalY = 0, 0
	for e in pairs( self.targets ) do
		e:forceUpdate()		
		local x1,y1 = e:modelToWorld( e:getPiv() )
		totalX = totalX + x1
		totalY = totalY + y1		
	end
	local count = self.targetCount
	self:setLoc( totalX/count, totalY/count, 0 )	

	if count == 1 then
		self.rot0 = next( self.targets ):getRotZ()
	else
		self.rot0 = 0
	end
	self:setRotZ( self.rot0 )
end

function TransformProxy:syncFromTarget()
	self.syncing = true
	self:forceUpdate()
	for e, proxy in pairs( self.proxies ) do
		e:forceUpdate()
		proxy:forceUpdate()
		GIIHelper.setWorldLoc( proxy, e:getWorldLoc() )
		proxy:setScl( e:getScl() )
		proxy:setRot( e:getRot() )
		proxy:forceUpdate()
	end
	self.syncing = false
end

function TransformProxy:onUpdate()
	if self.syncing then return end
	self.syncing = true
	self:forceUpdate()
	local rx0, ry0, rz0 = unpack( self.rot0 )
	local sx0, sy0, sz0 = unpack( self.scl0 )
	local sx1, sy1, sz1 = self:getScl()
	local rx1, ry1, rz1 = self:getRot()
	local ssx, ssy ,ssz = 0,0,0
	if sx1 ~= 0 then ssx = sx1/sx0 end
	if sy1 ~= 0 then ssy = sy1/sy0 end
	if sz1 ~= 0 then ssz = sz1/sz0 end
	for e, proxy in pairs( self.proxies ) do
		e:forceUpdate()
		proxy:forceUpdate()
		GIIHelper.setWorldLoc( e:getProp(), proxy:getWorldLoc() )
		local sx, sy, sz = proxy:getScl()
		local rx, ry, rz = proxy:getRot()
		e:setScl( sx*ssx, sy*ssy, sz*ssz )
		e:setRot( rx+rx1-rx0, ry+ry1-ry0, rz+rz1-rz0 )
		e:forceUpdate()
		gii.emitPythonSignal( 'entity.modified', e )
	end
	self.syncing = false
end
