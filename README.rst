====================
NuoDB Client Package
====================

.. image:: https://dl.circleci.com/status-badge/img/gh/nuodb/nuodb-client/tree/master.svg?style=svg
        :target: https://dl.circleci.com/status-badge/redirect/gh/nuodb/nuodb-client/tree/master

.. contents::

The NuoDB Client Package bundles the latest publicly available NuoDB_ database
client versions into a single downloadable file. Separate packages for each
components are also available. The official versions of the NuoDB Client Package
files are available from the NuoDB `GitHub Releases`_
page.

This project can also be used to create packages containing customized sets
of NuoDB Client individual packages.

Requirements
------------

Each client in the NuoDB Client Package will have different requirements when
connecting to a NuoDB database. The System requirements for running the NuoDB
database are found in the NuoDB documentation `System Requirements`_ page.

+--------------------+----------------------------------------+
|Utility             | Requirements                           |
+====================+========================================+
|nuocmd / pynuoadmin |Python 3.6 or later                     |
+--------------------+----------------------------------------+
|nuosql              |GNU/Linux or Windows                    |
+--------------------+----------------------------------------+
|nuoloader           |GNU/Linux or Windows                    |
+--------------------+----------------------------------------+
|nuodump             |GNU/Linux or Windows                    |
+--------------------+----------------------------------------+
|migrator (dep)      |Java 8 or 11                            |
+--------------------+----------------------------------------+

Also included are SQL drivers:

+------------------+---------------------+
|Driver            | Requirements        |
+==================+=====================+
|C                 |GNU/Linux or Windows |
+------------------+---------------------+
|C++               |GNU/Linux or Windows |
+------------------+---------------------+
|ODBC              |GNU/Linux or Windows |
+------------------+---------------------+
|JDBC              |Java 8 or 11         |
+------------------+---------------------+
|Hibernate5        |Java 8 or 11         |
+------------------+---------------------+
|Hibernate6        |Java 11 or 17        |
+------------------+---------------------+
|Python            |Python 3.6 or later  |
+------------------+---------------------+

The use of the NuoDB clients and the drivers in this package require a running
NuoDB database.  If a NuoDB_ database is not running in the
environment, refer to the NuoDB Documentation_ for steps
to deploy a NuoDB database.

Client Package Installation
---------------------------

Unpack the tar file, or unzip the zip file which will create a
*nuodb-<package>-<ver>* directory that contains the NuoDB Client Package files.

To use the drivers, user applications may need to be configured with the
appropriate path settings to locate the NuoDB Client package install
directory at runtime.

Resources
---------

NuoDB Documentation_

Building a client package
-------------------------

To build a client package, first clone this repository and ``cd`` into it. Then,
decide on the version string to use to identify this build of the client
package (e.g., ``2025.3``).

By default, a single package is generated that includes all the drivers and
tools. To build this package, issue this command::

  $ ./build --version 2025.3

The resulting bundle will be in the ``package`` directory::

  $ ls -1 package/*.tar.gz
  package/nuodb-client-2025.3.lin-x64.tar.gz

Optionally, multiple bundles can be built, one for each separate component type.
The following command will generate separate packages for the C, C++, and ODBC
drivers, and for the SQL tools::

  $ ./build --separate-bundles --version 2025.3

  $ ls -1 package/*.tar.gz
  package/nuodb-c-driver-2025.3.lin-x64.tar.gz
  package/nuodb-cpp-driver-2025.3.lin-x64.tar.gz
  package/nuodb-odbc-driver-2025.3.lin-x64.tar.gz
  package/nuodb-sql-tools-2025.3.lin-x64.tar.gz

Note that some components are not yet assigned to a separate bundle, and will
not be included in any of the packages generated with ``--separate-bundles``.
These components are:

- JDBC driver
- Hibernate drivers
- pynuodb driver

These components are included in the default ``nuodb-client`` package.

Check ``./build --help`` for more options.

License
-------

NuoDB Client is licensed under the `BSD 3-Clause License <https://github.com/nuodb/nuodb-client/blob/master/LICENSE>`_

.. _NuoDB: https://www.nuodb.com/
.. _GitHub Releases: https://github.com/nuodb/nuodb-client/releases
.. _System Requirements: https://doc.nuodb.com/nuodb/latest/deployment-models/physical-or-vmware-environments-with-nuodb-admin/system-requirements/
.. _Documentation: https://doc.nuodb.com/nuodb/latest/introduction-to-nuodb/
