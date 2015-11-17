from lib.Interface import Interface
from lib.Config import Config
from lib.SQLite import SQLite
from lib.SQLiteConsumer import SQLiteConsumer
from lib.Controller import Controller
from lib.UI import UI
from lib.Password import Password
import os

class Application( Interface ) :
	def __init__( self , configFile , visible = True ) :
		self.configFile = configFile
		self.config = Config( self.configFile )
		self.config.fetch( )

		self.visible = visible
		self.password = None

		self.__prepareConfig( )

		self.controller = Controller( self )
		self.controller.configure( )

	def getDBA( self , path , query = None ) :
		conn = SQLite( creator = self , filename = query )
		conn.prepare( path )

		return conn

	def prepareSQLite3( self ) :
		self.conn = self.getDBA( self.config[ "db" ][ "path" ] , self.config[ "db" ][ "query" ] )

		for entity in self.conn.config :
			consumer = SQLiteConsumer( entity = entity , creator = self.conn )
			setattr( self , entity , consumer )

		return self

	def __prepareConfig( self ) :
		self.config[ "libPath" ] = self.preparePath( self.config[ "libPath" ] )
		self.config[ "driverPath" ] = self.preparePath( self.config[ "driverPath" ] )

		for key in self.config[ "gui" ][ "icon" ] :
			self.config[ "gui" ][ "icon" ][ key ] = self.preparePath( self.config[ "gui" ][ "icon" ][ key ] )

		for key in ( "query" , "path" , "recrypt" ) :
			self.config[ "db" ][ key ] = self.preparePath( self.config[ "db" ][ key ] )

		self.config[ "gui" ][ "widgetPath" ] = self.preparePath( self.config[ "gui" ][ "widgetPath" ] )

		return self

	def preparePath( self , path , add = '..' ) :
		args = [ os.path.dirname( __file__ ) ]

		if add is not None :
			args.append( add )

		args.append( path )
		result = os.path.abspath( os.path.join( * args ) )

		return result

	def prepare( self ) :
		self.ui = UI( None , config = self.config , creator = self , visible = self.visible )

		self.password = Password( self.ui )
		self.password.prepare( )
		self.password.login( )

		self.prepareSQLite3( )
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

		onFinish = lambda: self.ui.update( ) and finish( )

		if not self.thread( target = target , finish = onFinish ) :
			self.exception( "unknown" )

		return False