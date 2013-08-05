CLASS: OffsetGrid ( Entity )
function OffsetGrid:onLoad()
		g:initRectGrid(w,h,16,16
			-- ,.5,.5
			)

		local prop=self:addProp{
			deck=res.tile
		}
		prop:setGrid(g)
		self:setPiv(self:getTileLoc(
				cx,cy
			)
		)
		self:forceUpdate()
		
end