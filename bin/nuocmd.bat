@echo off
REM -- Invoke the NuoDB Admin command-line tool
REM (C) Copyright 2019-2021 NuoDB, Inc.  All Rights Reserved.

set "PYTHONPATH=%~dp0..\etc\python\site-packages"
python -m pynuoadmin.nuodb_cli %*
