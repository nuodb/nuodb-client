:: (C) Copyright NuoDB Inc. 2019  All Rights Reserved.
::
:: This file should be _called_ by other scripts, after setlocal

set "NUODB_PKG=nuodb-client"

if not "%NUOCLIENT_HOME%" == "" goto _run
pushd %~dp0..
set "NUOCLIENT_HOME=%CD%"
popd
:_run

set "NUODB_CFGDIR=%NUOCLIENT_HOME%\var\etc"
set "NUODB_VARDIR=%NUOCLIENT_HOME%\var\opt"
set "NUODB_LOGDIR=%NUOCLIENT_HOME%\var\log"
set "NUODB_RUNDIR=%NUOCLIENT_HOME%\var\run"
set "NUODB_CRASHDIR=%NUODB_LOGDIR%\crash"
if not exist "%NUODB_CFGDIR%" mkdir "%NUODB_CFGDIR%"
if not exist "%NUODB_VARDIR%" mkdir "%NUODB_VARDIR%"
if not exist "%NUODB_LOGDIR%" mkdir "%NUODB_LOGDIR%"
if not exist "%NUODB_RUNDIR%" mkdir "%NUODB_RUNDIR%"
if not exist "%NUODB_CRASHDIR%" mkdir "%NUODB_CRASHDIR%"

exit /b 0
