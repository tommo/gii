from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QVariant
from qtpropertybrowser import *
##----------------------------------------------------------------##
from gii.core.model import *
##----------------------------------------------------------------##
PyTypeToPropertyType={
		int          : QVariant. Int,
		float        : QVariant. Double,
		str          : QVariant. String,
		unicode      : QVariant. String,
		bool         : QVariant. Bool,
		QtGui.QColor : QVariant. Color,
	}

MaxPropertyTypeId=1000
CustomPropertyManagerRegistry={
}

##----------------------------------------------------------------##
def registerCustomPropertyManager( typeobj, managerClas ):
	global MaxPropertyTypeId
	assert not PyTypeToPropertyType.has_key( typeobj ), 'property type already registered'
	id = MaxPropertyTypeId
	MaxPropertyTypeId += 1
	PyTypeToPropertyType[ typeobj ] = id
	CustomPropertyManagerRegistry[ id ] = managerClas	

##----------------------------------------------------------------##
class CustomPropertyManager(object):
	"""docstring for CustomPropertyManager"""
	def __init__(self, parent):
		self.propToData          = {}
		self.subProperties       = {}
		self.subPropertieToProp  = {}
		self.watchingValueChange = False
		self.parent = parent

	def clear(self):
		self.propToData.clear()
		self.subProperties.clear()
		self.subPropertieToProp.clear()

	def defaultValue(self):
		return False

	def valueText(self, prop):
		return repr(self.value(prop))

	def value(self, prop):
		return self.propToData.get(prop)

	def setValue(self, prop, value):
		self.propToData[prop]=value

	def initializeProperty(self, prop, parent=None):
		self.propToData[prop]=self.defaultValue()

	def uninitializeProperty(self, prop):
		if self.propToData.has_key( prop ):
			del self.propToData[prop]

	def addSubProperty(self, prop, typeobj, label, value=None):
		ptype = PyTypeToPropertyType.get( typeobj,None )
		if ptype:
			sub = self.parent.addProperty(ptype, label)
			if sub:
				subs=self.subProperties.get(prop,None)
				if not subs:
					subs={}
					self.subProperties[prop]=subs
				subs[label]=sub
				self.subPropertieToProp[sub]=prop
				prop.addSubProperty(sub)
				if not self.watchingValueChange:
					self.watchingValueChange=True
					self.parent.valueChanged.connect(self.onValueChanged)
				return sub
		return None

	def setSubValue(self, prop, label, value):
		subs=self.subProperties.get(prop,None)
		if subs:
			subProp = subs.get(label, None)
			if subProp:
				subProp.setValue(value)

	def onValueChanged(self, prop, value):
		parent = self.subPropertieToProp.get(prop)
		if parent:
			if self.onSubValueChanged(parent, prop ,value): #update?
				self.parent.propertyChanged.emit(parent)
				self.parent.valueChanged.emit(parent, parent.value())

	def onSubValueChanged(self, prop, subProp, value):
		return False


##----------------------------------------------------------------##
class PropertyManager(QtVariantPropertyManager):
	def __init__(self):
		super(PropertyManager, self).__init__()		
		self.customManagers={}

	def clear(self):
		for k in self.customManagers:
			self.customManagers[k].clear()
		QtVariantPropertyManager.clear(self)

	def getCustomPropertyManager(self, prop):
		propTypeId = self.propertyType(prop)
		mgr        = self.customManagers.get(propTypeId)
		if mgr:
			return mgr
		clas = CustomPropertyManagerRegistry.get(propTypeId,None)
		if clas:
			mgr = clas(self)
			self.customManagers[propTypeId]=mgr
			return mgr
		return None

	def isPropertyTypeSupported(self, typeId):
		if QtVariantPropertyManager.isPropertyTypeSupported(self,typeId): return True
		return CustomPropertyManagerRegistry.has_key(typeId)

	def postInitializeProperty(self, prop):
		customManager = self.getCustomPropertyManager(prop)
		if customManager:
			customManager.initializeProperty(prop)

	def uninitializeProperty(self, prop):
		customManager = self.getCustomPropertyManager(prop)
		if customManager:
			customManager.uninitializeProperty(prop)
		return QtVariantPropertyManager.uninitializeProperty(self, prop)

	def valueText(self, prop):
		customManager = self.getCustomPropertyManager(prop)
		if customManager:
			return customManager.valueText(prop)		
		return QtVariantPropertyManager.valueText(self, prop)

	def value(self, prop):
		customManager = self.getCustomPropertyManager(prop)
		if customManager:
			return customManager.value(prop)
		return QtVariantPropertyManager.value(self, prop)

	def setValue(self, prop, value):
		customManager = self.getCustomPropertyManager(prop)
		if customManager:
			customManager.setValue(prop, value)
			self.propertyChanged.emit(prop)
			self.valueChanged.emit(prop, value)
			return
		return QtVariantPropertyManager.setValue(self, prop, value)
		


##----------------------------------------------------------------##
class EditorFactory(QtVariantEditorFactory):
	def createEditor( self, prop, parent=None ):
		if prop.readonly:
			return True
		manager = self.propertyManager( prop )
		return QtVariantEditorFactory.createEditor(self, manager, prop, parent)
		

##----------------------------------------------------------------##
class TreePropertyBrowser(QtTreePropertyBrowser):
	def createEditor(self, prop, parent=None):
		editor=QtTreePropertyBrowser.createEditor(self, prop,parent)
		if editor:
			editor.destroyed.connect(self.onEditorDestroyed)
		return editor

	def onEditorDestroyed(self):
		self.update()

##----------------------------------------------------------------##

##----------------------------------------------------------------##
class PropertyGrid(QtGui.QWidget):
	propertyChanged = QtCore.pyqtSignal( object, str, object )

	def __init__(self, parentWidget, **option):
		super(PropertyGrid, self).__init__(parentWidget)
		self.model= None
		self.target= None
		
		self.manager= manager =PropertyManager()
		self.factory= factory =EditorFactory()
		self.browser= browser =TreePropertyBrowser(self)

		self.option=option or {}

		self.refreshing = False
		
		browser.setFactoryForManager(manager, factory)
		browser.setPropertiesWithoutValueMarked(True)
		browser.setAlternatingRowColors(False)
		browser.setHeaderVisible( option.get('header', True) )
		# browser.setRootIsDecorated(False)

		#TODO: build
		self.propMap={}
		
		#setup layout		
		self.layout=QtGui.QVBoxLayout(self)
		self.layout.setSpacing(0)
		self.layout.setMargin(0)

		self.layout.addWidget(browser)
		
		manager.propertyChanged.connect(self.onPropertyChanged)

	def clear(self):
		self.browser.clear()
		self.manager.clear()
		self.propMap.clear()
		self.target=None


	def setTarget(self, target, **kwargs ):
		if target==self.target:
			return
		self.clear()
		model = kwargs.get( 'model', None )
		if not model: model = ModelManager.get().getModel(target)
		if not model: 
			return

		self.model = model
		self.target = target

		assert(model)
		readonlyColor = QtGui.QColor('#ff0000')
		readonlyColor.setAlphaF(0.05)
		
		#install field info
		for field in model.fieldList:
			label = field.label
			ft    = field._type
			prop  = None
			if isinstance( ft, EnumType ):
				prop = self.manager.addProperty( QtVariantPropertyManager.enumTypeId(), label )
				enumNames = [ x[0] for x in ft.itemList ]
				prop.setAttribute( 'enumNames', enumNames )
				prop.enumType = ft 
			else:
				ptype = PyTypeToPropertyType.get( ft, None )
				if not ptype: #not supported, skip
					continue
				prop = self.manager.addProperty( ptype, label )

			if prop:
				prop.readonly = field.readonly
				self.browser.addProperty( prop )
				# self.rootProp.addSubProperty(prop)
				self.manager.postInitializeProperty(prop)
				fieldId = field.id
				self.propMap[fieldId] = prop #use fullname e.g: f1.subf1
				prop.fieldId = fieldId				
				#setup item
				items = self.browser.items(prop)
				item  = items and items[0] or None
				if item:				
					self.browser.setExpanded(item, False)
					if field.readonly:
						self.browser.setBackgroundColor(item, readonlyColor)
					# 	prop.setEnabled(False)
		#end of refresh
		self.refreshAll()

	def onPropertyChanged(self, prop):
		if self.refreshing: return  #pulling from target, don't update target
		if hasattr( prop, 'fieldId' ):
			v = prop.value()
			if hasattr( prop, 'enumType' ):
				v = prop.enumType.fromIndex( v )
			self.model.setFieldValue( self.target, prop.fieldId, v )
			self.propertyChanged.emit( self.target, prop.fieldId, v )

	def refreshField( self, id ):
		target = self.target
		if not target: return
		prop = self.propMap.get( id, None ) 
		if prop:
			v = self.model.getFieldValue( target, id )
			self.refreshing = True #avoid duplicated update
			prop.setValue(v)
			self.refreshing = False

	def refreshAll(self):
		target=self.target
		if not target: return
		for field in self.model.fieldList: #todo: just use propMap to iter?
			self.refreshField( field.id )

