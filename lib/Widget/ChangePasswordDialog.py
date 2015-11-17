from lib.GUI import GUI
import tkinter as tk

class ChangePasswordDialog( GUI ) :
	def prepare( self ) :
		GUI.prepare( self )

		self.top = tk.Toplevel( self.master )

		self.password_old = tk.StringVar( )
		self.password_new = tk.StringVar( )
		self.password_new2 = tk.StringVar( )

		label = tk.Label( self.top , text = self.config[ "gui" ][ "enter_password_old" ] )
		label.grid( row = 1 , column = 1 )

		entry = tk.Entry( self.top , show = '*' , textvariable = self.password_old )
		entry.grid( row = 1 , column = 2 )
		entry.focus( )

		label = tk.Label( self.top , text = self.config[ "gui" ][ "enter_password_new" ] )
		label.grid( row = 2 , column = 1 )

		entry = tk.Entry( self.top , show = '*' , textvariable = self.password_new )
		entry.grid( row = 2 , column = 2 )

		label = tk.Label( self.top , text = self.config[ "gui" ][ "enter_password_new2" ] )
		label.grid( row = 3 , column = 1 )

		entry = tk.Entry( self.top , show = '*' , textvariable = self.password_new2 )
		entry.grid( row = 3 , column = 2 )

		submit = tk.Button( self.top , text = self.config[ "gui" ][ "ok" ] , command = self.execute )
		submit.grid( row = 4 , column = 2 )

		self.top.transient( self.master )
		self.top.grab_set( )
		# self.top.pack( )
		self.creator.set( None )

		return self

	def execute( self , evt = None ) :
		password_old = self.password_old.get( )
		password_new = self.password_new.get( )
		password_new2 = self.password_new2.get( )

		self.creator.set( password_new )
		self.top.pack_forget( )
		self.top.destroy( )

		return True