from lib.SQLite import SQLite
from lib.Config import Config

class SQLiteConsumer( Config ) :
	def __init__( self , entity , creator ) :
		self.creator = creator
		self.queryes = self.creator[ entity ]

	def prepare( self ) :
		self.dbh = self.creator.dbh

		return self

	def action( self , name , value = None , key = None , fetch = None ) :
		if name not in self.queryes :
			return None

		data = self.queryes[ name ]

		if type( data ) == str :
			sql = data
			keys = [ ]
		else :
			sql = data[ "sql" ]
			keys = data[ "args" ]

		if value is None :
			args = [ ]
		else :
			args = [ value[ k ] for k in keys ]

		if key is not None :
			args.append( key )

		if fetch is None :
			self.creator.execute( sql , * args )
			self.creator.commit( )
			result = self.creator.dbh.lastrowid
		else :
			sub = getattr( self.creator , fetch )
			result = sub( sql , * args )

		return result

	def purge( self , key ) :
		result = self.creator.execute( self.queryes[ "purge" ] , key )
		self.creator.commit( )

		return result

	def get( self , key ) :
		result = self.creator.fetchrow( self.queryes[ "fetch" ] , key )

		return result

	def append( self , value ) :
		rowid = self.action( name = "store" , value = value )
		result = self.creator.fetchone( self.queryes[ "lastid" ] , rowid )

		return result

	def set( self , value , key ) :
		result = self.action( name = "update" , value = value , key = key )

		return result

	def exists( self , key ) :
		result = self.creator.fetchone( self.queryes[ "exists" ] , key )

		if result :
			return True

		return False

	def __add__( self , value ) :
		result = self.append( value )

		return result

	def __delitem__( self , key ) :
		result = self.purge( key )

		return result

	def __getitem__( self , key ) :
		result = self.get( key )

		return result

	def __contains__( self , key ) :
		result =  self.exists( key )

		return result

	def __setitem__( self , key , value ) :
		if self.set( value , key ) :
			return value
		return None

	def next( self ) :
		row = self.creator.dbh.fetchone( )
		result = self.creator.row( row )

		return result

	def keys( self ) :
		result = self.creator.fetchcol( self.queryes[ "keys" ] )

		return result

	def __iter__( self ) :
		result = self.keys( )

		return iter( result )

	def __len__( self ) :
		result = self.creator.fetchone( self.queryes[ "count" ] )

		return result