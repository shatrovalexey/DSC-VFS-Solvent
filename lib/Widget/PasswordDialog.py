from lib.GUI import GUI
import tkinter as tk

class PasswordDialog( GUI ) :
	def prepare( self ) :
		GUI.prepare( self )

		self.top = tk.Toplevel( self.master )

		label = tk.Label( self.top , text = self.config[ "gui" ][ "enter_password" ] )
		label.pack( )

		self.password = tk.StringVar( )

		entry = tk.Entry( self.top , show = '*' , textvariable = self.password )
		entry.bind( "<Return>" , self.execute )
		entry.pack( )

		submit = tk.Button( self.top , text = self.config[ "gui" ][ "set" ] , command = self.execute )
		submit.pack( )

		entry.focus( )

		self.top.transient( self.master )
		self.top.grab_set( )
		# self.top.pack( )
		self.creator.set( None )

		return self

	def execute( self , evt = None ) :
		password = self.password.get( )

		if not self.creator.check( password ) :
			return False

		self.creator.set( password )
		# self.top.pack_forget( )
		self.top.destroy( )

		return True