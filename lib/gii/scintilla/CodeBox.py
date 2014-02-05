import json
import os

from PyQt4      import QtGui, QtCore, Qsci
from PyQt4.Qsci import QsciScintilla as Sci

from gii.core   import app
from compat     import ScintillaCompat

MARGIN_LINENR = 0
MARGIN_BREAKPOINT = 1
MARGIN_FOLDING = 2
MARGIN_DIVIDER = 3

MARKER_BREAKPOINT = 1
MARKER_HILIGHT_NORMAL = 2
MARKER_HILIGHT_SERIOUS = 3

LUA_KEYWORDS=[
		{
			'id' : 0,
			'keywords' : "function end do for in local return then if else elseif while loop repeat until or and not",
			'name' : "Instruction",
		},
		{
			'id': 1,
			'keywords': "table string math pairs ipairs next select pack unpack setmetatable getmetatable\rgii class",
			'name': "Func1",
		}
	]

def convertColor(c, alpha=1):
	if isinstance(c, dict):
		return QtGui.QColor(c.get('r',1)*255,c.get('g',1)*255,c.get('b',1)*255, c.get('a',alpha)*255)
	else:
		return QtGui.QColor(c)

	
class CodeBox(ScintillaCompat, Qsci.QsciScintilla):
	"""docstring for CodeBox"""
	def __init__(self, arg):
		super(CodeBox, self).__init__(arg)		
		self.currentHilight=False
		# self.Bind(Sci.EVT_SCI_MODIFIED, self.onModified)
		# self.Bind(Sci.EVT_SCI_CHANGE, self.onChange)
		# self.Bind(Sci.EVT_SCI_CHARADDED, self.onCharAdded)
		# self.Bind(Sci.EVT_SCI_ZOOM, self.onZoom)
		# self.Bind(Sci.EVT_SCI_MARGINCLICK, self.onMarginClick)
		# self.Bind(Sci.EVT_SCI_KEY, self.onKey)
		# self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
		# self.Bind(Sci.EVT_SCI_UPDATEUI, self.onUpdateUI)
		# if wx.Platform == '__WXMAC__':
		# 	self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
		self.setUtf8(True)
		self.refreshing=False
		self.path=''


	def refreshCode(self):
		self.refreshing=True
		code='Not Load'
		with file(self.path,'r') as f:
			code=f.read()
			self.fileTime=os.path.getmtime(self.path)
		try:
			code=code.decode('utf-8')
		except Exception, e:
			pass
		readOnly=self.isReadOnly()
		self.setReadOnly(False)

		self.setText(code)

		self.setReadOnly(readOnly)
		# self.SetSavePoint()
		# self.EmptyUndoBuffer()

		self.refreshing=False

		#self.checkModifyState()

	def checkFileModified(self):
		newtime=os.path.getmtime(self.path)
		if newtime>self.fileTime:
			self.refreshCode()
	
	def locateLine(self, linenumber, hilight=False):
		self.setFocus()
		if linenumber > 0:
			self.gotoLine(linenumber)
			self.currentHilight=hilight
			if hilight=='normal':
				self.markerDeleteAll( MARKER_HILIGHT_NORMAL)
				self.markerAdd(linenumber, MARKER_HILIGHT_NORMAL)
			elif hilight=='serious':
				self.markerDeleteAll( MARKER_HILIGHT_SERIOUS)
				self.markerAdd(linenumber, MARKER_HILIGHT_SERIOUS)
			else:
				pass

	def toggleBreakPoint(self, line):
		#'self.MarkerGet(line) & MARKER_BREAKPOINT
		hasBreakpoint=self.MarkerGet(line, MARKER_BREAKPOINT)
		if hasBreakpoint:
			self.markerDelete(line, MARKER_BREAKPOINT)
		else:
			self.markerAdd(line, MARKER_BREAKPOINT)

	def clearBreakPoints(self):
		self.markerDeleteAll(MARKER_BREAKPOINT)

	def applySetting(self, setting):
		if not setting: setting={}
		defaultMargin=15
		
		self.setLexer(Qsci.QsciLexerLua(self))		
		styles=setting.get('styles',[])

		styleLineNumber={
			'id':Sci.STYLE_LINENUMBER,
			'font':'Consolas',
			'fg':'BLACK',
			'bg':'GRAY',
			'size':9
		}

		self.applyStyle(styleLineNumber)		
		# self.StyleSetForeground(Sci.STYLE_INDENTGUIDE, convertColor(setting.indentGuideColor))
		styleIndentGuide={
			'id':Sci.STYLE_INDENTGUIDE,
			'fg':'GRAY',
			'bg':'WHITE',
		}
		self.applyStyle(styleIndentGuide)		
		
		# 'common settings

		# ' Default font For all styles
		# SetViewEOL(setting.displayEOLEnable)
		if setting.get('indent_guide.enabled',True):
			self._send(Sci.SCI_SETINDENTATIONGUIDES, Sci.SC_IV_LOOKFORWARD)
		
		if setting.get('line_number.enabled',True):
			# LineNrMargin = self.TextWidth(Sci.STYLE_LINENUMBER, "_99999")
			# self.fm = QtGui.QFontMetrics(self.font)
			LineNrMargin=30
			# self.setMarginType(MARGIN_LINENR, Sci.NumberMargin)
			self.setMarginLineNumbers(MARGIN_LINENR, True)
			self.setMarginWidth(MARGIN_LINENR, LineNrMargin)
		else:
			self.setMarginWidth(MARGIN_LINENR, 0)		
		
		if setting.get('edge_line.enabled',False):
			self.setEdgeMode (Sci.EdgeLine)
		else:
			self.setEdgeMode (Sci.EdgeNone)
		
		if setting.get('white_space.visible', False):
			self.setWhitespaceVisibility(Sci.WsVisible)
		else:
			self.setWhitespaceVisibility(Sci.WsInvisible)
		
		# # SetOvertype(setting.overTypeInitial)
		
		if setting.get('wrap_word',False):
			self.setWrapMode(Sci.WrapWord)
		else:
			self.setWrapMode(Sci.WrapNone)
		
		self.setProperty("fold", '1')
		self.setProperty("fold.compact", '0')
		self.setProperty("fold.comment", '1')
		self.setProperty("fold.preprocessor", '1')
		
		# self.SetStyleBits(5)

		self.setFolding(Sci.BoxedTreeFoldStyle)
		

		# # ' set margin as unused
		self.setMarginType (MARGIN_DIVIDER, Sci.SymbolMarginDefaultBackgroundColor)
		self.setMarginWidth (MARGIN_DIVIDER, 10)
		self.setMarginSensitivity (MARGIN_DIVIDER, False);

		# # ' set visibility
		# self.setVisiblePolicy(Sci.VISIBLE_STRICT | Sci.VISIBLE_SLOP, 1)
		# self.SetXCaretPolicy(Sci.SC_CARET_EVEN | Sci.SC_VISIBLE_STRICT | Sci.SC_CARET_SLOP, 1)
		# self.SetYCaretPolicy(Sci.SC_CARET_EVEN | Sci.SC_VISIBLE_STRICT | Sci.SC_CARET_SLOP, 1)
		
		# # ' caret
		self.setCaretLineVisible(setting.get('caret.visible',True))
		self.setCaretLineBackgroundColor(
			QtGui.QColor(0,0,0,20)
			# convertColor(setting.get('caretBackground',))
			)
		# self.setCaretLineBackAlpha(80)
		
		# # 'other style
		# self.SetSelAlpha(256)
		# self.SetSelBackground(1, wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
				
		# # 'folder marker
		# self.setMarginSensitivity(MARGIN_FOLDING, True)
		# self.setMarginType(MARGIN_FOLDING, Sci.SC_MARGIN_SYMBOL)
		# self.setMarginMarkerMask(MARGIN_FOLDING, Sci.SC_MASK_FOLDERS)
		self.setMarginWidth (MARGIN_FOLDING, setting.get('margin.folding',defaultMargin))
		
		# # 'breakpoint marker
		# self.setMarginMarkerMask(MARGIN_BREAKPOINT, 2)
		# self.setMarginSensitivity(MARGIN_BREAKPOINT, True)
		# self.setMarginType(MARGIN_BREAKPOINT, Sci.SC_MARGIN_SYMBOL)
		# self.setMarginWidth (MARGIN_BREAKPOINT, setting.get('margin.breaking',defaultMargin))
		
		# # # ' markers
		# self.markerDefine(Sci.SC_MARKNUM_FOLDER, Sci.SC_MARK_BOXPLUS)
		# self.markerSetBackground(Sci.SC_MARKNUM_FOLDER, "WHITE")
		# self.markerSetForeground(Sci.SC_MARKNUM_FOLDER, "BLACK")
		# self.markerDefine(Sci.SC_MARKNUM_FOLDEROPEN, Sci.SC_MARK_BOXMINUS)
		# self.markerSetBackground(Sci.SC_MARKNUM_FOLDEROPEN, "WHITE")
		# self.markerSetForeground(Sci.SC_MARKNUM_FOLDEROPEN, "BLACK")
		
		# self.markerDefine(Sci.SC_MARKNUM_FOLDERSUB, Sci.SC_MARK_EMPTY)
		# self.markerDefine(Sci.SC_MARKNUM_FOLDEREND, Sci.SC_MARK_SHORTARROW)
		# self.markerDefine(Sci.SC_MARKNUM_FOLDEROPENMID, Sci.SC_MARK_ARROWDOWN)
		# self.markerDefine(Sci.SC_MARKNUM_FOLDERMIDTAIL, Sci.SC_MARK_EMPTY)
		# self.markerDefine(Sci.SC_MARKNUM_FOLDERTAIL, Sci.SC_MARK_EMPTY)
		
		self.markerDefine(MARKER_BREAKPOINT, Sci.SC_MARK_CIRCLE)
		self.markerSetBackground(MARKER_BREAKPOINT, "RED")
		self.markerSetForeground(MARKER_BREAKPOINT, "BLACK")
		
		self.markerSetBackground(MARKER_HILIGHT_NORMAL, "YELLOW")
		self.markerSetForeground(MARKER_HILIGHT_NORMAL, "BLACK")
		
		self.markerDefine(MARKER_HILIGHT_SERIOUS, Sci.SC_MARK_SHORTARROW)
		self.markerSetBackground(MARKER_HILIGHT_SERIOUS, "RED")
		self.markerSetAlpha(MARKER_HILIGHT_SERIOUS, 20)
												
		# # ' miscelaneous
		self.setUsePopUp(True)
		
		self.setTabWidth(setting.get('tab.width',4))
		self.setIndentationWidth (0)
		self.setIndentationsUseTabs (True)
		self.setTabIndents (True)
		self.setBackspaceUnindents (True)
		
		self.setLayoutCache(Sci.SC_CACHE_PAGE)
		self.setBufferedDraw(True)
	
		# # 'apply language setting
		for s in styles:
			self.applyStyle(s)
		
		# for d in LUA_KEYWORDS:
			# self.SetKeyWords(d['id'], d['keywords'])
	def setKeywords(id, keywords):
		self._send(Sci.SCI_SETKEYWORDS, id, keywords)

	def applyStyle(self, style):
		lexer=self.lexer()
		id=style['id']

		lexer.setColor(
				convertColor(style.get('fg',{'r':0,'g':0,'b':0})), id
			)
		lexer.setPaper(
				convertColor(style.get('bg',{'r':1,'g':1,'b':1})), id
			)
		font=QtGui.QFont()
		font.setFamily(style.get('font','Consolas'))
		font.setPointSize(style.get('size',12))
		font.setBold(style.get('bold',False))
		font.setItalic(style.get('italic',False))
		font.setUnderline(style.get('underline',False))
		lexer.setFont(font, id)
		
	def onMouseWheel(self,event):
		if event.GetWheelAxis()==wx.MOUSE_WHEEL_HORIZONTAL:
			x0=self.GetXOffset()
			delta=event.GetWheelDelta() * 2
			rotation=event.GetWheelRotation()
			if rotation<0:
				self.SetXOffset(x0+delta)
			else:
				self.SetXOffset(max(x0-delta,0))
		else:
			event.Skip()

	def onMarginClick(self, event):
		pos=event.GetPosition()
		line=self.LineFromPosition(pos)
		margin=event.GetMargin()
		if margin == MARGIN_FOLDING:
			self.ToggleFold(line)
		# elif margin == MARGIN_LINENR:
		# 	self.SetSelection(self.PositionFromLine(line), self.PositionFromLineEnd(line))
		elif margin == MARGIN_BREAKPOINT:
			pass
		event.Skip()

	def mousePressEvent(self, event):
	 	Sci.mousePressEvent(self, event)
