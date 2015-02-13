module 'mock'

local keymap_bmx={
	--		modifier_none    = 0;
	--		modifier_shift   = 1;                            -- shift key
	--		modifier_control = 2;                             -- ctrl key
	--		modifier_option  = 4;                      -- alt or menu key
	--		modifier_system  = 8;                 -- windows or apple key

		["backspace"] = 8;         ["left"]  = 37;
		["tab"]       = 9;         ["up"]    = 38;
		["clear"]     = 12;        ["right"] = 39;
		["enter"]    = 13;         ["down"]  = 40;
		["return"]= 13;
		["escape"]    = 27;        ["select"]  = 41;
		["space"]     = 32;        ["print"]   = 42;
		["pageup"]    = 33;        ["execute"] = 43;
		["pagedown"]  = 34;        ["screen"]  = 44;
		["end"]       = 35;        ["insert"]  = 45;
		["home"]      = 36;        ["delete"]  = 46;

		["0"] = 48;                ["num0"] = 96;
		["1"] = 49;                ["num1"] = 97;
		["2"] = 50;                ["num2"] = 98;
		["3"] = 51;                ["num3"] = 99;
		["4"] = 52;                ["num4"] = 100;
		["5"] = 53;                ["num5"] = 101;
		["6"] = 54;                ["num6"] = 102;
		["7"] = 55;                ["num7"] = 103;
		["8"] = 56;                ["num8"] = 104;
		["9"] = 57;                ["num9"] = 105;
		["a"] = 65;
		["b"] = 66;                ["num*"] = 106;
		["c"] = 67;                ["num+"] = 107;
		["d"] = 68;                ["num-"] = 109;
		["e"] = 69;                ["num."] = 110;
		["f"] = 70;                ["num/"] = 111;
		["g"] = 71;
		["h"] = 72;                ["f1"]  = 112;
		["i"] = 73;                ["f2"]  = 113;
		["j"] = 74;                ["f3"]  = 114;
		["k"] = 75;                ["f4"]  = 115;
		["l"] = 76;                ["f5"]  = 116;
		["m"] = 77;                ["f6"]  = 117;
		["n"] = 78;                ["f7"]  = 118;
		["o"] = 79;                ["f8"]  = 119;
		["p"] = 80;                ["f9"]  = 120;
		["q"] = 81;                ["f10"] = 121;
		["r"] = 82;                ["f11"] = 122;
		["s"] = 83;                ["f12"] = 123;
		["t"] = 84;
		["u"] = 85;                ["`"] = 192;
		["v"] = 86;                ["-"] = 189;
		["w"] = 87;                ["="] = 187;
		["x"] = 88;
		["y"] = 89;
		["z"] = 90;

		["{"] = 219;    ["lshift"]  = 160;
		["}"] = 221;    ["rshift"] = 161;
		["\\"] = 226;    ["lctrl"] = 162;
		["|"] = 226;		["rctrl"] = 163;
		
		[";"] = 186;      ["lalt"] = 164;
		["'"] = 222;      ["ralt"]= 165;
		
													["lsys"]     = 91;
		[","] = 188;          ["rsys"]    = 92;
		["."] = 190;
		["/"] = 191;
	}

local keymap_GII={
	["alt"] = 205 ;
	["pause"] = 178 ;
	["menu"] = 255 ;
	[","] = 44 ;
	["0"] = 48 ;
	["4"] = 52 ;
	["8"] = 56 ;
	["sysreq"] = 180 ;
	["@"] = 64 ;
	["return"] = 174 ;
	["7"] = 55 ;
	["\\"] = 92 ;
	["insert"] = 176 ;
	["d"] = 68 ;
	["h"] = 72 ;
	["l"] = 76 ;
	["p"] = 80 ;
	["t"] = 84 ;
	["x"] = 88 ;
	["right"] = 190 ;
	["meta"] = 204 ;
	["escape"] = 170 ;
	["home"] = 186 ;
	["'"] = 96 ;
	["space"] = 32 ;
	["3"] = 51 ;
	["backspace"] = 173 ;
	["pagedown"] = 193 ;
	["slash"] = 47 ;
	[";"] = 59 ;
	["scrolllock"] = 208 ;
	["["] = 91 ;
	["c"] = 67 ;
	["z"] = 90 ;
	["g"] = 71 ;
	["shift"] = 202 ;
	["k"] = 75 ;
	["o"] = 79 ;
	["s"] = 83 ;
	["w"] = 87 ;
	["delete"] = 177 ;
	["down"] = 191 ;
	["."] = 46 ;
	["2"] = 50 ;
	["6"] = 54 ;
	[":"] = 58 ;
	["b"] = 66 ;
	["f"] = 70 ;
	["j"] = 74 ;
	["pageup"] = 192 ;
	["up"] = 189 ;
	["n"] = 78 ;
	["r"] = 82 ;
	["v"] = 86 ;
	["f12"] = 229 ;
	["f13"] = 230 ;
	["f10"] = 227 ;
	["f11"] = 228 ;
	["f14"] = 231 ;
	["f15"] = 232 ;
	["ctrl"] = 203 ;
	["f1"] = 218 ;
	["f2"] = 219 ;
	["f3"] = 220 ;
	["f4"] = 221 ;
	["f5"] = 222 ;
	["f6"] = 223 ;
	["f7"] = 224 ;
	["f8"] = 225 ;
	["f9"] = 226 ;
	["tab"] = 171 ;
	["numlock"] = 207 ;
	["end"] = 187 ;
	["-"] = 45 ;
	["1"] = 49 ;
	["5"] = 53 ;
	["9"] = 57 ;
	["="] = 61 ;
	["]"] = 93 ;
	["a"] = 65 ;
	["e"] = 69 ;
	["i"] = 73 ;
	["m"] = 77 ;
	["q"] = 81 ;
	["u"] = 85 ;
	["y"] = 89 ;
	["left"] = 188 ;
}


local keymap_GLUT={
	-- ['f1']=	1 ;
	-- ['f2']=	2 ;
	-- ['f3']=	3 ;
	-- ['f4']=	4 ;
	-- ['f5']=	5 ;
	-- ['f6']=	6 ;
	-- ['f7']=	7 ;
	['delete']=	8 ;
	['tab']=	9 ;
	-- ['f10']=	10 ;
	-- ['f11']=	11 ;
	-- ['f12']=	12 ;
	['escape']=	27 ;
	['space']=	32 ;
	['enter']=	13 ;
	--directional key
	['left']=	80 ;
	['up']=	82 ;
	['right']=	79 ;
	['down']=	81 ;
	-- ['pageup']=104 ;
	-- ['pagedown']=105 ;
	-- ['home']=	106 ;
	-- ['end']=	107 ;
	-- ['insert']=	108 ;

}

--TODO: fix this
for i=39, 64 do
	keymap_GLUT[ string.char(i) ]=i
end

for i=91, 120 do
	keymap_GLUT[ string.char(i) ]=i
end

function getKeyMap()
	local configuration=MOAIInputMgr.configuration or 'AKUGlut'
	_stat( 'using input configuration:', configuration )
	if configuration=='AKUGlut' then
		return keymap_GLUT
	elseif configuration=='GII' then
		return keymap_GII
	else
		return keymap_GLUT
	end
end

