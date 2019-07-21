@echo off
REM -- Invoke the NuoDB Agent tool
REM (C) Copyright 2019 NuoDB, Inc.  All Rights Reserved.

java %NUODB_MANAGER_JAVA_OPTS% -jar "%~dp0..\jar\nuodbmanager.jar" %*
