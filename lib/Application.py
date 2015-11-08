from lib.Interface import Interface
from lib.Config import Config
from lib.SQLite import SQLite
from lib.SQLiteConsumer import SQLiteConsumer
from lib.Controller import Controller
from lib.UI import UI
import os

class Application( Interface ) :
	def __init__( self , configFile , visible = True ) :
		self.configFile = configFile
		self.config = Config( self.configFile )
		self.config.fetch( )
		self.__prepareConfig( )

		self.visible = visible

		self.prepareSQLite3( )

		self.controller = Controller( self )
		self.controller.configure( )

	def prepareSQLite3( self ) :
		self.conn = SQLite( creator = self , filename = self.config[ "db" ][ "query" ] )
		self.conn.prepare( self.config[ "db" ][ "path" ] )

		for entity in self.conn.config :
			consumer = SQLiteConsumer( entity = entity , creator = self.conn )
			setattr( self , entity , consumer )

		return self

	def __prepareConfig( self ) :
		self.config[ "libPath" ] = self.__preparePath( self.config[ "libPath" ] )
		self.config[ "driverPath" ] = self.__preparePath( self.config[ "driverPath" ] )

		for key in self.config[ "gui" ][ "icon" ] :
			self.config[ "gui" ][ "icon" ][ key ] = self.__preparePath( self.config[ "gui" ][ "icon" ][ key ] )

		self.config[ "gui" ][ "widgetPath" ] = self.__preparePath( self.config[ "gui" ][ "widgetPath" ] )
		self.config[ "db" ][ "query" ] = self.__preparePath( self.config[ "db" ][ "query" ] )
		self.config[ "db" ][ "path" ] = self.__preparePath( self.config[ "db" ][ "path" ] )

		return self

	def __preparePath( self , path ) :
		result = os.path.abspath( os.path.join( os.path.dirname( __file__ ) , '..' , path ) )

		return result

	def prepare( self ) :
		self.ui = UI( None , config = self.config , creator = self , visible = self.visible )
		self.ui.prepare( )

		return self

	def execute( self ) :
		if self.visible :
			self.ui.execute( )

		return self

	def action( self , action , * argv , ** kwargs ) :
		error = self.config[ "error" ]
		onError = lambda exception : self.ui.message(
			title	= str( exception ) ,
			message	= error[ "%s_comment" % action ].format( * argv ) ,
		)
		try :
			target = lambda : self.controller.action( action , onError , argv , kwargs )
			finish = lambda : self.ui.update( ) and self.ui.message(
				title	= error[ "%s_title" % action ].format( * argv , ** kwargs ) ,
				message	= error[ "%s_comment" % action ].format( * argv , ** kwargs ) ,
			)
			self.run( target = target , finish = finish )
		except Exception as exception :
			onError( exception )

			return False
		return True

	def run( self , target , finish ) :
		if not self.visible :
			target( )
			return finish( )

		if not self.thread(
			target = target ,
			finish = lambda: self.ui.update( ) and finish( )
		) :
			self.exception( "unknown" )

		return False