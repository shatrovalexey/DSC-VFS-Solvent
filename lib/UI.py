from lib.GUI import GUI
from lib.Widget.FileList import FileList
from lib.Widget.AccountList import AccountList
from lib.Widget.WindowsBalloonTip import WindowsBalloonTip

class UI( GUI ) :
	def prepare( self ) :
		GUI.prepare( self )

		self.messenger = WindowsBalloonTip( self.master , self.config , self , visible = False )
		self.messenger.prepare( )

		self.control = [ ]

		if self.visible :
			control = FileList( self , config = self.config , creator = self )
			control2 = AccountList( self , config = self.config , creator = self )

			control.prepare( )
			control2.prepare( )

			self.control.append( control )
			self.control.append( control2 )

		self.update( )

		return self

	def message( self , ** kwargs ) :
		result = None

		try :
			self.messenger.destroy( True )
			result = self.messenger.execute( ** kwargs )

			return result
		except Exception as exception :
			# isinstance(s, str)
			print( exception )

		return result

	def update( self ) :
		for control in self.control :
			control.update( )

		return self




	def onProgress( self , processed , total ) :
		percent = processed / total * 100.0

		print( "\n%0.02f%%" % percent )

		return self

	def onTitle( self , message , title = None ) :
		if title is None :
			title = self.config[ "gui" ][ "processing" ]

		self.message( title = title , message = message )

		print( self.config[ "line" ] ) ;
		print( message )

		return self

	def onAfter( self , result ) :
		if result :
			message = self.config[ "gui" ][ "success" ]
		else :
			message = self.config[ "gui" ][ "failure" ]

		print( message )

		self.message( title = self.config[ "gui" ][ "done" ] , message = message )

		print( self.config[ "line" ] ) ;
		print( message )

		return self

	def onProgressError( self , filename , exception ) :
		self.message( title = filename , message = exception )

		return self

	def action( self , action , * args , ** kwargs ) :
		method = getattr( self.creator.controller , action )
		if method is None :
			return None

		method(
			onTitle = self.onTitle ,
			onProgress = self.onProgress ,
			onProgressError = self.onProgressError ,
			onAfter = self.onAfter ,
			* args ,
			** kwargs
		)

		return self