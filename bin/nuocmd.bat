@echo off
REM -- Invoke the NuoDB Admin command-line tool
REM (C) Copyright 2019 NuoDB, Inc.  All Rights Reserved.

set "PYTHONPATH=%~dp0..\python\site-packages"
python -m nuodb_cli.py %*
