import sys , os
from lib.Application import Application
from lib.Config import Config

currentPath = sys.argv[ 0 ]
configFile = None
args = None

try :
	argv = sys.argv
	args = dict( argv[ 1 : ] )
	configFile = args[ "config" ]
except :
	configFile = "config/config.gz"

configFile = Application.preparePath( None , configFile )

try :
	if "action" not in args:
		raise Exception( None )

	if "path" in args:
		args[ "path" ] = os.path.abspath( args[ "path" ] )
	else :
		args[ "path" ] = os.getcwd( )

	argv = [ ]
	argv.append( args[ "action" ] )
	argv.append( args[ "path" ] )

	if "id" in args :
		argv.append( args[ "id" ] )

	if "password" in args :
		argv.append( args[ "password" ] )

	app = Application( configFile = configFile , visible = False )
	app.prepare( )
	app.ui.action( * argv )
	app.finish( )
except Exception as exception:
	app = Application( configFile = configFile )
	app.prepare( )
	app.execute( )
	app.finish( )