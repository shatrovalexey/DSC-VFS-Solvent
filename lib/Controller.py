from lib.DriverClass import DriverClass
from lib.SQLite import SQLite
import os , io , random , hashlib , shutil , sqlite3 , gzip , datetime , collections , tempfile
import qrcode

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
		while True :
			try :
				fn = getattr( self , action )
				if fn and fn( * argv , ** kwargs ) :
					return True

				self.exception( action )
			except sqlite3.ProgrammingError as exception :
				self.creator.prepareSQLite3( )

				if "break" in kwargs :
					onError( exception )

				kwargs[ "break" ] = True
				continue
			except Exception as exception :
				onError( exception )
			break
		return False

	def __driver( self , account_id , ** kwargs ) :
		item = self.creator.acc_item[ account_id ]

		if item is None :
			return None

		self.event( "connection" , onAction = lambda fn : fn( current , total , item ) , ** kwargs )
		connection = self.prepare( item )

		if connection is None :
			self.exception( "error" )

		return connection

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
					self.connection[ account_id ] = self.__driver( account_id )
					break
				except :
					del suggestions[ account_id ]
				current += 1

		return ( account_id , self.connection[ account_id ] )

	def reader( self , fh ) :
		def _( ) :
			try :
				while True :
					message = fh.read( self.config[ "buffSize" ] )
					assert len( message )
					yield message
			except AssertionError as exception :
				return None

		return iter( _( ) )

	def read( self , fh ) :
		for message in self.reader( fh ) :
			msglen = len( message )
			password , result = self.encrypt( message )

			yield ( msglen , password , result )

	def write( self , fh , password , message ) :
		try :
			decrypted = self.decrypt( message , password )
			fh.write( decrypted )
		except Exception as exception :
			self.exception( exception )

			return False
		return True

	def purge( self , file_id , ** kwargs ) :
		self.event( "before" , onAction = lambda fn : fn( file_id ) , ** kwargs )

		if file_id not in self.creator.fs_item :
			file_id = self.creator.fs_item.action( "search_by_name" , None , file_id , "fetchone" )

			if file_id not in self.creator.fs_item :
				self.exception( "no_file" )

		result = [ ]

		try :
			data = self.creator.fs_node.action( "fs_item_nodes" , None , file_id , "fetchall" )
			for ( processed , item ) in enumerate( data ) :
				account , driver = self.driver( item[ 'account_id' ] , ** kwargs )
				purge_result = driver.purge( item[ "fs_node_id" ] )
				if not purge_result :
					self.exception( 'purge' )

				del self.creator.fs_node[ item[ "id" ] ]

				self.event( "progress" , onAction = lambda fn : fn( processed , total ) , ** kwargs )

				result.append( purge_result )
			del self.creator.fs_item[ file_id ]
		except Exception as exception :
			self.event( "error" , onAction = lambda fn : fn( file_id , item ) , ** kwargs )
			raise exception

		self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

		return result

	def sync( self , path , ** kwargs ) :
		self.event( "before" , onAction = lambda fn : fn( file_id ) , ** kwargs )

		filenamelist = dict( )

		for ( dirpath , dirnames , filenames ) in os.walk( path ) :
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
					for message in self.reader( fh ) :
						md5.update( message )

					if hash == md5.hexdigest( ) :
						continue

					try :
						self.purge( filename )
					except Exception as exception :
						self.event( "progressError" , onAction = lambda fn : fn( filename , exception ) , ** kwargs )

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

		files = self.creator.fs_item.action( "search_by_path" , None , path , "fetchall" , True )

		if files is None :
			self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

			return False

		common_path = os.path.commonprefix( * [ file[ "name" ] for file in files ] )
		common_path_len = len( common_path )
		common_prefix = os.path.relpath( path )

		total = len( files )
		processed = 0
		result = True

		for ( processed , file ) in enumerate( files ) :
			file_id = file[ "id" ]
			file_name = file[ "name" ]
			new_file = os.path.join( common_prefix , file_name[ common_path_len : ] )

			self.event( "title" , onAction = lambda fn : fn( new_file ) , ** kwargs )
			self.fetch( file_id , new_file )
			self.event( "progress" , onAction = lambda fn : fn( processed , total ) , ** kwargs )

		self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

		return True

	def drop( self , path , ** kwargs ) :
		self.event( "before" , onAction = lambda fn : fn( file_id ) , ** kwargs )

		file_ids = self.creator.fs_item.action( "search_by_path" , None , path , "fetchcol" , True )
		total = len( file_ids )

		for ( processed , file_id ) in enumerate( file_ids ) :
			filename = self.creator.fs_item.action( "get_name" , None , file_id , "fetchone" )
			title = self.config[ "gui" ][ "deleting" ]
			onTitle = lambda fn : fn( message = filename , title = title )
			self.event( "title" , onAction = onTitle , ** kwargs )
			self.purge( file_id )
			self.event( "progress" , onAction = lambda fn : fn( processed , total ) , ** kwargs )
		else :
			self.exception( "file_not_found" )

		self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

		return file_ids

	def store( self , filename , ** kwargs ) :
		self.event( 'before' , onAction = lambda fn : fn( filename ) , ** kwargs )

		if filename is None :
			self.exception( "no_file" )

		for fs_item_id in self.creator.fs_item.action( "search_by_name" , None , key = filename , fetch = "fetchcol" ) :
			self.purge( fs_item_id )

		processed = 0
		try :
			filesize = os.stat( filename ).st_size
			fs_item_id = self.creator.fs_item.append( { "name": filename } )

			md5 = hashlib.md5( )
			fh = io.open( filename , "rb" )

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
				onProgress = lambda fn : fn( processed , filesize )
				self.event( "progress" , title = self.config[ "gui" ][ "downloading" ] , onAction = onProgress , ** kwargs )
			fh.close( )

			checksum = md5.hexdigest( )

			self.creator.fs_item.action( "update" , {
				"name": filename ,
				"size": str( filesize ) ,
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
		file_local = os.path.realpath( file_local )

		try :
			file_dir = os.path.dirname( file_local )
			if not os.access( file_dir , os.W_OK ) :
				self.exception( "access_denied" )

			if file_id not in self.creator.fs_item :
				for file_id in self.creator.fs_item.action( "search_by_name" , None , file_id , "fetchcol" ) :
					break
				else :
					self.exception( "file_not_found" )

			fs_item = self.creator.fs_item[ file_id ]
			fs_nodes = self.creator.fs_node.action( "fs_item_nodes" , None , file_id , "fetchall" , True )
			total = len( fs_nodes )

			with io.open( file_local , "wb" ) as fh :
				for ( processed , fs_node ) in enumerate( fs_nodes ) :
					account , driver = self.driver( fs_node[ "account_id" ] )
					message = driver.fetch( fs_node[ "fs_node_id" ] )
					password = fs_node[ "password" ]

					self.write( fh , password , message )
					result.append( fs_node[ "id" ] )

					title = self.config[ "gui" ][ "uploading" ]
					onProgress = lambda fn : fn( processed , total )
					self.event( "progress" , title = title , onAction = onProgress , ** kwargs )
				fh.close( )
		except Exception as exception :
			self.event( "error" , onAction = lambda fn : fn( file_id , file_local ) , ** kwargs )
			raise exception

		self.event( "after" , onAction = lambda fn : fn( result ) , ** kwargs )

		return True

	def copy( self , filename_inp , filename_out ) :
		try :
			inp = gzip.open( filename_inp , mode = "rb" )
			out = io.open( filename_out , "wb" )

			shutil.copyfileobj( inp , out )

			out.close( )
			inp.close( )
		except Exception as exception :
			self.event( "error" , onAction = lambda fn : fn( exception ) , ** kwargs )

			return False
		return True

	def mkdir( self , dirname ) :
		try :
			os.mkdir( backuppath )
		except Exception as exception :
			self.event( "error" , onAction = lambda fn : fn( exception ) , ** kwargs  )

			return False
		return True

	def unbackup( self , path , fs_item_id , * args , ** kwargs ) :
		self.event( "before" , onAction = lambda fn : fn( fs_item_id ) , ** kwargs  )

		fs_item = self.creator.fs_item[ fs_item_id ]
		if fs_item is None :
			self.exception( "file_not_found" )

		dirname = os.path.dirname( self.config[ "db" ][ "backup_path" ] )
		filename = os.path.basename( fs_item[ "name" ] )

		self.mkdir( dirname )

		localfile = os.path.join( dirname , filename )
		localfile = self.creator.preparePath( localfile )
		result = self.fetch( fs_item_id , localfile )

		if not result :
			self.exception( "file_not_found" )

		self.creator.conn.finish( )
		backupfile = self.__backup( )

		self.copy( localfile , self.config[ "db" ][ "path" ] )
		os.remove( localfile )

		self.creator.prepareSQLite3( )
		print( backupfile )

		self.event( "after" , onAction = lambda fn : fn( fs_item_id ) , ** kwargs  )

		return self

	def __backup( self , * args , ** kwargs ) :
		backuppath = self.config[ "db" ][ "backup_path" ]
		backupfile = datetime.datetime.now( ).strftime( backuppath )
		backupfile = self.creator.preparePath( backupfile )

		self.mkdir( backuppath )
		self.copy( backupfile , self.config[ "db" ][ "path" ] )

		return backupfile

	def backup( self , * args , ** kwargs ) :
		self.event( "before" , onAction = lambda fn : fn( file_id , file_local ) , ** kwargs )

		self.creator.conn.finish( )
		backupfile = self.__backup( )
		self.creator.prepareSQLite3( )
		result = self.store( backupfile )

		( qrcode_fileno , qrcode_filename ) = tempfile.mkstemp( suffix = ".png" )
		with io.open( qrcode_filename , "wb" ) as qrcode_fh :
			qrcode_img = qrcode.make( result )
			qrcode_img.save( qrcode_fh )
			qrcode_fh.close( )

		print( result )
		print( qrcode_filename )

		self.event( "after" , onAction = lambda fn : fn( file_id , file_local ) , ** kwargs )

		return self

	def recrypt( self , path , password , * args , ** kwargs ) :
		self.event( "before" , onAction = lambda fn : fn( password ) , ** kwargs )

		if password is None :
			password = self.creator.password.generate( )
		else :
			try :
				if len( password ) not in self.config[ "passwordLen" ] :
					self.exception( "password_len" )
			except Exception as exception :
				self.event( "error" , onAction = lambda fn : fn( exception ) , ** kwargs )

				return False

		total = count( self.creator.conn.config[ "action" ][ "recrypt" ] )

		for ( processed , sql ) in enumerate( self.creator.conn.config[ "action" ][ "recrypt" ] ) :
			processed += 1

			if not sql :
				continue

			argc = sql.count( "?" )
			argv = [ password for i in range( argc ) ]
			self.creator.conn.execute( sql , * argv )

			self.event( "progress" , onAction = lambda fn : fn( processed , total ) , ** kwargs )

		self.creator.conn.commit( )
		self.creator.password.change_password( self.creator.password.password , password , password )

		self.event( "after" , onAction = lambda fn : fn( password ) , ** kwargs )

		return True