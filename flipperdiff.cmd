@echo off
set SCRIPT_PATH=%~dp0.
call "%SCRIPT_PATH%\activate.cmd"
python.exe "%SCRIPT_PATH%/flipperdiff.py" %*
set RESULT=%ERRORLEVEL%
call deactivate.bat
exit /b %RESULT%
