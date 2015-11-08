from lib.Interface import Interface
import codecs , json , os.path , uuid , gzip

class Config( dict , Interface ) :
	def __init__( self , fileName , charset = 'utf-8' ) :
		self.fileName = fileName
		self.charset = charset
		self.config = None

		return None

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
			fh = gzip.open( self.fileName , mode = "rt" )
			self.config = json.load( fh )
			fh.close( )
		except Exception as exception :
			self.config = { }
			self.store( )

		return self.config

	def find( self , path ) :
		result = [ ]

		for key in self.config :
			if key.find( path ) :
				continue
			result.append( key )

		return result

	def store( self ) :
		fh = gzip.open( self.fileName , mode = "wt" , encoding = self.charset )
		json.dump( self.config , fh )
		fh.close( )

		return True

	def update( self ) :
		if self.store( ) :
			return self.fetch( )

		return None

	def get( self , key ) :
		if key in self.config :
			return self.config[ key ]

		return None

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
		result = os.path.realpath( path )
		result = os.path.dirname( result )

		return result

	def list2dict( self , inputList , startKey = 0 ) :
		result = dict( )
		i = startKey
		while i < len( inputList ) :
			result[ inputList[ i ] ] = inputList[ i + 1 ]
			i += 2

		return result