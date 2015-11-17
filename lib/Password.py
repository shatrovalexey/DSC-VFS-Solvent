from lib.Interface import Interface
from lib.DriverClass import DriverClass
from lib.Widget.PasswordDialog import PasswordDialog
from Crypto.Cipher import AES
from Crypto import Random
import getpass
import hashlib

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
		# self.set( "f2ox9ermf2ox9erm" )
		# return True

		while True :
			password = self.get( )

			if self.auth( password ) :
				self.set( password )

				return True
		return False

	def get( self , prompt = None ) :
		if prompt is None :
			prompt = self.config[ "gui" ][ "enter_password" ]

		"""
		self.password = None

		if not self.was :
			self.was = True
			result = "f2ox9ermf2ox9erm"
		else :
			result = None
		"""

		result = None

		while ( result is None ) or ( not len( result ) ) :
			if self.visible :
				self.passwordDialog = PasswordDialog( self.creator.master , config = self.config , creator = self , visible = False )
				self.passwordDialog.prepare( )

				try :
					self.creator.master.wait_window( self.passwordDialog.top )
				except :
					exit( 0 )

				del self.passwordDialog
				result = self.password
			else :
				result = getpass.getpass( prompt )

		return result

	def change_password( self , password1 , password2 , password3 ) :
		if not self.equals( password2 , password3 ) :
			return None

		if not self.check( password1 ) :
			return None

		self.set( password2 )
		self.config[ "password" ] = self.hash( password2 )
		self.config[ "IV" ] = self.generate( )[ 0 : ( AES.block_size - 1 ) ]
		self.config.store( )
		self.config.fetch( )

		return password2

	def change( self ) :
		password1 = self.get( self.config[ "gui" ][ "enter_password_old" ] )
		password2 = self.get( self.config[ "gui" ][ "enter_password_new" ] )
		password3 = self.get( self.config[ "gui" ][ "enter_password_new2" ] )

		result = self.change_password( password1 , password2 , password3 )

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
		md5check1 = self.config[ "password" ]
		md5check2 = self.hash( password )

		if md5check1 == md5check2 :
			return True

		self.creator.message(
			title = self.config[ "gui" ][ "error" ] ,
			message = self.config[ "error" ][ "invalid_password" ]
		)

		return False
