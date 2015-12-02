from lib.Interface import Interface
from lib.DriverClass import DriverClass
from lib.Widget.PasswordDialog import PasswordDialog
from Crypto.Cipher import AES
from Crypto import Random
import getpass , hashlib

class Password( Interface ) :
	def __init__( self , creator ) :
		self.creator = creator
		self.config = creator.config
		self.visible = creator.visible
		self.random = Random.new( )
		self.password = None
		self.suggestedPassword = None
		self.was = False

	def hash( self , message ) :
		if type( message ) == str :
			message = message.encode( )

		md5 = hashlib.md5( message ) ;
		result = md5.hexdigest( )

		return result

	def rand( self , length = 32 ):
		result = self.random.read( length )

		return result

	def generate( self ):
		rand = self.rand( )
		result = self.hash( rand )

		return result

	def set( self , password ) :
		self.password = password

		return self

	def auth( self , password ) :
		if self.check( password ) :
			self.set( password )

			return True

		self.creator.message(
			title = self.config[ "gui" ][ "error" ] ,
			message = self.config[ "error" ][ "invalid_password" ]
		)

		return False

	def login( self ) :
		"""
		self.set( "f2ox9ermf2ox9erm" )
		return True
		"""

		password = self.get( )

		if self.auth( password ) :
			self.set( password )

			return True
		return False

	def get( self , prompt = None ) :
		if prompt is None :
			prompt = self.config[ "gui" ][ "enter_password" ]

		if self.visible :
			self.passwordDialog = PasswordDialog(
				self.creator.master ,
				config = self.config ,
				creator = self ,
				visible = self.visible
			)
			self.passwordDialog.prepare( )
			self.creator.master.wait_window( self.passwordDialog )
			del self.passwordDialog
		else :
			self.password = getpass.getpass( prompt )

		return self.password

	def change_password( self , password1 , password2 , password3 ) :
		if not self.equals( password2 , password3 ) :
			return None

		if not self.check( password1 ) :
			return None

		self.set( password2 )
		self.config[ "password" ] = self.hash( password2 )
		self.config[ "IV" ] = self.generate( )[ 0 : ( AES.block_size - 1 ) ]
		self.config.update( )

		return password2

	def change( self ) :
		args = [ self.config[ "gui" ][ "enter_password_" + key ] for key in ( "old" , "new" , "new2" ) ]
		result = self.change_password( * args )

		return result

	def equals( self , password1 , password2 ) :
		if password1 == password2 :
			return True

		self.creator.message(
			title = self.config[ "gui" ][ "error" ] ,
			message = self.config[ "error" ][ "password_donotmatch" ]
		)

		return False

	def check( self , password ) :
		if password is None :
			return False

		md5check1 = self.config[ "password" ]
		md5check2 = self.hash( password )

		if md5check1 == md5check2 :
			return True

		self.creator.message(
			title = self.config[ "gui" ][ "error" ] ,
			message = self.config[ "error" ][ "invalid_password" ]
		)

		return False
