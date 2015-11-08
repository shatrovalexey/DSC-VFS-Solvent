from lib.DriverClass import DriverClass
import imaplib
import binascii
import email.parser
import sys
from tkinter.messagebox import *

class DriverIMAP4( DriverClass ) :
	def prepare( self ) :
		self.connection = imaplib.IMAP4_SSL( host = self.account[ "host" ] , port = self.account[ "port" ] )
		self.connection.login( self.account[ "login" ] , self.account[ "password" ] )
		self.connection.create( mailbox = self.account[ "path" ] )
		self.connection.select( mailbox = self.account[ "path" ] )

		return self

	def finish( self ) :
		try :
			self.connection.logout( )
			self.connection.close( )
		except :
			return False

		return True

	def purge( self , id ) :
		while True :
			try :
				self.connection.uid( 'STORE' , id , '+FLAGS' , '(\\deleted)' )
				status , data = self.connection.expunge( )

				if status == "OK" :
					return True

				self.exception( 'purge' )
			except Exception as exception :
				self.exception( exception )
				self.restart( )

		return False

	def store( self , message ) :
		encoding = self.config[ 'charset' ]
		msg = email.message.Message( )
		message = binascii.b2a_hex( message ).decode( encoding )
		msg.set_payload( message )
		data = msg.as_string( ).encode( encoding )

		while True :
			try :
				status , data = self.connection.append( mailbox = self.account[ "path" ] , message = data , flags = None , date_time = None )
				if status == 'OK' :
					break

				self.exception( 'store' , status = status , data = data )
			except Exception as exception :
				print( exception )
				self.restart( )

		response = data[ 0 ]
		responseList = response.split( )
		responseData = responseList[ 2 ]
		file_id = responseData[ : -1 ]
		file_id = file_id.decode( encoding = encoding )

		return file_id

	def fetch( self , id ) :
		status = None
		while True :
			try :
				status , result = self.connection.uid( "FETCH" , id , "(RFC822)" )
			except Exception as exception :
				print( exception )
				self.restart( )
				continue
			break

		if status != "OK" :
			self.exception( "fetch" , status = status , result = result )

		msg = None

		try :
			msg = email.message_from_binary_file( result )
		except :
			msg = email.message_from_bytes( result[ 0 ][ 1 ] )

		result = msg.get_payload( )
		result = binascii.a2b_hex( result.rstrip( ) )

		return result