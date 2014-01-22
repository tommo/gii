import os.path
import logging

from gii.core import AssetManager, AssetLibrary, getProjectPath, app, jsonHelper

import re
import xlrd

##----------------------------------------------------------------##
def cellValue( cell ):
	if cell.ctype == xlrd.XL_CELL_BOOLEAN:
		return cell.value == 1
	elif cell.ctype == xlrd.XL_CELL_EMPTY:
		return None
	else:
		return cell.value

def convertSheetToData( sheet ):
	name = sheet.name
	mo = re.match( '(\w+)@(\w+)', name )
	if not mo: return False
	sheetId  = mo.group(1)
	typeName = mo.group(2)
	if typeName == 'list':
		data = []
		cols = sheet.ncols
		rows = sheet.nrows
		if rows<2: return False
		keys = [ cell.value for cell in sheet.row( 0 ) ]
		for row in range( 1, rows ):
			rowData = {}
			for i, key in enumerate( keys ):
				if key:
					cell = sheet.cell( row, i )
					rowData[key] = cellValue( cell )
			data.append( rowData )
		return sheetId, data

	elif typeName == 'vlist':
		data = []
		cols = sheet.ncols
		rows = sheet.nrows
		if cols<2: return False
		keys = [ cell.value for cell in sheet.col( 0 ) ]
		for col in range( 1, cols ):
			colData = {}
			for i, key in enumerate( keys ):
				if key:
					cell = sheet.cell( i, col )
					colData[key] = cellValue( cell )
			data.append( colData )
		return sheetId, data

	elif typeName == 'dict':
		data = {}
		rows = sheet.nrows
		cols = sheet.ncols
		if cols<2:
			logging.warn( 'KV table columns must >= 2' )

		for row in range( 0, rows ):
			key = sheet.cell( row, 0 ).value
			if not key: continue
			value = sheet.cell( row, 1 ).value
			if data.has_key( key ):
				logging.warn( 'skip duplicated key: %s' % key.encode('utf-8') )
				continue
			data[ key ] = value
		return sheetId, data
		

def convertWorkbookToData( workbook ):
	bookData = {}
	for sheet in workbook.sheets():
		sheetData = convertSheetToData( sheet ) 
		if sheetData:
			( id, data )= sheetData
			if bookData.has_key( id ):
				logging.warn( 'skip duplicated sheet id: %s' % id.encode('utf-8') )
				continue
			bookData[ id ] = data
	return bookData

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class DataXLSAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.data_xls'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name, ext = os.path.splitext(filepath)
		if not ext in ['.xls']: return False
		return True

	def importAsset(self, node, reload = False ):
		#JOB: convert xls into json
		workbook = xlrd.open_workbook( node.getAbsFilePath() )
		if not workbook:
			logging.warn( 'excel version not supported for %s' % node.getFilePath() )
			return False

		data = convertWorkbookToData( workbook )
		if not data:
			logging.warn( 'no data converted from xls: %s' % node.getFilePath() )
			return False
		cachePath = node.getCacheFile( 'data' )
		
		if not jsonHelper.trySaveJSON( data, cachePath ):
			logging.warn( 'failed saving xls data: %s' % cachePath )
			return False

		node.assetType = 'data_xls'
		node.setObjectFile( 'data', cachePath )
		return True

DataXLSAssetManager().register()
AssetLibrary.get().setAssetIcon( 'data_xls', 'data' )

