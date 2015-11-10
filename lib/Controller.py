from lib.DriverClass import DriverClass
from lib.SQLite import SQLite
import os , io , random
import hashlib
import sqlite3
import gzip
import datetime
from os import walk

class Controller( DriverClass ) :
	def configure( self ) :
		self.connection = { }

		return self

	def prepare( self , account ) :
		driver_id = account[ "driver_id" ]
		driverData = self.creator.acc_driver[ driver_id ]
		driverName = driverData[ "name" ]
		driverPath = self.config[ 'driverPathMap' ].format(
			driverPath		= self.config[ 'driverPath' ] ,
			pathSeparator	= self.config[ 'pathSeparator' ] ,
			driverName		= driverName ,
			driverExtension	= self.config[ 'driverExtension' ]
		)
		driver = self.getObject( driverName , driverPath , creator = self , account = account )
		driver.prepare( )

		return driver

	def action( self , action , onError , argv , kwargs ) :
		try :
			fn = getattr( self , action )
			if fn and fn( * argv , ** kwargs ) :
				return True

			self.exception( action )
		except Exception as exception :
			self.creator.prepareSQLite3( )

			if "break" in kwargs :
				onError( exception )

			kwargs[ "break" ] = True

			return self.action( action , onError , argv , kwargs )
		except Exception as exception :
			onError( exception )

		return False

	def driver( self , account_id = None , ** kwargs ) :
		if account_id not in self.connection :
			suggestions = { id: True for id in self.creator.acc_item.keys( ) }
			total = len( suggestions.keys( ) )
			current = 0
			while True :
				keys = suggestions.keys( )

				if not len( keys ) :
					self.exception( "no_account" )

				account_id = random.choice( list( keys ) )

				try :
					item = self.creator.acc_item[ account_id ]
					self.event( "connection" , onAction = lambda fn : fn( current , total , item ) , ** kwargs )
					connection = self.prepare( item )

					if connection is None :
						self.exception( "error" )
					self.connection[ account_id ] = connection

					break
				except Exception as exception :
					del suggestions[ account_id ]
				current += 1
			else :
				self.exception( "no_account" )

		return ( account_id , self.connection[ account_id ] )

	def reader( self , fh ) :
		buffSize = self.config[ 'buffSize' ]

		def _( ) :
			while True :
				message = fh.read( buffSize )
				if not len( message ) :
					break

				yield message

		result = iter( _( ) )

		return result

	def read( self , fh ) :
		reader = self.reader( fh )
		for message in reader :
			msglen = len( message )
			password , result = self.encrypt( message = message )

			yield ( msglen , password , result )

	def write( self , fh , password , message ) :
		try :
			decrypted = self.decrypt( password = password , message = message )
			fh.write( decrypted )
		except Exception as exception :	
			self.exception( exception )

			return False
		return True

	def purge( self , file_id , ** kwargs ) :
		self.event( "before" , onAction = lambda fn : fn( file_id ) , ** kwargs )
		result = [ ]
		processed = 0

		if file_id not in self.creator.fs_item :
			file_id = self.creator.fs_item.action( "search_by_name" , None , file_id , "fetchone" )

			if file_id not in self.creator.fs_item :
				self.exception( "no_file" )

		try :
			for item in self.creator.fs_node.action( "fs_item_nodes" , None , file_id , "fetchall" ) :
				account , driver = self.driver( item[ 'account_id' ] , ** kwargs )
				purge_result = driver.purge( item[ "fs_node_id" ] )
				if not purge_result :
					self.exception( 'purge' )

				del self.creator.fs_node[ item[ "id" ] ]

				processed += 1
				self.event( "progress" , onAction = lambda fn : fn( processed , total ) , ** kwargs )

				result.append( purge_result )
			del self.creator.fs_item[ file_id ]
		except Exception as exception :
			self.event( "error" , onAction = lambda fn : fn( file_id , item ) , ** kwargs )
			raise exception

		self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

		return result

	def sync( self , path , ** kwargs ) :
		self.event( 'before' , onAction = lambda fn : fn( file_id ) , ** kwargs )

		filenamelist = dict( )

		for ( dirpath , dirnames , filenames ) in walk( path ) :
			for item in filenames :
				filename = os.path.join( dirpath , item )
				filename = os.path.abspath( filename )
				filenamelist[ filename ] = os.path.getsize( filename )

		total = sum( filenamelist.values( ) )
		processed = 0

		for filename in filenamelist :
			self.event( "title" , onAction = lambda fn : fn( filename ) , ** kwargs )

			hash = self.creator.fs_item.action( "search_hash_by_name" , None , filename , "fetchone" )

			if hash is not None :
				with io.open( filename , "rb" ) as fh :
					md5 = hashlib.md5( )
					reader = self.reader( fh )
					for message in reader :
						md5.update( message )

					if hash == md5.hexdigest( ) :
						continue

					try :
						self.purge( filename )
					except Exception as exception :
						self.event( "progressError" , onAction = lambda fn : fn( filename , exception ) , ** kwargs )
						pass

			self.store( filename )
			processed += filenamelist[ filename ]

			title = self.config[ "gui" ][ "downloading" ]
			onProgress = lambda fn : fn( processed , total )

			self.event( "progress" , title = title , onAction = onProgress , ** kwargs )
		self.event( "after" , onAction = lambda fn : fn( True ) , ** kwargs )

		return filenamelist

	def restore( self , path , ** kwargs ) :
		path = os.path.abspath( path )

		self.event( "before" , onAction = lambda fn : fn( path ) , ** kwargs )

		files = [ file for file in self.creator.fs_item.action( "search_by_path" , None , path , "fetchall" ) ]
		file_names = [ file[ "name" ] for file in files ]
		file_ids = [ file[ "id" ] for file in files ]

		common_path = os.path.commonprefix( file_names )
		common_path_len = len( common_path )
		common_prefix = os.path.relpath( path )

		total = len( file_ids )
		processed = 0
		result = True

		while len( file_ids ) > 0 :

			file_id = file_ids.pop( )
			file_name = file_names.pop( )

			new_file = os.path.join( common_prefix , file_name[ common_path_len : ] )
			self.event( "title" , onAction = lambda fn : fn( new_file ) , ** kwargs )
			self.fetch( file_id , new_file )

			processed += 1

			self.event( "progress" , onAction = lambda fn : fn( processed , total ) , ** kwargs )

		self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

		return file_ids

	def drop( self , path , ** kwargs ) :
		self.event( "before" , onAction = lambda fn : fn( file_id ) , ** kwargs )

		file_ids = self.creator.fs_item.action( "search_by_path" , None , path , "fetchcol" )

		if file_ids is None :
			self.exception( "file_not_found" )

		total = len( file_ids )
		processed = 0

		for file_id in file_ids :
			filename = self.creator.fs_item.action( "get_name" , None , file_id , "fetchone" )

			onTitle = lambda fn : fn( message = filename , title = self.config[ "gui" ][ "deleting" ] )
			self.event( "title" , onAction = onTitle , ** kwargs )
			self.purge( file_id )

			processed += 1

			self.event( "progress" , onAction = lambda fn : fn( processed , total ) , ** kwargs )

		self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

		return file_ids

	def store( self , filename , ** kwargs ) :
		self.event( 'before' , onAction = lambda fn : fn( filename ) , ** kwargs )

		if filename is None :
			self.exception( 'no_file' )

		file_ids = self.creator.fs_item.action( "search_by_name" , None , key = filename , fetch = "fetchcol" )
		if file_ids is not None :
			for id in file_ids :
				self.purge( id )

		processed = 0

		try :
			file_size = os.stat( filename ).st_size
			fs_item_id = self.creator.fs_item.append( { "name": filename } )

			md5 = hashlib.md5( )
			fh = io.open( filename , 'rb' )

			for msglen , password , message in self.read( fh ) :
				account_id , driver = self.driver( )
				md5.update( message )
				fs_node_id = driver.store( message = message )
				self.creator.fs_node.action( "store" , {
					"fs_item_id": fs_item_id ,
					"account_id": account_id ,
					"fs_node_id": fs_node_id ,
					"password": password
				} )
				processed += msglen
				onProgress = lambda fn : fn( processed , file_size )
				self.event( "progress" , title = self.config[ "gui" ][ "downloading" ] , onAction = onProgress , ** kwargs )
			fh.close( )

			checksum = md5.hexdigest( )

			self.creator.fs_item.action( "update" , {
				"name": filename ,
				"size": file_size ,
				"checksum": checksum
			} , fs_item_id )

		except Exception as exception :
			self.event( 'error' , onAction = lambda fn : fn( filename ) , ** kwargs )
			raise exception

		self.event( 'after' , onAction = lambda fn : fn( result ) , ** kwargs )

		return fs_item_id

	def fetch( self , file_id , file_local , ** kwargs ) :
		self.event( 'before' , onAction = lambda fn : fn( file_id , file_local ) , ** kwargs )

		result = [ ]
		processed = 0

		try :
			if file_id not in self.creator.fs_item :
				file_id = self.creator.fs_item.action( "search_by_name" , None , file_id , "fetchone" )

				if file_id is None :
					self.exception( "file_not_found" )

			fs_item = self.creator.fs_item[ file_id ]
			fs_nodes = [ fs_node for fs_node in self.creator.fs_node.action( "fs_item_nodes" , None , file_id , "fetchall" ) ]

			total = len( fs_nodes )
			fh = io.open( file_local , "wb" )

			for fs_node in fs_nodes :
				account , driver = self.driver( fs_node[ "account_id" ] )
				message = driver.fetch( fs_node[ "fs_node_id" ] )

				password = fs_node[ "password" ]

				self.write( fh , password , message )

				result.append( fs_node[ "id" ] )

				onProgress = lambda fn : fn( processed , total )
				title = self.config[ "gui" ][ "uploading" ]

				if self.event( "progress" , title = title , onAction = onProgress , ** kwargs ) :
					processed += 1
			fh.close( )
		except Exception as exception :
			self.event( "error" , onAction = lambda fn : fn( file_id , file_local ) , ** kwargs )
			raise exception

		self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

		return True

	def unbackup( self , path , fs_item_id , * args , ** kwargs ) :
		if self.creator.visible :
			return None

		fs_item = self.creator.fs_item[ fs_item_id ]

		if fs_item is None :
			self.exception( "file_not_found" )

		dirname = os.path.dirname( self.config[ "db" ][ "backup_path" ] )
		filename = os.path.basename( fs_item[ "name" ] )

		try :
			os.mkdir( dirname )
		except :
			pass

		localfile = os.path.join( dirname , filename )
		localfile = self.creator.preparePath( localfile )
		result = self.fetch( fs_item_id , localfile )

		if not result :
			self.exception( "file_not_found" )

		self.creator.conn.finish( )
		backupfile = self.__backup( )

		inp = gzip.open( localfile , mode = "rb" )
		out = io.open( self.config[ "db" ][ "path" ] , "wb" )

		for block in self.reader( inp ) :
			out.write( block )

		out.close( )
		inp.close( )

		os.remove( localfile )
		self.creator.prepareSQLite3( )

		print( backupfile )

		return self

	def __backup( self , * args , ** kwargs ) :
		backuppath = self.config[ "db" ][ "backup_path" ]
		backupfile = datetime.datetime.now( ).strftime( backuppath )
		backupfile = self.creator.preparePath( backupfile )

		try :
			os.mkdir( backuppath )
		except :
			pass

		out = gzip.open( backupfile , mode = "wb" )
		inp = io.open( self.config[ "db" ][ "path" ] , "rb" )

		for block in self.reader( inp ) :
			out.write( block )

		inp.close( )
		out.close( )

		return backupfile

	def backup( self , * args , ** kwargs ) :
		if self.creator.visible :
			return None

		self.event( "before" , onAction = lambda fn : fn( file_id , file_local ) , ** kwargs )

		self.creator.conn.finish( )
		backupfile = self.__backup( )
		self.creator.prepareSQLite3( )
		result = self.store( backupfile )

		print( result )

		self.event( "after" , onAction = lambda fn : fn( file_id , file_local ) , ** kwargs )

		return self