.. _installation:

Installation/Updates
####################



.. _installation-pip:

Using PIP
*********

Installation using PIP
======================

.. code-block:: bash

   pip3 install pyVHDLModel


Updating using PIP
==================

.. code-block:: bash

   pip3 install -U pyVHDLModel



.. _installation-setup:

Using setup.py
**************

.. todo::

   Describe setup procedure using ``setup.py``



.. _dependency:

Dependencies
************

.. _dependency-package:

pyVHDLModel Package
===================

+----------------------------------------------------+-------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+
| **Package**                                        | **Version** | **License**                                                        | **Dependencies**                                                                                                              |
+====================================================+=============+====================================================================+===============================================================================================================================+
| `pydecor <https://github.com/mplanchard/pydecor>`_ | ≥2.0.1      | `MIT <https://github.com/mplanchard/pydecor/blob/master/LICENSE>`_ | * `dill <https://github.com/uqfoundation/dill>`_ (`BSD 3-clause <https://github.com/uqfoundation/dill/blob/master/LICENSE>`_) |
|                                                    |             |                                                                    | * `six <https://github.com/benjaminp/six>`_ (`MIT <https://github.com/benjaminp/six/blob/master/LICENSE>`_)                   |
+----------------------------------------------------+-------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+


.. _dependency-testing:

Unit Testing / Coverage
=======================

Additional Python packages needed for testing and code coverage collection.
These packages are only needed for developers or on a CI server, thus
sub-dependencies are not evaluated further.

+----------------------------------------------------------+-------------+---------------------------------------------------------------------------------------+----------------------+
| **Package**                                              | **Version** | **License**                                                                           | **Dependencies**     |
+==========================================================+=============+=======================================================================================+======================+
| `pytest <https://github.com/pytest-dev/pytest>`_         | ≥6.2.1      | `MIT <https://github.com/pytest-dev/pytest/blob/master/LICENSE>`_                     | *Not yet evaluated.* |
+----------------------------------------------------------+-------------+---------------------------------------------------------------------------------------+----------------------+
| `pytest-cov <https://github.com/pytest-dev/pytest-cov>`_ | ≥2.10.1     | `MIT <https://github.com/pytest-dev/pytest-cov/blob/master/LICENSE>`_                 | *Not yet evaluated.* |
+----------------------------------------------------------+-------------+---------------------------------------------------------------------------------------+----------------------+
| `Coverage <https://github.com/nedbat/coveragepy>`_       | ≥5.3        | `Apache License, 2.0 <https://github.com/nedbat/coveragepy/blob/master/LICENSE.txt>`_ | *Not yet evaluated.* |
+----------------------------------------------------------+-------------+---------------------------------------------------------------------------------------+----------------------+


.. _dependency-documentation:

Sphinx Documentation
====================

Additional Python packages needed for documentation generation. These packages
are only needed for developers or on a CI server, thus sub-dependencies are not
evaluated further.

* Sphinx
* sphinx-rtd-theme
* sphinx.ext.coverage
* autoapi
* sphinx_fontawesome
* sphinx_autodoc_typehints
* btd.sphinx.graphviz
* btd.sphinx.inheritance_diagram
* Pygments
