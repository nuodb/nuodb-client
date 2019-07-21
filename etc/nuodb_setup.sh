# (C) Copyright NuoDB Inc. 2019  All Rights Reserved.
#
# This file should be _sourced_ by other scripts.

NUODB_PKG=nuodb-client

_nuodb_setup_CMD=${0##*/}
_nuodb_setup_DIR=$(cd "${0%$_nuodb_setup_CMD}." && pwd)
: ${NUOCLIENT_HOME:="${_nuodb_setup_DIR%/*}"}
unset _nuodb_setup_CMD _nuodb_setup_DIR

# We use the XDG Base Directory Specification locations
# https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

: ${XDG_CONFIG_HOME:="$HOME/.config"}
: ${XDG_DATA_HOME:="$HOME/.local/share"}

: ${NUODB_CFGDIR:="$XDG_CONFIG_HOME/$NUODB_PKG"}
: ${NUODB_VARDIR:="$XDG_DATA_HOME/$NUODB_PKG/data"}
: ${NUODB_LOGDIR:="$XDG_DATA_HOME/$NUODB_PKG/log"}
: ${NUODB_CRASHDIR:="$NUODB_LOGDIR/crash"}

[ -n "$XDG_RUNTIME_DIR" ] \
    && : ${NUODB_RUNDIR:="$XDG_RUNTIME_DIR/$NUODB_PKG"} \
    || : ${NUODB_RUNDIR:="$XDG_DATA_HOME/$NUODB_PKG/run"}

for d in "$NUODB_CFGDIR" "$NUODB_VARDIR" "$NUODB_LOGDIR" "$NUODB_RUNDIR" "$NUODB_CRASHDIR"; do
    [ -d "$d" ] || { mkdir -p "${d%/*}" 2>/dev/null && mkdir -m 0700 "$d"; }
done
