from Crypto import Random
from Crypto.Cipher import AES
from lib.Interface import Interface
import hashlib

class DriverClass( Interface ) :
	def __init__( self , creator , account = None ) :
		self.account = account
		self.creator = creator
		self.config = self.creator.config
		self.blockSize = self.config[ "blockSize" ]

		self.random = Random.new( )
		self.hash = hashlib.md5( )

		return None

	def __hash( self , message ):
		self.hash.update( message )
		result = self.hash.hexdigest( )

		return result

	def __rand( self , length = 32 ):
		result = self.random.read( length )

		return result

	def __password( self ):
		rand = self.__rand( )
		result = self.__hash( rand )

		return result

	def encrypt( self , message ):
		IV = self.__rand( self.blockSize )
		password = self.__password( )
		aes = AES.new( password , AES.MODE_CFB , IV )
		result = IV + aes.encrypt( message )

		return ( password , result )

	def decrypt( self , password , message ):
		IV = message[ : self.blockSize ]
		aes = AES.new( password , AES.MODE_CFB , IV )
		result = aes.decrypt( message[ self.blockSize : ] )

		return result