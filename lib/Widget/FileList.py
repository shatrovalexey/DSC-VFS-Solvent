from lib.GUI import GUI, ttk
from lib.Widget.ChangePasswordDialog import ChangePasswordDialog
import tkinter.filedialog
from tkinter.messagebox import *
import tkinter as tk
import sys

class FileList( GUI ) :
	def prepare( self ) :
		GUI.prepare( self )

		self.controller = self.creator.creator.controller

		self.inputValue = tk.StringVar( )
		self.outputValue = tk.StringVar( )

		fileBox = ttk.Frame( self.master , relief = tk.SUNKEN )
		fileEntry = ttk.Entry( fileBox , textvariable = self.inputValue )

		# chpassButton = ttk.Button( fileBox , text = self.config[ "gui" ][ "change_password" ] , command = self.changePassword )
		purgeButton = ttk.Button( fileBox , text = self.config[ "gui" ][ "del" ] , command = self.purge )
		storeButton = ttk.Button( fileBox , text = self.config[ "gui" ][ "upload" ] , command = self.store )
		fileButton = ttk.Button( fileBox , text = self.config[ "gui" ][ "select" ] , command = self.onChooseFile )

		# chpassButton.pack( side = tk.RIGHT )
		purgeButton.pack( side = tk.RIGHT )
		storeButton.pack( side = tk.RIGHT )
		fileButton.pack( side = tk.RIGHT )

		fileEntry.pack( side = tk.LEFT , fill = tk.X , expand = tk.YES )
		fileBox.pack( side = tk.TOP , fill = tk.X )

		progressBox = ttk.Frame( self.master )

		self.fileProgressStatus = ttk.Label( progressBox , width = 20 )
		self.fileProgressLabel = ttk.Label( progressBox , width = 10 )
		self.fileProgressTotal = ttk.Label( progressBox , width = 20 )

		self.connectionProgressStatus = ttk.Label( progressBox , width = 20 )
		self.connectionProgressLabel = ttk.Label( progressBox , width = 10 )
		self.connectionProgressTotal = ttk.Label( progressBox , width = 20 )

		self.fileProgress = ttk.Progressbar( progressBox )
		self.connectionProgress = ttk.Progressbar( progressBox )

		self.fileProgressStatus.pack( side = tk.LEFT )
		self.fileProgressLabel.pack( side = tk.LEFT )
		self.fileProgress.pack( side = tk.LEFT , fill = tk.X , expand = tk.YES )
		self.fileProgressTotal.pack( side = tk.LEFT )

		self.connectionProgressStatus.pack( side = tk.LEFT )
		self.connectionProgressLabel.pack( side = tk.LEFT )
		self.connectionProgress.pack( side = tk.LEFT , fill = tk.X , expand = tk.YES )
		self.connectionProgressTotal.pack( side = tk.LEFT )

		fileBoxStatus = ttk.Frame( self.master )
		filePath = ttk.Entry( fileBoxStatus , textvariable = self.outputValue )
		fileUpload = ttk.Button( fileBoxStatus , text = self.config[ "gui" ][ "download" ] , command = self.fetch )

		filePath.pack( side = tk.LEFT , fill = tk.BOTH , expand = tk.YES )
		fileUpload.pack( side = tk.RIGHT )

		heading_keys = list( self.config[ "gui" ][ "filelist" ][ "heading" ].keys( ) )
		heading_keys.sort( )

		fileBox = ttk.Frame( self.master )
		self.fileList = ttk.Treeview(
			fileBox ,
			columns			= heading_keys ,
			selectmode		= tk.BROWSE ,
			displaycolumns	= "#all" ,
			show			= "headings" ,
		)
		self.fileListScrollbar = ttk.Scrollbar( fileBox )

		for key in heading_keys :
			item = self.config[ "gui" ][ "filelist" ][ "heading" ][ key ]
			if "width" in item :
				self.fileList.column( key , width = item[ "width" ] )
			self.fileList.heading( key , text = item[ "label" ] )

		self.fileList.config( yscrollcommand = self.fileListScrollbar.set )
		self.fileListScrollbar.config( command = self.fileList.yview )

		self.fileList.pack( side = tk.LEFT , fill = tk.BOTH , expand = tk.YES )
		self.fileListScrollbar.pack( side = tk.RIGHT , fill = tk.Y )

		fileBox.pack( side = tk.TOP , fill = tk.BOTH , expand = tk.YES )
		fileBoxStatus.pack( side = tk.TOP , fill = tk.X )
		progressBox.pack( side = tk.TOP , fill = tk.X )

		self.event = dict(
			onAfter		= self.onAfter ,
			onBefore	= self.onBefore ,
			onError		= self.onError ,
			onProgress	= self.onProgress ,
			onConnection= self.onConnection ,
		)

		self.update( )

		return self

	def __percent( self , current , total ) :
		result = current / total * 100.0
		result = float( result )

		return result

	def onProgress( self , current , total ) :
		value = self.__percent( current , total )
		self.fileProgress[ "value" ] = value
		self.fileProgressLabel[ "text" ] = self.config[ "gui" ][ "progress_label_format" ].format( value )
		self.fileProgressTotal[ "text" ] = self.config[ "gui" ][ "progress_total_format" ].format( current , total )

		return value

	def onConnection( self , current , total , item ) :
		value = self.__percent( current , total )
		self.connectionProgress[ "value" ] = value
		self.connectionProgressLabel[ "text" ] = self.config[ "gui" ][ "progress_label_format" ].format( value )
		self.connectionProgressTotal[ "text" ] = self.config[ "gui" ][ "progress_total_format" ].format( current , total )

		return value

	def onAfter( self , * argv , ** kwargs ) :
		result = self.onStatus( "done" , * argv , ** kwargs )

		return result

	def onBefore( self , * argv , ** kwargs ) :
		result = self.onStatus( "connecting" , * argv , ** kwargs )

		return result

	def onError( self , * argv , ** kwargs ) :
		result = self.onStatus( "error" , * argv , ** kwargs )

		return result

	def onStatus( self , key , * argv , ** kwargs ) :
		self.fileProgressStatus[ "text" ] = self.config[ "gui" ][ key ].format( * argv , ** kwargs )

		return True

	def changePassword( self ) :
		dialog = ChangePasswordDialog( self.master , self.config , self )
		dialog.prepare( )

		return self

	def onChooseFile( self ) :
		title = self.config[ "title" ]
		path = tk.filedialog.askopenfilename( title = title )
		self.inputValue.set( path )

		return self

	def selectedItem( self ) :
		selected = self.fileList.selection( )
		if ( selected is None ) or ( not len( selected ) ) :
			self.exception( "file_not_found" )

		current = self.fileList.item( selected )
		try :
			return current[ "values" ][ 0 ]
		except :
			self.exception( "file_not_found" )

	def variableValue( self , variable ) :
		value = variable.get( )
		if not len( value ) :
			self.exception( "file_not_found" )

		return value

	def fileRemote( self ) :
		result = self.selectedItem( )

		return result

	def fileLocal( self ) :
		result = self.variableValue( self.outputValue )

		return result

	def fileInput( self ) :
		result = self.variableValue( self.inputValue )

		return result

	def action( self , action , * args ) :
		result = self.creator.creator.action( action , * args , ** self.event )

		return result


	"""
	def backup( self ) :
		subName = self.subName( )
		result = self.action( subName )

		return result

	def unbackup( self ) :
		subName = self.subName( )
		filename = self.fileRemote( )

		result = self.action( subName , filename )

		return result

	"""

	def purge( self ) :
		subName = self.subName( )
		filename = self.fileRemote( )

		result = self.action( subName , filename )

		return result

	def store( self ) :
		subName = self.subName( )
		fileInput = self.fileInput( )
		result = self.action( subName , fileInput )

		return result

	def fetch( self ) :
		subName = self.subName( )
		filename = self.fileRemote( )

		fileLocal = self.fileLocal( )
		result = self.action( subName , filename , fileLocal )

		return result

	def update( self ) :
		for item in self.fileList.get_children( ) :
			self.fileList.delete( item )

		for file in self.creator.creator.fs_item.action( "all" , None , None , "fetchall" ) :
			values = [ file[ key ] for key in ( "id" , "name" ) ]
			self.fileList.insert( "" , tk.END , values = values , tags = file[ "id" ] )

		return self