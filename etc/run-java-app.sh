#!/bin/sh
#
# Start a Java application
# (C) Copyright NuoDB, Inc. 2013-2014  All Rights Reserved
#
# Start either a simple Java command, or a Java daemon.
# Exits with non-0 on failure
# If a daemon and it successfully starts:
# - Write the PID to <pidfile>
# - Writes logging-type output to stdout, error messages to stderr

JAVA_MINVER=8
JAVA_OLDVER=7

# Unfortunately, ksh93 defines builtin aliases even when run non-interactively.
unalias -a

die   () { echo "$*" 1>&2; exit 1; }
info  () { : no-op ; }

usage () {
    echo "usage: $0 <jarfile> <title> [-- <args...>]]"
    exit 1
}

PATH=$PATH:/sbin:/usr/sbin:/bin:/usr/bin

# The first arg is always a jar file, and it must exist
# The second argument is a title
[ -n "$1" ] && [ -n "$2" ] || usage
jar="$1"
title="$2"
shift 2

[ "$1" = -- ] && shift

# Find the installation directory.
CMD=${0##*/}
DIR=`cd "${0%$CMD}." && pwd`

setup () {
    # Find the setup file
    _home="$NUOCLIENT_HOME"
    [ -z "$_home" ] && [ -f "${DIR%/*}"/etc/nuodb_setup.sh ] && _home="${DIR%/*}"

    [ -n "$_home" ] && [ -f "$_home"/etc/nuodb_setup.sh ] \
        && . "$_home"/etc/nuodb_setup.sh

    # Load the jvm-options file
    [ -n "$NUODB_CFGDIR" ] && [ -f "$NUODB_CFGDIR"/jvm-options ] \
        && . "$NUODB_CFGDIR"/jvm-options

    # Set Java options
    [ -z "$NUODB_JAVA_OPTS" ] && [ -n "$NUODB_OPTSVAR" ] \
        && eval NUODB_JAVA_OPTS="\$$NUODB_OPTSVAR" 2>/dev/null

    unset NUODB_OPTSVAR

    case $jar in
        (/*) : do nothing ;;
        (*)  jar="${_home:+$_home/}$jar" ;;
    esac
}

# Finds a sufficiently new Java.
# Sets $JAVA to the path, or dies if none available.

find_java () {
    # If JAVA_HOME is set, use that.
    if [ -n "$JAVA_HOME" ]; then
        JAVA="$JAVA_HOME/bin/java"
        check_java_version "$JAVA" && return

        # Not good enough.
        JAVA=
    fi

    case $(uname -s) in
        (Darwin) find_java_osx ;;
        (*)      find_java_base ;;
    esac
    [ -n "$JAVA" ] || die "$title requires Java $JAVA_MINVER or later."
}

find_java_osx () {
    # On OS X, there's a utility to find a given version.
    jhome=$(/usr/libexec/java_home -v "1.$JAVA_MINVER" 2>/dev/null)

    # If we don't find a sufficient version fall back to the standard search.
    check_java_version "$jhome/bin/java" \
        && JAVA="$jhome/bin/java" \
        || find_java_base
}

findall () {
    (
        IFS=:
        for p in $PATH; do
            [ -x "$p/$1" ] && echo "$p/$1"
        done
    )
}

find_java_base () {
    # Use a standard path search algorithm, and look in some common places
    # that JREs are stashed.
    JAVA=$( (findall java;
             ls -1 /usr/lib/jvm/*/bin/java /usr/java/*/bin/java) 2>/dev/null \
              | while read java; do
                    # Check for compatible java version
                    check_java_version "$java" || continue
                    echo "$java"
                    break
                 done)
}

check_java_version () {
    JAVAVERSION=$("$1" -version 2>&1 | sed -n 's/.* version[^"]*"\([^"]*\).*/\1/p')
    case $JAVAVERSION in
        (''|0*|1.[0-$JAVA_OLDVER]*) return 1 ;;
        (*) return 0 ;;
    esac
}

# --------------------------------------------------
# This starts a Java application directly.

setup
find_java
exec "$JAVA" $NUODB_JAVA_OPTS -jar "$jar" "$@" || exit 1
