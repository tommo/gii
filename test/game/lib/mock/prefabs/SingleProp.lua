CLASS: SingleProp ( Object )
--simple deck container
--TODO: add init from texture

function SingleProp:onInit(option)
	self.propOption=option.prop
end

function SingleProp:onLoad()
	self.prop=self:addProp(self.propOption)
end
