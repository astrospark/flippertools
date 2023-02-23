@echo off
set SCRIPT_PATH=%~dp0.
call "%SCRIPT_PATH%\venv\Scripts\activate.bat"
python.exe "%SCRIPT_PATH%/flipper2svg.py" %*
set RESULT=%ERRORLEVEL%
call deactivate.bat
exit /b %RESULT%
