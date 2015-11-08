from lib.DriverClass import DriverClass
import ftplib
import io

class DriverFTP( DriverClass ) :
	def prepare( self ) :
		self.connection = ftplib.FTP( source_address = ( self.account[ "host" ] , self.account[ "port" ] ) )
		self.connection.login( user = self.account[ "login" ] , password = self.account[ "password" ] )

		try :
			self.connection.mkd( self.account[ "path" ] )
		except :
			pass

		self.connection.cwd( self.account[ "path" ] )

		return self

	def finish( self ) :
		self.connection.quit( )

		return self

	def purge( self , id ) :
		return self.connection.purge( id )

	def store( self , message ) :
		fh = io.StringIO( message )
		id = self.connection.storbinary( "STOU" , fh , blocksize = self.config[ "buffSize" ] )
		fh.close( )

		return id

	def fetch( self , id ) :
		fh = io.StringIO( )
		self.connection.retrbinary( "RETR \"%s\"" % ( id ) , fh.write , blocksize = self.config[ "buffSize" ] )
		message = fh.readall( )
		fh.close( )

		return message