from lib.Interface import Interface

class SQLiteRow :
	def __init__( self , data , creator ) :
		self.creator = creator
		self.data = data

	def __delitem__( self , key ) :
		return self

	def __getitem__( self , key ) :
		if key not in self.data:
			return None

		result = self.data[ key ]

		return result

	def __contains__( self , key ) :
		result =  self.exists( key )

		return result

	def __setitem__( self , key , value ) :
		if self.set( value , key ) :
			return value
		return None