====================
NuoDB Client Package
====================

.. contents::

This project bundles the latest publicly-available versions of NuoDB_
database clients into a single downloadable file.  The official versions of
the NuoDB Client Package file are available both from `GitHub Releases`_ as
well as from the `NuoDB Community Edition`_ webpage.

You can use this project to create a package containing customized sets of NuoDB
Client packages.

Requirements
------------

Each client will have different requirements.  System requirements for running
the NuoDB database can be found on the NuoDB online documentation `System Requirements`_ page.

+------------------+-----------------------------------+
|Utility           | Requirements                      |
+==================+===================================+
|nuosql            |GNU/Linux or Windows               |
+------------------+-----------------------------------+
|nuoloader         |GNU/Linux or Windows               |
+------------------+-----------------------------------+
|nuodb-migrator    |Java 8 or 11                       |
+------------------+-----------------------------------+
|nuocmd            |Python 2 with *requests* installed |
+------------------+-----------------------------------+
|nuodbmgr          |Java 8 or 11                       |
+------------------+-----------------------------------+

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
|Hibernate3        |Java 8 or 11         |
+------------------+---------------------+
|Hibernate5        |Java 8 or 11         |
+------------------+---------------------+

The use of the client drivers require a running NuoDB database.  If you don't
have NuoDB_ available yet, you can use the `NuoDB Community Edition`_.

Installation
------------

Unpack the tar file, or unzip the zip file.  No other installation is
required.

To use the drivers you may need to configure applications with the appropriate
paths.

Resources
---------

NuoDB_Documentation_

License
-------

NuoDB Client is licensed under the `BSD 3-Clause License <https://github.com/nuodb/nuodb-client/blob/master/LICENSE>`_.

.. _NuoDB: https://www.nuodb.com/
.. _GitHub Releases: https://github.com/nuodb/nuodb-client/releases
.. _NuoDB Community Edition: https://www.nuodb.com/dev-center/community-edition-download
.. _System Requirements: https://doc.nuodb.com/Latest/Content/System-Requirements.htm
.. _Documentation: https://doc.nuodb.com/Latest/Default.htm
.. _NuoDB Documenation: https://doc.nuodb.com/Latest/Default.htm
