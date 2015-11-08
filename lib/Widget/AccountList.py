from lib.GUI import *
import tkinter.filedialog

class AccountList( GUI ) :
	def prepare( self ) :
		GUI.prepare( self )

		accountBox = ttk.LabelFrame( self.master , text = self.config[ "gui" ][ "accountList" ] )

		self.heading = self.config[ "gui" ][ "accountlist" ][ "heading" ]
		self.heading_keys = sorted( self.heading.keys( ) )
		self.hide_control = self.config[ "gui" ][ "hide_control" ]

		self.accountList = ttk.Treeview(
			accountBox ,
			columns			= self.heading_keys ,
			selectmode		= "browse" ,
			displaycolumns	= [ key for key in self.heading_keys if key not in self.hide_control ] ,
			show			= "headings"
		)

		for key in self.heading_keys :
			self.accountList.column( key , width = self.config[ "gui" ][ "column_width" ] )
			self.accountList.heading( key , text = self.heading[ key ] )

		for key in self.hide_control :
			try :
				self.accountList.column( key , width = 0 )
			except :
				pass

		self.accountList.column( "#0" , width = 0 )

		self.accountList.pack( fill = tk.BOTH , expand = tk.YES )

		accountEditorBox = ttk.LabelFrame( self.master , text = self.config[ "gui" ][ "accountEditor" ] )

		self.accountDriverListVar = tk.StringVar( )

		accountEditBox = ttk.Frame( accountEditorBox )

		box = ttk.Frame( accountEditBox )
		label = ttk.Label( box , text = self.config[ "gui" ][ "accountlist" ][ "heading" ][ "driver" ] )
		self.accountDriverList = ttk.OptionMenu(
			box ,
			self.accountDriverListVar ,
			self.config[ "gui" ][ "select" ] ,
			* self.creator.creator.acc_driver.action( "fetch_name" , None , None , "fetchcol" )
			# * self.config[ "driver" ]
		)
		label.pack( side = tk.LEFT )
		self.accountDriverList.pack( side = tk.LEFT , expand = tk.YES , fill = tk.X )
		box.pack( side = tk.TOP , expand = tk.YES , fill = tk.X )

		minWidth = 0
		for key in self.heading_keys[ :: -1 ] :
			item = self.heading[ key ]
			currentWidth = len( item )
			if currentWidth > minWidth :
				minWidth = currentWidth

		self.accountEntry = {
			"driver": self.accountDriverListVar
		}
		for key in self.heading_keys[ :: -1 ] :
			if key in self.accountEntry :
				continue

			box = ttk.Frame( accountEditBox )
			label = ttk.Label( box , text = self.heading[ key ] , width = minWidth + 1 )
			entry = ttk.Entry(
				box ,
				validate = "all" ,
				validatecommand = ( self.register( self.onCmdTextValidate ) , "%s" , "%P" )
			)

			self.accountEntry[ key ] = entry

			label.pack( side = tk.LEFT )
			entry.pack( side = tk.LEFT , expand = tk.YES , fill = tk.X )
			box.pack( side = tk.BOTTOM , expand = tk.YES , fill = tk.X )

			if key in self.hide_control :
				box.pack_forget( )

		accountToolbar = ttk.Frame( accountEditorBox )

		button_items = self.config[ "gui" ][ "accountlist" ][ "button" ]
		button_keys = sorted( button_items.keys( ) )
		for key in button_keys :
			item = button_items[ key ]
			# image = tk.BitmapImage( file = self.config[ "gui" ][ "icon" ][ item[ "image" ] ] )
			button = ttk.Button(
				accountToolbar ,
				# image = image ,
				text = self.config[ "gui" ][ item[ "label" ] ] ,
				command = self.__getattribute__( item[ "command" ] ) ,
			)
			button.pack( side = tk.RIGHT , fill = tk.BOTH , expand = tk.YES )

		accountEditBox.pack( side = tk.TOP , fill = tk.BOTH )
		accountToolbar.pack( side = tk.BOTTOM , fill = tk.BOTH )

		accountEditorBox.pack( side = tk.LEFT , fill = tk.BOTH )
		accountBox.pack( side = tk.RIGHT , fill = tk.BOTH , expand = tk.YES )

		self.accountList.bind( "<<TreeviewSelect>>" , self.onCmdAccountListSelect )
		self.configure( width = self.config[ "gui" ][ "accountlist" ][ "width" ] )

		self.accountEntry[ "password" ].configure( show = self.config[ "passwordChar" ] )
		self.accountEntry[ "port" ].configure( validatecommand = ( self.register( self.onCmdPortValidate ) , "%s" , "%P" ) )

		self.update( )

		return self

	def update( self ) :
		for item in self.accountList.get_children( ) :
			self.accountList.delete( item )

		for account in self.creator.creator.acc_item.action( "all" , None , None , "fetchall" ) :
			self.accountList.insert(
				"" ,
				tk.END ,
				values = [ account[ key ] for key in self.heading_keys ] ,
				tags = account[ "id" ]
			)

		self.onCmdAccountEmpty( )

		return self

	def onCmdTextValidate( self , previous , current ) :
		if not len( current ) :
			return True

		if len( current ) > self.config[ "gui" ][ "accountlist" ][ "validate" ][ "textMaxLength" ] :
			return False

		return True

	def onCmdPortValidate( self , previous , current ) :
		if not self.onCmdTextValidate( previous , current ) :
			return False

		if not len( current ) :
			return True

		if not current.isdigit( ) :
			return False

		if len( current ) > self.config[ "gui" ][ "accountlist" ][ "validate" ][ "portMaxLength" ] :
			return False

		return True

	def onCmdAccountEmpty( self ) :
		for key in self.heading_keys :
			if key == "driver" :
				self.accountDriverListVar.set( "" )
			else :
				self.accountEntry[ key ].delete( 0 , tk.END )

		return self

	def onCmdAccountAdd( self , account_id = None ) :
		account_id = self.creator.creator.acc_item.action( "create" )

		if account_id is None :
			return False

		self.update( )

		return True

	def onCmdAccountSet( self ) :
		account_id , item = self.currentAccount( )
		config = dict( )

		for key in self.heading_keys :
			if key in self.hide_control :
				continue

			if key not in self.accountEntry :
				continue

			config[ key ] = self.accountEntry[ key ].get( )

		acc_driver = self.creator.creator.acc_driver
		config[ "driver_id" ] = acc_driver.action( "fetch_by_name" , None , config[ "driver" ] , "fetchone" )
		self.creator.creator.acc_item.action( "update" , config , self.accountEntry[ "id" ].get( ) )

		self.update( )

		return True

	def onCmdAccountDel( self ) :
		try :
			account_id , item = self.currentAccount( )
			del self.creator.creator.acc_item[ account_id ]
			self.update( )
		except Exception as exception:
			print( exception )

			return False
		return True

	def onCmdAccountListSelect( self , evt ) :
		account_id , item = self.currentAccount( )
		for key in self.heading_keys :
			if key == "driver_id" :
				driverName = self.creator.creator.acc_driver[ item[ key ] ][ "name" ]
				self.accountDriverListVar.set( driverName )
				self.accountDriverList.value = driverName

				continue

			if key not in item :
				continue

			self.accountEntry[ key ].delete( 0 , tk.END )
			self.accountEntry[ key ].insert( 0 , item[ key ] )

		return self


	def currentAccount( self ) :
		try :
			current = self.accountList.selection( )
			account = self.accountList.item( current[ 0 ] )
			account_id = account[ "tags" ][ 0 ]
			item = self.creator.creator.acc_item[ account_id ]

			return ( account_id , item )
		except Exception as exception :
			self.exception( "no_account_selected" )

		return None