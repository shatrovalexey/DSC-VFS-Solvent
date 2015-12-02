from lib.GUI import GUI
from lib.Interface import Interface
from tkinter import ttk
import tkinter as tk

class X( GUI , ttk.Frame ) :
	def __init__( self ) :
		Interface.__init__( self )
		self.master = tk.Tk( )
		self.top = ttk.Frame.__init__( self , self.master )
		self.frame = None
		self.timer = None

	def prepare( self ) :
		button = ttk.Button( self.master , text = "Test" , command = self.onCmdButtonClick )
		button.pack( )

		self.master.mainloop( )

		return self

	def onCmdButtonClick( self , evt = None ) :
		self.execute( title = "Title" , message = "LKkldsf df dfs J  FJDJF D ;d ;fF ESSD J  FJDJF D ;d ;fF ESSD " )

		return self

	def execute( self , title , message ) :
		( frame_width , frame_height ) = ( 300 , 100 )

		self.frame = tk.Toplevel( self.master , bd = 1 , relief = tk.SUNKEN )

		title = tk.Label( self.frame ,
			text = title ,
			bg = "white" ,
			font = "Helvetica 8 bold" ,
			justify = tk.LEFT
		)
		message = tk.Label( self.frame ,
			text = message ,
			bg = "white" ,
			font = "Helvetica 8" ,
			wraplength = frame_width * 0.9
		)

		title.pack( fill = tk.X )
		message.pack( fill = tk.X )

		screen_width = self.master.winfo_screenwidth( )
		screen_height = self.master.winfo_screenheight( )

		( frame_x , frame_y ) = ( screen_width - frame_width , screen_height - frame_height )

		self.frame.overrideredirect( True )
		self.frame.geometry( "%dx%d+%d+%d" % ( frame_width , frame_height , frame_x , frame_y ) )
		self.frame.bind( "<Button>" , self.destroy )
		self.timer = self.timed( target = lambda: self.frame.destroy( ) )

	def destroy( self , evt = None ) :
		try :
			self.frame.destroy( )
		except :
			pass
		try :
			self.timer.cancel( )
		except :
			pass

	def __del__( self ) :
		self.destroy( )

x = X( )
x.prepare( )