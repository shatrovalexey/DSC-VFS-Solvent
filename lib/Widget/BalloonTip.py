from lib.GUI import GUI
from lib.Interface import Interface
from tkinter import ttk
import tkinter as tk

class BalloonTip( GUI ) :
	def execute( self , title , message ) :
		frame_width = self.config[ "gui" ][ "balloon_tip" ][ "frame_width" ]
		frame_height = self.config[ "gui" ][ "balloon_tip" ][ "frame_height" ]

		screen_width = self.creator.master.winfo_screenwidth( )
		screen_height = self.creator.master.winfo_screenheight( )

		( frame_x , frame_y ) = ( screen_width - frame_width , screen_height - frame_height )

		self.frame = tk.Toplevel( self.creator.master , bd = 1 , relief = tk.SUNKEN )
		self.frame.update_idletasks( )
		self.frame.overrideredirect( True )
		self.frame.geometry( "%dx%d+%d+%d" % ( frame_width , frame_height , frame_x , frame_y ) )
		self.frame.bind( "<Button>" , self.destroy )

		title = tk.Label( self.frame ,
			text = title ,
			justify = tk.LEFT ,
			** self.config[ "gui" ][ "balloon_tip" ][ "title" ][ "attr" ]
		)
		message = tk.Label( self.frame ,
			text = message ,
			** self.config[ "gui" ][ "balloon_tip" ][ "message" ][ "attr" ]
		)

		title.pack( fill = tk.X )
		message.pack( fill = tk.X )

		self.timer = self.timed( target = self.destroy )

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