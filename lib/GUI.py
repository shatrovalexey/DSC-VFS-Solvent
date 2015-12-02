from lib.Interface import Interface , sys
import tkinter as tk
from tkinter import ttk

class GUI( Interface , ttk.Frame ) :
	def __init__( self , master , config , creator , visible = True ) :
		self.config = config
		self.creator = creator
		self.visible = visible
		self.master = None
		self.topFrame = None
		if self.visible :
			if master is None :
				master = tk.Tk( )

			self.master = master
			self.topFrame = ttk.Frame.__init__( self , self.master )

	def prepare( self ) :
		if self.visible :
			try :
				self.master.title( self.config[ "title" ] )
			except :
				pass
			try :
				self.master.wm_iconbitmap( bitmap = self.config[ "icon" ] )
			except :
				pass
			try :
				self.master.wm_iconwindow( self.config[ "icon" ] )
			except :
				pass
			try :
				self.pack( side = tk.BOTTOM , fill = tk.BOTH , expand = tk.YES )
			except :
				pass

		return self

	def execute( self ) :
		if self.visible :
			self.master.mainloop( )

		return self