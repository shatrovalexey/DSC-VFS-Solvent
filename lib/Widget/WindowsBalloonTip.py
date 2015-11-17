from lib.GUI import GUI
from win32gui import *
from lib.Interface import Interface
import win32con
import sys, os
import struct
import time
import threading

class WindowsBalloonTip( GUI ) :
	def prepare( self ) :
		wc = WNDCLASS( )
		self.hinst = wc.hInstance = GetModuleHandle( None )
		wc.lpszClassName = self.config[ "name" ]
		wc.lpfnWndProc = {
			win32con.WM_DESTROY: self.finish ,
		}
		self.classAtom = RegisterClass( wc )
		self.style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
		self.flags = NIF_ICON | NIF_MESSAGE | NIF_TIP

		try :
			iconPath = self.config[ "icon" ]
			programPath = sys.path[ 0 ]
			joinedPath = os.path.join( programPath , iconPath )
			iconPathName = os.path.abspath( joinedPath )
			iconFlags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE | win32con.LR_DEFAULTCOLOR
			self.hicon = LoadImage( self.hinst , iconPathName , win32con.IMAGE_ICON , 0 , 0 , iconFlags )
		except :
			self.hicon = LoadIcon( 0 , win32con.IDI_APPLICATION )

		self.createWindowArgs = ( self.classAtom , "Taskbar" , self.style , 0 , 0 , win32con.CW_USEDEFAULT , win32con.CW_USEDEFAULT , 0 , 0 , self.hinst , None )

		return self

	def execute( self , title = None , message = None ) :
		self.hwnd = CreateWindow( * self.createWindowArgs )
		UpdateWindow( self.hwnd )
		Shell_NotifyIcon( NIM_ADD , (
			self.hwnd , 0 , self.flags , win32con.WM_USER + 20 , self.hicon , "tooltip"
		) )
		Shell_NotifyIcon( NIM_MODIFY , (
			self.hwnd , 0 , NIF_INFO , win32con.WM_USER + 20 , self.hicon , "tooltip" , message , 200 , title # , self.hicon
		) )

		return self.finish( )

	def finish( self , * args ) :
		# return self.thread( target = self.destroy )

		pass

	def destroy( self , immidiate = False , ** kwargs ) :
		if not immidiate :
			time.sleep( self.config[ "balloon_timeout" ] )

		try :
			DestroyWindow( self.hwnd )
			Shell_NotifyIcon( NIM_DELETE , ( self.hwnd , 0 ) )
			PostQuitMessage( 0 )
		except :
			pass

		return self