from lib.Interface import Interface
import codecs , json , os.path , uuid , gzip

class Config( dict , Interface ) :
	def __init__( self , fileName , charset = 'utf-8' ) :
		self.fileName = fileName
		self.charset = charset
		self.config = None

	def __delitem__( self , key ) :
		return self.purge( key )

	def __getitem__( self , key ) :
		return self.get( key )

	def __contains__( self , key ) :
		return key in self.config

	def __setitem__( self , key , value ) :
		if self.set( value , key ) :
			return value

		return None

	def __iter__( self ) :
		for key in self.config :
			yield key

	def __copy__( self ) :
		return self.config.copy( )

	def __len__( self ) :
		return len( self.config )

	def fetch( self ) :
		try :
			with gzip.open( self.fileName , mode = "rt" ) as fh :
				self.config = json.load( fh )
				fh.close( )
		except Exception as exception :
			self.config = { }
			self.store( )

		return self.config

	def store( self ) :
		with gzip.open( self.fileName , mode = "wt" , encoding = self.charset ) as fh :
			json.dump( self.config , fh )
			fh.close( )

		return True

	def update( self ) :
		if self.store( ) :
			return self.fetch( )

		return None

	def get( self , key ) :
		if key not in self.config :
			return None
		return self.config[ key ]

	def set( self , value , key = None , store = False ) :
		if key is None :
			key = uuid.uuid4( ).hex
		self.config[ key ] = value

		if store :
			self.store( )

		return value

	def purge( self , key , store = False ) :
		if key in self.config :
			del self.config[ key ]

			if store :
				self.store( )

			return True

		return False

	def path( self , path ) :
		path = os.path.realpath( path )
		path = os.path.dirname( path )

		return path
