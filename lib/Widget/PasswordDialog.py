from lib.GUI import GUI
import tkinter as tk

class PasswordDialog( GUI , tk.Toplevel ) :
	def __init__( self , * args , ** kwargs ) :
		GUI.__init__( self , * args , ** kwargs )
		tk.Toplevel.__init__( self , self.master )

		self.title( self.config[ "gui" ][ "authorization" ] )

	def prepare( self ) :
		GUI.prepare( self )

		self.password = tk.StringVar( )

		label = tk.Label( self , text = self.config[ "gui" ][ "enter_password" ] )
		entry = tk.Entry( self , show = '*' , textvariable = self.password )
		entry.bind( "<Return>" , self.execute )
		entry.bind( "<Escape>" , self.finish )
		submit = tk.Button( self , text = self.config[ "gui" ][ "ok" ] , command = self.execute )

		label.pack( side = tk.LEFT )
		entry.pack( side = tk.LEFT )
		submit.pack( side = tk.LEFT )

		entry.focus( )

		self.transient( self.master )
		self.grab_set( )
		self.creator.set( None )

		return self

	def execute( self , evt = None ) :
		password = self.password.get( )

		if self.creator.check( password ) :
			self.creator.set( password )
		else :
			tk.messagebox.showinfo( self.config[ "gui" ][ "error" ] , self.config[ "error" ][ "invalid_password" ] )

		self.finish( )

		return self

	def finish( self , evt = None ) :
		self.destroy( )

		return self