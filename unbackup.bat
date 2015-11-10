@SET PYTHONPATH=python.exe
@SET SCRYPT=C:\dev\program-sqlite3\__init__.py
@SET ID=%1%
@IF "%ID%" == "" SET /p ID="Enter file id: "
@"%PYTHONPATH%" "%SCRYPT%" action unbackup id "%ID%"
@PAUSE