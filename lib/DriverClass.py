from Crypto.Cipher import AES
from lib.Interface import Interface
import hashlib
import binascii

class DriverClass( Interface ) :
	def __init__( self , creator , account = None ) :
		self.account = account
		self.creator = creator
		self.config = self.creator.config

		return None

	def encrypt( self , message , password = None ) :
		IV = self.creator.password.rand( AES.block_size )

		if password is None :
			password = self.creator.password.generate( )

		if message is None :
			return ( password , None )

		aes = AES.new( password , AES.MODE_CFB , IV )
		result = IV + aes.encrypt( message )

		return ( password , result )

	def decrypt( self , message , password ) :
		if message is None :
			return None

		IV = message[ : AES.block_size ]
		aes = AES.new( password , AES.MODE_CFB , IV )
		result = aes.decrypt( message[ AES.block_size : ] )

		return result

	def encryptor( self ) :
		password = self.creator.password.password
		def _( message ) :
			result = self.encrypt( message , password )[ 1 ]
			return result
		return _

	def decryptor( self ) :
		password = self.creator.password.password
		def _( message ) :
			result = self.decrypt( message , password ).decode( )
			return result
		return _

	def _recrypt( self , message , password_new ) :
		password_old = self.creator.password.password

		result = self.decrypt( message , password_old )
		result = self.encrypt( message , password_new )

		return result

	def recryptor( self ) :
		def _( message , password ) :
			try :
				( password , result ) = self._recrypt( message , password )
			except Exception as exception :
				print( exception )

			return result
		return _
