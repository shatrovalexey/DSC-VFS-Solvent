@SET PYTHONPATH=python.exe
@SET SCRYPT=C:\dev\program-sqlite3\__init__.py
@SET PASSW=%1%
@IF "%PASSW%" == "" SET /p ID="Enter new password: "
@"%PYTHONPATH%" "%SCRYPT%" action recrypt password %PASSW%
@PAUSE