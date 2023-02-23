@echo off
set SCRIPT_PATH=%~dp0.
set SCRIPT_NAME=%~nx0
set ACTIVATE_SCRIPT=%SCRIPT_PATH%\venv\Scripts\activate.bat
set PYLAUNCHER=%WINDIR%\py.exe

if not exist "%ACTIVATE_SCRIPT%" goto noactivate
call "%ACTIVATE_SCRIPT%"
exit /b 0

:noactivate
if not exist "%PYLAUNCHER%" goto nopylauncher
set PYTHON=%PYLAUNCHER%
goto createvenv

:nopylauncher
where python.exe >nul 2>&1
if %ERRORLEVEL% equ 0 goto pythoninpath
echo %SCRIPT_NAME%: Failed to locate Python >&2
exit /b 1

:pythoninpath
set PYTHON=python.exe

:createvenv
"%PYTHON%" -m venv "%SCRIPT_PATH%/venv"
if %ERRORLEVEL% equ 0 goto activate
echo %SCRIPT_NAME%: Failed to create virtual environment >&2
exit /b 2

:activate
call "%ACTIVATE_SCRIPT%"

pip install -r "%SCRIPT_PATH%/requirements.txt"
if %ERRORLEVEL% equ 0 exit /b 0
echo %SCRIPT_NAME%: Failed to install required packages >&2
call deactivate.bat
rmdir /s /q "%SCRIPT_PATH%/venv"
exit /b 3
