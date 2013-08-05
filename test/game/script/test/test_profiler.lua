CLASS: TestProfiler ( Entity )
function TestProfiler:onLoad()

	local box=MOAIProfilerReportBox.new()
	self:addRawProp(box,{shader='color-tex'})
	box:setFont(res.fonts['small'])
	box:setFontSize(8)
	box:setRect(0,0,100,100)
	box:enableProfiling()

end

function OnTestStart(logic)
	logic:addSibling(TestProfiler())
end


