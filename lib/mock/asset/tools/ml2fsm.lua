#!/usr/local/bin/lua

local input, output=...
if not input or not output then
	print(string.format('usage: ml2fsm.lua <input_file.graphml> <output_file.lua>'))
	return
end

require 'lxp'

local match = string.match
function string.trim(s)
	return match(s,'^()%s*$') and '' or match(s,'^%s*(.*%S)')
end

local function convertGraphML(fn)
	local callbacks={}
	
	local objects={}

	local root={value='nodes',type='group'}
	local edges={}

	local nodeStack={}
	local pointer=0
	local currentNode
	local prevNode

	local groupSep='.'
	local actionSep=':'

	local function getFullName(n)
		local res=n.value or ''
		while true do
			local p=n.parent
			if not p or p==root then return res end
			res=p.value..groupSep..res
			n=p
		end
	end

	local function pushNode(n)
		pointer=pointer+1
		nodeStack[pointer]=n
		
		local parent=currentNode or root
		local children=parent.children
		if not children then children={} parent.children=children end
		children[n]=true
		n.parent=parent

		currentNode=n
	end

	local function popNode()
		if pointer>0 then
			pointer=pointer-1
			currentNode=nodeStack[pointer]
		else
			currentNode=nil
		end
	end

	local currentGroup
	
	local function getObject(id)
		local o=objects[id]
		if not o then o={id=id} objects[id]=o end
		return o
	end

	local function CharacterData(parser,string)
		if not currentNode.value then currentNode.value=string:trim() end
	end

	function callbacks.StartElement(parser,name,attrs)
		callbacks.CharacterData=false
		if name=='edge' then			
			local n={
				type='edge',
				id=attrs.id,
				from=getObject(attrs.source),
				to=getObject(attrs.target),
			}
			edges[attrs.id]=n
			pushNode(n)
		elseif name=='node' then
			local n=getObject(attrs.id)
			n.jump={}
			if attrs['yfiles.foldertype']=='group' then
				n.type='group'
			else
				n.type='state'
			end
			pushNode(n)
		elseif name=='y:EdgeLabel' or name=='y:NodeLabel' then
			if currentNode and not currentNode.value then
				callbacks.CharacterData=CharacterData
			end
		end
	end

	function callbacks.EndElement(parser,name)
		if name=='node' then
			-- callbacks.CharacterData=false			
			currentNode.fullname=getFullName(currentNode)
			currentNode.funcname='_FSM_'..string.gsub(currentNode.fullname,'%.','_')
			popNode()
		-- elseif name=='y:EdgeLabel' or name=='y:NodeLabel' then
		-- 	callbacks.CharacterData=false
		end
	end

	callbacks.CharacterData=false

	local file=io.open(fn,'r')
	if not file then 
		print("file not found:",fn)
		os.exit(1)		
	end	

	local p=lxp.new(callbacks)

	for line in file:lines() do
		p:parse(line)
	end

	file:close()


	local function findchild(group,name)
		local children=group.children
		if not children then return nil end
		for c in pairs(children) do
			if c.value==name then return c end
		end
		return nil
	end
	-----------------------------
	--generate jump table
	for i,e in pairs(edges) do
		local from=e.from
		local to=e.to
		local msg=e.value

		local jump=from.jump
		local isGroup=false
		if to.type=='group' then
			isGroup=true
			local startState=findchild(to,'start')
			if startState then
				to=startState
			else
				print("no 'start' state for group:",to.fullname)
				return error()
			end
		end

		if msg and msg~='' then
			jump[msg]=to
		else
			--validate group
			if from.type=='group' then
				local stopState=findchild(from,'stop')
				if stopState then
					from=stopState					
				else
					print("no 'stop' state for group:",from.fullname)
					return error()
				end
			end
			
			local __next=from.__next
			if not __next then
				__next={}
				from.__next=__next
			end
			__next[to]=isGroup and 'group' or 'node'
		end

	end

	local function generateJumpTarget( from, to )
		if from.parent == to.parent then
			return string.format( '%q', to.fullname )
		end
		local exits  = ""
		local enters = ""
		local node = from.parent
		while true do --find group crossing path
			local found = false
			enters = ""
			local node1 = to.parent
			while node1 ~= root do
				if node1 == node then	found = true break end
				enters = string.format( '%q,', node1.funcname .. '__jumpin' ) .. enters
				node1 = node1.parent				
			end
			if found then
				break
			end
			if node == root then break end
			exits = exits .. string.format( '%q,', node.funcname .. '__jumpout' )
			node = node.parent	
		end
		local output = exits .. enters
		--format: [ list of func needed to be called ] .. 'next state name'
		return string.format( "{ %s%q }", output, to.fullname)		
	end

	--overwrite according to parent-level-priority
	local function updateJump(node,src)
		if not node or node==root then return end
		if src then
			local jump0=src.jump
			local jump=node.jump
			for msg,target in pairs(jump) do
				jump0[msg]=target
			end
		else
			src=node
		end
		return updateJump(node.parent,src)
	end

	for i,o in pairs(objects) do
		updateJump(o)
	end

	local output=''
	local function writef(...)
		output=output..(string.format(...))
	end

	local function write(a)
		output=output..a
	end

	--data code(jumptable) generation
	-- file=io.open(fnout,'w')
	-- if not file then 
	-- 	print("cannot open file to write")
	-- 	os.exit(1)
	-- end
	write('(function()\n')
	write('local nodelist={')
	write('\n')
	for id,n in pairs(objects) do		
		writef(string.format('[%q]={name=%q,localName=%q,id=%q,type=%q};',n.fullname,n.fullname,n.value,n.funcname,n.type))
		write('\n')
	end
	write('};')
	write('\n')


	for id,n in pairs(objects) do
		write('-----------\n')
		if n.jump and next(n.jump) then
			writef('nodelist[%q].jump={\n',n.fullname)
			for msg, target in pairs(n.jump) do
				local jumpto = target.fullname
				writef( '\t[%q]=%s;\n', msg, generateJumpTarget( n, target ) )
			end
			write('}\n')
		else
			writef('nodelist[%q].jump=false\n',n.fullname)
		end

		if n.__next then
			writef('nodelist[%q].next={\n', n.fullname )
			local count=0
			for target,targetType in pairs(n.__next) do
			-- local target=n.__next
				local jumpto=target.fullname
				local targetName=target.value
				--add a symbol for better distinction
				if targetType=='group' then targetName=target.parent.value end
				writef('["$%s"]=%s;\n',targetName, generateJumpTarget( n, target ) ) 
				count=count+1
			end
			
			if count==1 then --only one, give it a 'true' transition
				local target=next(n.__next)
				local jumpto=target.fullname
				writef('[true]=%s;\n', generateJumpTarget( n, target ) )
			end

			writef('}\n')
		end
	end

	write('return nodelist\n')
	write('end) ()\n')

	write('\n')

	return output
end

-- local result=parseXMLFile(input,output)
-- if result then
-- 	print('done!')
-- else
-- 	print('failed')
-- end


local function stripExt(p)
		 p=string.gsub(p,'%..*$','')
		 return p
end

local function extractExt(p)
	return string.gsub(p,'.*%.','')
end


function convertSingle( input, output )
	local result = convertGraphML( input )
	local outfile=io.open(output,'w')
	outfile:write( 'return ')
	outfile:write( result )
	outfile:close()	
	return true
end

convertSingle( input, output )
-- local lfs = require"lfs"

-- local function convertAll (path,output)
-- 	local outfile=io.open(output,'w')
-- 	outfile:write('return {\n')

-- 	for filename in lfs.dir(path) do
-- 		local ext=extractExt(filename)
-- 		if ext=='graphml' then
-- 			local f = path..'/'..filename
-- 			local name=stripExt(filename)
-- 			print ("\t "..f)
-- 			local attr = lfs.attributes (f)
-- 			assert (type(attr) == "table")
-- 			if attr.mode ~= "directory" then
-- 				outfile:write(string.format('[%q]=',name))
-- 				local result=convertGraphML(f)
-- 				outfile:write(result)
-- 				outfile:write(';\n')
-- 			end
-- 		end
-- 	end

-- 	outfile:write('}\n')
-- 	outfile:close()
-- end


-- convertAll(input,output)

	--direct code generation
	-- file=io.open('fsmcode.lua','w')

	
	-- local function buildState(n)
	-- 	writef('function %s(self)\n',n.funcname)
	-- 		--step
	-- 		local stepFuncName=n.funcname..'_step'
	-- 		writef('local flag\n')
	-- 		writef('if self.%s then flag=self:%s() end\n', stepFuncName, stepFuncName)
	-- 		--msg loop
	-- 		writef('while true do')
	-- 		writef('local msg=self:pollMsg()')
	-- 		writef('if not msg then break end')
	-- 		writef('end')

	-- 	write('end\n\n')
	-- end

	-- for id,node in pairs(objects) do
	-- 	writef('local %s\n',node.funcname)
	-- end

	-- for id,node in pairs(objects) do
	-- 	buildState(node)
	-- end

	-- file:close()

-----------------------------
	-- --data code generation
	-- file=io.open('output.lua','w')
	-- file:write('local function FSMDATA()\n')


	-- local function writeNode(n,prefix)
	-- 	if n.children then
	-- 		file:write(prefix)
	-- 		file:write(string.format('%s={\n',n.value or "??"))
	-- 		for c in pairs(n.children) do
	-- 			if c.type~='edge' then	writeNode(c,prefix..'\t') end
	-- 		end
	-- 		file:write(prefix)
	-- 		file:write('};\n')
	-- 	else
	-- 		file:write(prefix)
	-- 		file:write(string.format('%s={};\n',n.value))
	-- 	end
	-- end
	-- file:write('local ')
	-- writeNode(root,'')

	-- file:write('local transitions={')
	-- file:write('\n')
	-- for id, e in pairs(edges) do
	-- 	local msg=e.value
	-- 	if msg then msg=msg:trim() end
	-- 	if (not msg) or msg=='' then
	-- 		file:write(string.format('{from=nodes.%s,to=nodes.%s};',e.from.fullname,e.to.fullname))
	-- 		file:write('\n')
	-- 	else
	-- 		file:write(string.format('{from=nodes.%s,to=nodes.%s,msg=%q};',e.from.fullname,e.to.fullname,msg))
	-- 		file:write('\n')
	-- 	end
	-- end
	-- file:write('};')
	-- file:write('\n')

	-- file:write('local nodelist={')
	-- file:write('\n')
	-- for id,n in pairs(objects) do		
	-- 	file:write(string.format('[%q]=nodes.%s;',n.fullname, n.fullname))
	-- 	file:write('\n')
	-- end
	-- file:write('};')
	-- file:write('\n')

	-- file:write('return {list=nodelist, tree=nodes, transitions=transitions}\n')
	-- file:write('end')--end of func
	-- file:write('\n')

	-- file:write('return FSMDATA()')--end of package
	-- file:write('\n')
