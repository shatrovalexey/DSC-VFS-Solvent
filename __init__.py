import sys
import os.path
from lib.Application import Application
from lib.Config import Config

currentPath = sys.argv[ 0 ]
configFile = None
args = None

try :
	args = Config.list2dict( None , sys.argv , startKey = 1 )
	configFile = args[ "config" ]
except :
	configFile = "config/config.gz"

configFile = Application.preparePath( None , configFile )

try :
	if "action" not in args:
		raise Exception( None )

	if "path" not in args:
		args[ "path" ] = os.getcwd( )
	else :
		args[ "path" ] = os.path.abspath( args[ "path" ] )

	argv = []
	argv.append( args[ "action" ] )
	argv.append( args[ "path" ] )

	if "id" in args :
		argv.append( args[ "id" ] )

	app = Application( configFile = configFile , visible = False )
	app.prepare( )
	app.ui.action( * argv )
	app.finish( )

except Exception as exception:
	app = Application( configFile = configFile )
	app.prepare( )
	app.execute( )