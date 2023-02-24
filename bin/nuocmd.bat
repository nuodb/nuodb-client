@echo off
REM -- Invoke the NuoDB Admin command-line tool
REM (C) Copyright 2019-2023 NuoDB, Inc.  All Rights Reserved.

setlocal

if "%NUOPYTHON%" == "" goto trypyvar
set "pycmd=%NUOPYTHON%"
goto getpkg

:trypyvar
if "%PYTHON%" == "" goto trypy3
set "pycmd=%PYTHON%"
goto getpkg

:trypy3
where /q python3
if ERRORLEVEL 1 goto trypy
set "pycmd=python3"
goto getpkg

:trypy
where /q python
if ERRORLEVEL 1 (
    echo No Python interpreter found: please install and update PATH
    exit /b 1
)
set "pycmd=python"

:getpkg
set "pkgdir=etc\python\site-packages"
set "cli=pynuoadmin\nuodb_cli.py"

if "%NUOCLIENT_HOME%" == "" goto lochome
set "pkghome=%NUOCLIENT_HOME%\%pkgdir%"
if exist "%pkghome%\%cli%" goto run

:lochome
set "pkghome=%~dp0..\%pkgdir%"
if not exist "%pkghome%\%cli%" (
    echo Cannot locate pynuoadmin installation
    exit /b 1
)

:run
set "PYTHONPATH=%pkghome%;%PYTHONPATH%"
"%pycmd%" -m pynuoadmin.nuodb_cli %*
