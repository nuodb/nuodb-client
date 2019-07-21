@echo off
REM -- Invoke the NuoDB Admin command-line tool
REM (C) Copyright 2019 NuoDB, Inc.  All Rights Reserved.

python "%~dp0..\python\pynuoadmin\nuodb_cli.py" %*
