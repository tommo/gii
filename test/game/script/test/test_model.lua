-- require 'model'

-- local Field=model.Field
-- local Model=model.Model
-- local Meta=model.Meta



-- function setupModel(clas, name, model)
-- end

-- function setupConfig(target, configName)
-- 	configName=configName or 'default'
-- end

-- [[
-- -----------------------------------------------
-- 	MOAIProp* 	prop;
-- 	int					x,y,z;
-- 	Profile 		profile;
-- -----------------------------------------------
-- 	Field.MOAIProp 	"prop";
-- 	Field.int				("x","y","z");
-- 	Field.Profile		"profile";
-- -----------------------------------------------
-- 	prop 		= ref(MOAIProp)
-- 	x,y,z 	= int()
-- 	profile = sub{ name = str(), age = int() }
-- -----------------------------------------------
-- 	field		prop		:MOAIProp @{ref}
-- 	field		x,y,z		:number		@{integer}
-- 	field		profile	:Profile	@{sub}
-- -----------------------------------------------

-- ]]


-- CLASS: TestObject ( Entity )
-- setupModel(TestObject,'TestObject',
-- 		{	
-- 			Field.ref 'prop' {type='MOAIProp'};
-- 		}
-- 	)

-- function TestObject:onLoad()
-- 	self.prop=self:addProp{deck=res.tex['creature_devil']}
-- 	setupConfig(self)
-- end

-- function OnTestStart(m)
-- 	local o=m:addChild(TestObject())

-- end