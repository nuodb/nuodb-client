====================
NuoDB Client Package
====================

.. image:: https://dl.circleci.com/status-badge/img/gh/nuodb/nuodb-client/tree/master.svg?style=svg
        :target: https://dl.circleci.com/status-badge/redirect/gh/nuodb/nuodb-client/tree/master

.. contents::

The NuoDB Client Package bundles the latest publicly-available NuoDB_ database
client versions into a single downloadable files. The official versions of the
NuoDB Client Package files are available from the NuoDB `GitHub Releases`_
page.

You can also use this project to create packages containing customized sets
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
NuoDB database.  If you don't have a NuoDB_ database running in your
environment, refer to the NuoDB Documentation_ to guide you through the steps
to deploy a NuoDB database.

Client Package Installation
---------------------------

Unpack the tar file, or unzip the zip file which will create a
*nuodb-<package>-<ver>* directory that contains the NuoDB Client Package files.

To use the drivers you may need to configure your user applications with the
appropriate path settings to locate your NuoDB Client package install
directory at runtime.

Resources
---------

NuoDB Documentation_

Building a client package
-------------------------

To build a client package, first clone this repository and ``cd`` into it. Then,
decide on the version string you wish to use to identify this build of the client
package (e.g., ``2025.3``). Then issue this command to download all the software
included in the client package and bundle it::

  $ ./build --version 2025.3

The resulting bundle will be in the ``package`` directory::

  $ ls -1 package/*.tar.gz
  nuodb-tools-2025.3.lin-x64.tar.gz

You may optionally build multiple bundles, one for CLI tools and one
for drivers, by issuing this command::

  $ ./build --separate-bundles --version 2025.3

  $ ls -1 package/*.tar.gz
  package/nuodb-cli-tools-2025.3.lin-x64.tar.gz
  package/nuodb-drivers-2025.3.lin-x64.tar.gz

Check ``./build --help`` for more options.

License
-------

NuoDB Client is licensed under the `BSD 3-Clause License <https://github.com/nuodb/nuodb-client/blob/master/LICENSE>`_

.. _NuoDB: https://www.nuodb.com/
.. _GitHub Releases: https://github.com/nuodb/nuodb-client/releases
.. _System Requirements: https://doc.nuodb.com/nuodb/latest/deployment-models/physical-or-vmware-environments-with-nuodb-admin/system-requirements/
.. _Documentation: https://doc.nuodb.com/nuodb/latest/introduction-to-nuodb/
