.. _DEP:

Dependency
##########

.. _DEP/package:

pyVHDLModel Package (Mandatory)
*******************************

.. rubric:: Manually Installing Package Requirements

Use the :file:`requirements.txt` file to install all dependencies via ``pip3`` or install the package directly from
PyPI (see :ref:`INSTALL`).

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r requirements.txt

.. rubric:: Dependency List

.. dependency-table:: package
   :caption: Mandatory dependencies of the pyVHDLModel package.


.. _DEP/testing:

Unit Testing / Coverage / Type Checking (Optional)
**************************************************

Additional Python packages needed for testing, code coverage collection and static type checking. These packages are
only needed for developers or on a CI server.

.. rubric:: Manually Installing Test Requirements

Use the :file:`tests/requirements.txt` file to install all dependencies via ``pip3``. The file will recursively install
the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r tests/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r tests\requirements.txt

.. rubric:: Dependency List

.. dependency-table:: testing
   :caption: Dependencies for unit testing, code coverage and static type checking.


.. _DEP/documentation:

Sphinx Documentation (Optional)
*******************************

Additional Python packages needed for documentation generation. These packages are only needed for developers or on a
CI server.

.. rubric:: Manually Installing Documentation Requirements

Use the :file:`doc/requirements.txt` file to install all dependencies via ``pip3``. The file will recursively install
the mandatory dependencies too.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r doc/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r doc\requirements.txt

.. rubric:: Dependency List

.. dependency-table:: documentation
   :caption: Dependencies for building the documentation.


.. _DEP/packaging:

Packaging (Optional)
********************

The build requirements - ``setuptools`` and ``pyTooling``, whose :mod:`pyTooling.Packaging` describes the package in
:file:`setup.py` - are declared in :file:`pyproject.toml` (``[build-system]``). ``pip`` and ``python -m build``
install them into an isolated build environment.


.. _DEP/publishing:

Publishing (CI-Server only)
***************************

Additional Python packages needed for publishing the generated installation package to PyPI or an equivalent service.
These packages are only needed for maintainers or on a CI server.

.. rubric:: Manually Installing Publishing Requirements

Use the :file:`dist/requirements.txt` file to install all dependencies via ``pip3``.

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: Linux

      .. code-block:: bash

         pip3 install -U -r dist/requirements.txt

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip install -U -r dist\requirements.txt

.. rubric:: Dependency List

.. dependency-table:: publishing
   :caption: Dependencies for publishing the package.
