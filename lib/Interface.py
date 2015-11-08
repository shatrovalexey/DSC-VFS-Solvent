import imp , sys , threading

class Interface :
	def prepare( self ) : return self
	def execute( self ) : return self
	def finish( self )  : return self
	def restart( self ) :
		if self.finish( ) :
			return self.prepare( )
		return None

	def exception( self , name , ** kwargs ) :
		error = self.config[ "error" ]
		if name in error :
			raise Exception( error[ name ].format( ** kwargs ) )
		raise Exception( error[ "no_error_message_found" ].format( name = name ) )

	def getClass( self , class_name , class_path ) :
		try :
			moduleH = imp.load_source( class_name , class_path )
			classH = getattr( moduleH , class_name , None )

			return classH
		except Exception as exception :
			return self.exception( "class_not_found" , class_name = class_name , class_path = class_path , exception = exception )

	def getObject( self , * argv , ** kwargs ) :
		classH = self.getClass( * argv )
		objectH = classH( ** kwargs )

		return objectH

	def thread( self , target , finish = None ) :
		def _( ) :
			if not target( ) :
				return False

			if finish is not None :
				finish( )

			return True

		th = threading.Thread( target = _ )
		th.start( )

		return th

	def subName( self ) :
		return sys._getframe( 1 ).f_code.co_name

	def eventName( self , eventName ) :
		return "on%s" % eventName.capitalize( )

	def fireEvent( self , eventName , * argv , ** kwargs ) :
		eventName = self.eventName( eventName )

		if eventName in kwargs :
			return kwargs[ eventName ]( * argv )

		return False

	def event( self , action , ** kwargs ) :
		try :
			action = self.eventName( action )
			if action not in kwargs :
				return False

			self.fireEvent( "action" , kwargs[ action ] , ** kwargs )

			return True
		except Exception as exception :
			self.fireEvent( "error" , exception , ** kwargs )

			return False