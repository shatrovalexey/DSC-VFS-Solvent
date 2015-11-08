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
		self.dbh = self.conn.cursor( )
		if fetch is True :
			self.fetch( )
		self.execute( self.creator.config[ "db" ][ "sql" ][ "prepare" ] )

		return self

	def executescript( self , script , * args ) :
		result = self.dbh.executescript( script )

		return result

	def execute( self , sql , * args ) :
		result = self.dbh.execute( sql , args )

		return result

	def fetchcol( self , sql , * args ) :
		self.execute( sql , * args )
		rows = self.dbh.fetchall( )

		if rows is None :
			return None

		result = [ ]

		for row in rows :
			col = row[ 0 ]
			result.append( col )

		return result

	def fetchall( self , sql , * args ) :
		self.execute( sql , * args )
		while True :
			row = self.dbh.fetchone( )
			if row is None :
				break

			result = self.row( row )

			yield result

	def fetchrow( self , sql , * args ) :
		rows = self.fetchall( sql , * args )

		if rows is None :
			return None

		for result in rows :
			return result

		return None

	def fetchone( self , sql , * args ) :
		self.execute( sql , * args )
		row = self.dbh.fetchone( )

		if row is None :
			return None

		result = row[ 0 ]

		return result

	def commit( self ) :
		result = self.conn.commit( )

		return result

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