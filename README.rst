====================
NuoDB Client Package
====================

.. image:: https://travis-ci.org/nuodb/nuodb-client.svg?branch=master
    :target: https://travis-ci.org/nuodb/nuodb-client

.. contents::

The NuoDB Client Package bundles the latest publicly-available NuoDB_ database
client versions into a single downloadable file. The official versions of the
NuoDB Client Package file are available from the NuoDB `GitHub Releases`_
page.

You can also use this project to create a package containing customized sets
of NuoDB Client packages.

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
|nuodb-migrator      |Java 8 or 11                            |
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
|Python            |Python 3.6 or later  |
+------------------+---------------------+

The use of the NuoDB clients and the drivers in this package require a running
NuoDB database.  If you don't have a NuoDB_ database running in your
environment, refer to the NuoDB Documentation_ to guide you through the steps
to deploy a NuoDB database.

Client Package Installation
---------------------------

Unpack the tar file, or unzip the zip file which will create a
*nuodb-client-<ver>* directory that contains the NuoDB Client Package files.

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
package (e.g., ``2023.1``). Then issue this command to download all the software
included in the client package and bundle it::

  $ ./build --version 2023.1

The resulting bundle will be in the ``package`` directory::

  $ ls -1 package/*.tar.gz
  nuodb-tools-2023.1.lin-x64.tar.gz

You may optionally build multiple bundles, one for CLI tools and one
for drivers, by issuing this command::

  $ ./build --separate-bundles --version 2023.1

  $ ls -1 package/*.tar.gz
  package/nuodb-cli-tools-2023.1.lin-x64.tar.gz
  package/nuodb-drivers-2023.1.lin-x64.tar.gz

Check ``./build --help`` for more options.

License
-------

NuoDB Client is licensed under the `BSD 3-Clause License <https://github.com/nuodb/nuodb-client/blob/master/LICENSE>`_

.. _NuoDB: https://www.nuodb.com/
.. _GitHub Releases: https://github.com/nuodb/nuodb-client/releases
.. _System Requirements: https://doc.nuodb.com/nuodb/latest/deployment-models/physical-or-vmware-environments-with-nuodb-admin/system-requirements/
.. _Documentation: https://doc.nuodb.com/nuodb/latest/introduction-to-nuodb/
