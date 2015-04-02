import xml.etree.ElementTree as ET
def convertGraphML(fn):
	callbacks={}
	objects={}
	root={value='nodes',type='group'}
	edges={}
	nodeStack={}
	pointer=0
	currentNode
	prevNode
	groupSep='.'
	actionSep=':'
	def getFullName(n):
		res=n.value or ''
		while true do
			p=n.parent
			if not p or p==root then return res 
			res=p.value+groupSep+res
			n=p
	def pushNode(n):
		pointer=pointer+1
		nodeStack[pointer]=n
		
		parent=currentNode or root
		children=parent.children
		if not children then children={} parent.children=children 
		children[n]=true
		n.parent=parent
		currentNode=n
	
	def popNode():
		if pointer>0 then
			pointer=pointer-1
			currentNode=nodeStack[pointer]
		else
			currentNode=nil
		
	
	currentGroup
	
	def getObject(id):
		o=objects[id]
		if not o then o={id=id} objects[id]=o 
		return o
	
	def CharacterData(parser,string):
		if not currentNode.value then currentNode.value=string:trim() 
	
	def callbacks.StartElement(parser,name,attrs):
		callbacks.CharacterData=false
		if name=='edge' then			
			n={
				type='edge',
				id=attrs.id,
				from=getObject(attrs.source),
				to=getObject(attrs.target),
			}
			edges[attrs.id]=n
			pushNode(n)
		elseif name=='node' then
			n=getObject(attrs.id)
			n.jump={}
			if attrs['yfiles.foldertype']=='group' then
				n.type='group'
			else
				n.type='state'
			
			pushNode(n)
		elseif name=='y:EdgeLabel' or name=='y:NodeLabel' then
			if currentNode and not currentNode.value then
				callbacks.CharacterData=CharacterData
			
		
	
	def callbacks.EndElement(parser,name):
		if name=='node' then
			# callbacks.CharacterData=false			
			currentNode.fullname=getFullName(currentNode)
			currentNode.funcname='_FSM_'+string.gsub(currentNode.fullname,'%.','_')
			popNode()
		# elseif name=='y:EdgeLabel' or name=='y:NodeLabel' then
		# 	callbacks.CharacterData=false
		
	
	callbacks.CharacterData=false
	file=io.open(fn,'r')
	if not file then 
		print("file not found:",fn)
		os.exit(1)		
		
	p=lxp.new(callbacks)
	for line in file:lines() do
		p:parse(line)
	
	file:close()

	def findchild(group,name):
		children=group.children
		if not children then return nil 
		for c in pairs(children) do
			if c.value==name then return c 
		
		return nil
	
	##############-
	#generate jump table
	for i,e in pairs(edges) do
		from=e.from
		to=e.to
		msg=e.value
		jump=from.jump
		isGroup=false
		if to.type=='group' then
			isGroup=true
			startState=findchild(to,'start')
			if startState then
				to=startState
			else
				print("no 'start' state for group:",to.fullname)
				return error()
			
		
		if msg and msg~='' then
			jump[msg]=to
		else
			#validate group
			if from.type=='group' then
				stopState=findchild(from,'stop')
				if stopState then
					from=stopState					
				else
					print("no 'stop' state for group:",from.fullname)
					return error()
				
			
			
			__next=from.__next
			if not __next then
				__next={}
				from.__next=__next
			
			__next[to]=isGroup and 'group' or 'node'
		
	
	def generateJumpTarget( from, to ):
		if from.parent == to.parent then
			return string.format( '%q', to.fullname )
		
		exits  = ""
		enters = ""
		node = from.parent
		while true do #find group crossing path
			found = false
			enters = ""
			node1 = to.parent
			while node1 ~= root do
				if node1 == node then	found = true break 
				enters = string.format( '%q,', node1.funcname + '__jumpin' ) + enters
				node1 = node1.parent				
			
			if found then
				break
			
			if node == root then break 
			exits = exits + string.format( '%q,', node.funcname + '__jumpout' )
			node = node.parent	
		
		output = exits + enters
		#format: [ list of func needed to be called ] + 'next state name'
		return string.format( "{ %s%q }", output, to.fullname)		
	
	#overwrite according to parent-level-priority
	def updateJump(node,src):
		if not node or node==root then return 
		if src then
			jump0=src.jump
			jump=node.jump
			for msg,target in pairs(jump) do
				jump0[msg]=target
			
		else
			src=node
		
		return updateJump(node.parent,src)
	
	for i,o in pairs(objects) do
		updateJump(o)
	
	output=''
	def writef( pattern, *args ):
		output=output+( pattern % args )
	
	def write(a):
		output=output+a
	
	#data code(jumptable) generation
	# file=io.open(fnout,'w')
	# if not file then 
	# 	print("cannot open file to write")
	# 	os.exit(1)
	# 
	write('(def()\n'):
	write('nodelist={')
	write('\n')
	for id,n in pairs(objects) do		
		writef(string.format('[%q]={name=%q,localName=%q,id=%q,type=%q};',n.fullname,n.fullname,n.value,n.funcname,n.type))
		write('\n')
	
	write('};')
	write('\n')

	for id,n in pairs(objects) do
		write('#####-\n')
		if n.jump and next(n.jump) then
			writef('nodelist[%q].jump={\n',n.fullname)
			for msg, target in pairs(n.jump) do
				jumpto = target.fullname
				writef( '\t[%q]=%s;\n', msg, generateJumpTarget( n, target ) )
			
			write('}\n')
		else
			writef('nodelist[%q].jump=false\n',n.fullname)
		
		if n.__next then
			writef('nodelist[%q].next={\n', n.fullname )
			count=0
			for target,targetType in pairs(n.__next) do
			# target=n.__next
				jumpto=target.fullname
				targetName=target.value
				#add a symbol for better distinction
				if targetType=='group' then targetName=target.parent.value 
				writef('["$%s"]=%s;\n',targetName, generateJumpTarget( n, target ) ) 
				count=count+1
			
			
			if count==1 then #only one, give it a 'true' transition
				target=next(n.__next)
				jumpto=target.fullname
				writef('[true]=%s;\n', generateJumpTarget( n, target ) )
			
			writef('}\n')
		
	
	write('return nodelist\n')
	write(') ()\n')
	write('\n')
	return output

def stripExt(p):
		 p=string.gsub(p,'%+*$','')
		 return p

def extractExt(p):
	return string.gsub(p,'.*%.','')

def convertSingle( input, output ):
	result = convertGraphML( input )
	outfile=io.open(output,'w')
	outfile:write( 'return ')
	outfile:write( result )
	outfile:close()	
	return true

convertSingle( input, output )

tree = ET.parse('Hero.fsm.graphml')
root = tree.getroot()
