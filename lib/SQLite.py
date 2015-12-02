from lib.Config import Config
import sqlite3

class SQLite( Config ) :
	def __init__( self , creator, filename = None , charset = 'utf-8' ) :
		self.creator = creator
		self.fileName = filename
		self.charset = charset
		self.config = None

		return None

	def row( self , row ) :
		if row is None :
			return None

		result = dict( )
		i = 0

		for item in self.dbh.description :
			key = item[ 0 ]
			result[ key ] = row[ i ]
			i += 1

		return result

	def prepare( self , database , fetch = True ) :
		self.conn = sqlite3.connect( database , detect_types = sqlite3.PARSE_COLNAMES )

		encryptor = self.creator.controller.encryptor( )
		decryptor = self.creator.controller.decryptor( )
		recryptor = self.creator.controller.recryptor( )

		self.conn.create_function( "encrypt" , 1 , encryptor )
		self.conn.create_function( "decrypt" , 1 , decryptor )
		self.conn.create_function( "recrypt" , 2 , recryptor )

		self.dbh = self.conn.cursor( )
		if fetch is True :
			self.fetch( )
		self.execute( self.creator.config[ "db" ][ "sql" ][ "prepare" ] )

		return self

	def executescript( self , script , * args ) :
		return self.dbh.executescript( script )

	def execute( self , sql , * args ) :
		return self.dbh.execute( sql , args )

	def fetchcol( self , sql , * args , ** kwargs ) :
		rows = self.execute( sql , * args )
		result = [ ]
		colId = 0

		if "col" in kwargs :
			colId = kwargs[ "col" ]

		for row in rows :
			if "limit" in kwargs :
				if kwargs[ "limit" ] <= 0 :
					break
				kwargs[ "limit" ] -= 1

			col = row[ colId ]
			result.append( col )

		return result

	def fetchall( self , sql , * args ) :
		for row in self.execute( sql , * args ) :
			yield self.row( row )
		else :
			return None

	def fetchrow( self , sql , * args ) :
		for row in self.fetchall( sql , * args ) :
			return row
		else :
			return None

	def fetchone( self , sql , * args ) :
		for col in self.fetchcol( sql , limit = 1 , * args ) :
			return col
		else :
			return None

	def commit( self ) :
		return self.conn.commit( )

	def finish( self ) :
		try :
			self.conn.commit( )
			self.conn.close( )
		except :
			return False
		return True

	def rollback( self ) :
		result = self.conn.rollback( )

		return result

	def __del__( self , commit = False ) :
		try :
			if commit is True :
				self.conn.commit( )
			self.conn.close( )
		except :
			return False
		return True