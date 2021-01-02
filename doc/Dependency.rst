.. _dependency:

Dependency
##########

.. _dependency-package:

pyVHDLModel Package
*******************

+----------------------------------------------------+-------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+
| **Package**                                        | **Version** | **License**                                                        | **Dependencies**                                                                                                              |
+====================================================+=============+====================================================================+===============================================================================================================================+
| `pydecor <https://github.com/mplanchard/pydecor>`_ | ≥2.0.1      | `MIT <https://github.com/mplanchard/pydecor/blob/master/LICENSE>`_ | * `dill <https://github.com/uqfoundation/dill>`_ (`BSD 3-clause <https://github.com/uqfoundation/dill/blob/master/LICENSE>`_) |
|                                                    |             |                                                                    | * `six <https://github.com/benjaminp/six>`_ (`MIT <https://github.com/benjaminp/six/blob/master/LICENSE>`_)                   |
+----------------------------------------------------+-------------+--------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------+


.. _dependency-testing:

Unit Testing / Coverage
***********************

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
********************

Additional Python packages needed for documentation generation. These packages
are only needed for developers or on a CI server, thus sub-dependencies are not
evaluated further.

+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
| **Package**                                                                                    | **Version**  | **License**                                                                                             | **Dependencies**     |
+================================================================================================+==============+=========================================================================================================+======================+
| `Sphinx <https://github.com/sphinx-doc/sphinx>`_                                               | ≥3.4.1       | `BSD 3-Clause <https://github.com/sphinx-doc/sphinx/blob/master/LICENSE>`_                              | *Not yet evaluated.* |
+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
| ?? `sphinx_rtd_theme <https://github.com/readthedocs/sphinx_rtd_theme>`_                       |              | `MIT <https://github.com/readthedocs/sphinx_rtd_theme/blob/master/LICENSE>`_                            | *Not yet evaluated.* |
+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
| `autoapi <https://github.com/carlos-jenkins/autoapi>`_                                         |              | `Apache License, 2.0 <https://github.com/carlos-jenkins/autoapi/blob/master/LICENSE>`_                  | *Not yet evaluated.* |
+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
| !! `sphinx_fontawesome <https://github.com/fraoustin/sphinx_fontawesome>`_                     | ≥0.0.6       | `GPL 2.0 <https://github.com/fraoustin/sphinx_fontawesome/blob/master/LICENSE>`_                        | *Not yet evaluated.* |
+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
| `sphinx_autodoc_typehints <https://github.com/agronholm/sphinx-autodoc-typehints>`_            | ≥1.11.1      | `MIT <https://github.com/agronholm/sphinx-autodoc-typehints/blob/master/LICENSE>`_                      | *Not yet evaluated.* |
+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
| `btd.sphinx.graphviz <https://github.com/buildthedocs/sphinx.graphviz>`_                       | ≥2.3.1.post1 | `BSD 2-Clause <https://github.com/buildthedocs/sphinx.graphviz/blob/btd/master/LICENSE.md>`_            | *Not yet evaluated.* |
+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
| `btd.sphinx.inheritance_diagram <https://github.com/buildthedocs/sphinx.inheritance_diagram>`_ | ≥2.3.1.post1 | `BSD 2-Clause <https://github.com/buildthedocs/sphinx.inheritance_diagram/blob/btd/master/LICENSE.md>`_ | *Not yet evaluated.* |
+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
| `Pygments <https://github.com/pygments/pygments>`_                                             | ≥2.7.2       | `BSD 2-Clause <https://github.com/pygments/pygments/blob/master/LICENSE>`_                              | *Not yet evaluated.* |
+------------------------------------------------------------------------------------------------+--------------+---------------------------------------------------------------------------------------------------------+----------------------+
