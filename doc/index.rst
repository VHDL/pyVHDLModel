.. include:: shields.inc

.. image:: _static/logo.svg
   :height: 90 px
   :align: center
   :target: https://GitHub.com/vhdl/pyVHDLModel

.. raw:: html

    <br>

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:pyVHDLModel-github| |SHIELD:svg:pyVHDLModel-src-license| |SHIELD:svg:pyVHDLModel-ghp-doc| |SHIELD:svg:pyVHDLModel-doc-license| |SHIELD:svg:pyVHDLModel-gitter|
   |  |SHIELD:svg:pyVHDLModel-pypi-tag| |SHIELD:svg:pyVHDLModel-pypi-status| |SHIELD:svg:pyVHDLModel-pypi-python|
   |  |SHIELD:svg:pyVHDLModel-gha-test| |SHIELD:svg:pyVHDLModel-lib-status| |SHIELD:svg:pyVHDLModel-codacy-quality| |SHIELD:svg:pyVHDLModel-codacy-coverage| |SHIELD:svg:pyVHDLModel-codecov-coverage|

.. Disabled shields: |SHIELD:svg:pyVHDLModel-lib-dep| |SHIELD:svg:pyVHDLModel-lib-rank|

.. only:: latex

   |SHIELD:png:pyVHDLModel-github| |SHIELD:png:pyVHDLModel-src-license| |SHIELD:png:pyVHDLModel-ghp-doc| |SHIELD:png:pyVHDLModel-doc-license| |SHIELD:svg:pyVHDLModel-gitter|
   |SHIELD:png:pyVHDLModel-pypi-tag| |SHIELD:png:pyVHDLModel-pypi-status| |SHIELD:png:pyVHDLModel-pypi-python|
   |SHIELD:png:pyVHDLModel-gha-test| |SHIELD:png:pyVHDLModel-lib-status| |SHIELD:png:pyVHDLModel-codacy-quality| |SHIELD:png:pyVHDLModel-codacy-coverage| |SHIELD:png:pyVHDLModel-codecov-coverage|

.. Disabled shields: |SHIELD:png:pyVHDLModel-lib-dep| |SHIELD:png:pyVHDLModel-lib-rank|

The pyVHDLModel Documentation
#############################

An abstract VHDL language model.


.. _goals:

Main Goals
**********

This package provides a unified abstract language model for VHDL. Projects reading
from source files can derive own classes and implement additional logic to create
a concrete language model for their tools.

Projects consuming pre-processed VHDL data (parsed, analyzed or elaborated) can
build higher level features and services on such a model, while supporting multiple
frontends.


.. _usecase:

Use Cases
*********

* High-level API for `GHDL's <https://GitHub.com/ghdl/ghdl>`__ `libghdl` offered via `pyGHDL <https://ghdl.github.io/ghdl/using/pyGHDL/index.html>`__.
* Code Document-Object-Model (Code-DOM) in `pyVHDLParser <https://GitHub.com/Paebbels/pyVHDLParser>`__.


.. _news:

News
****

.. only:: html

   Jan. 2023 - Dependency, Hierarchy, Compile Order Analysis
   =========================================================

.. only:: latex

   .. rubric:: Dependency, Hierarchy, Compile Order Analysis

* Enhanced analysis of cross references.
* Enhanced dependency graphs:

  * Hierarchy graph and toplevel detection
  * Compile order computation

* Transformation from single module to >15 modules.
* Improved code coverage and test cases.

.. only:: html

   Dec. 2022 - Added Documentation Property
   ========================================

.. only:: latex

   .. rubric:: Added Documentation Property

* `GHDL's <https://GitHub.com/ghdl/ghdl>`__ is now able to collect and associate (documentation) comments to language
  constructs. This enhancement adds a ``Documentation`` property to many classes similar to a *doc-string* in Python.
* New -style of symbols merging a ``Name`` and a ``Symbol`` class.
* Finding relations between packages and its bodies, entities and its architectures.
* References to libraries, packages and contexts.
* Dependency graph for packages, contexts, and entities.

  * Package graph.
  * Hierarchy graph.
  * Compile order.


.. only:: html

   Jul. 2021 - First adoption and enhancements
   ===========================================

.. only:: latex

   .. rubric:: First adoption and enhancements

* `GHDL's <https://GitHub.com/ghdl/ghdl>`__ is the first big adopter with `pyGHDL.dom <https://ghdl.github.io/ghdl/pyGHDL/pyGHDL.dom.html>`__
  to generate a network of instantiated classes derived from ``pyVHDLModel``. |br|
  It uses `pyGHDL <https://ghdl.github.io/ghdl/using/pyGHDL/index.html>`__ as a backend (GHDL build as shared object and
  loaded into CPython via C-binding API (``ctypes``).


.. only:: html

   Jun. 2021 - Model and documentation enhancements
   ================================================

.. only:: latex

   .. rubric:: Model and documentation enhancements

* Made generic, port, and parameter items a subclass of the matching object classes.
* Added missing object representations for language features.

  * Finalized literals, expressions and types.
  * Added properties to empty placeholder classes.

* Corrected class hierarchy according to LRM.
* Enhanced class documentation and cross references.
* New documentation chapter for literals and expressions.
* Added inheritance diagrams as overviews to documentation sections.
* Added condensed code snippets outlining the main interface of a model's object.
* New Single-File GitHub Action workflow (pipeline) including tests, documentation, packaging and publishing.
* Added Dependabot configuration file.
* Removed 2 dependencies to patched Sphinx extensions (now fixed in Sphinx).
* ...

.. only:: html

   Jan. 2021 - Documentation enhancements
   ======================================

.. only:: latex

   .. rubric:: Documentation enhancements

* Enhanced class documentation.
* Changed test runner to ``pytest``.
* Dependency check and license clearance. |br|
  See :ref:`dependency` for details.


.. only:: html

   Dec. 2020 - Split from pyVHDLParser
   ===================================

.. only:: latex

   .. rubric:: Split from pyVHDLParser

* `pyVHDLModel` was split from `pyVHDLParser <https://GitHub.com/Paebbels/pyVHDLParser>`__ (v0.6.0) as an independent Python package.


.. _contributors:

Contributors
************

* `Patrick Lehmann <https://GitHub.com/Paebbels>`__ (Maintainer)
* `Unai Martinez-Corral <https://GitHub.com/umarcor/>`__
* `and more... <https://GitHub.com/VHDL/pyVHDLModel/graphs/contributors>`__


License
*******

.. only:: html

   This Python package (source code) is licensed under `Apache License 2.0 <Code-License.html>`__. |br|
   The accompanying documentation is licensed under `Creative Commons - Attribution 4.0 (CC-BY 4.0) <Doc-License.html>`__.

.. only:: latex

   This Python package (source code) is licensed under **Apache License 2.0**. |br|
   The accompanying documentation is licensed under **Creative Commons - Attribution 4.0 (CC-BY 4.0)**.

------------------------------------

.. |docdate| date:: %d.%b %Y - %H:%M

.. only:: html

   This document was generated on |docdate|.


.. toctree::
   :hidden:

   Used as a layer of EDA² ➚ <https://edaa-org.github.io/>


.. toctree::
   :caption: Introduction
   :hidden:

   GettingStarted
   Installation
   Dependency


.. raw:: latex

   \part{Main Documentation}

.. toctree::
   :caption: Main Documentation
   :hidden:

   LanguageModel/index
   Analyze/index
   DataStructure/index


.. raw:: latex

   \part{References and Reports}

.. toctree::
   :caption: References and Reports
   :hidden:

   pyVHDLModel/pyVHDLModel
   Unittest Report ➚ <unittests/index>
   Coverage Report ➚ <coverage/index>
   Static Type Check Report ➚ <typing/index>


.. raw:: latex

   \part{Appendix}

.. toctree::
   :caption: Appendix
   :hidden:

   ChangeLog/index
   License
   Doc-License
   Glossary
   genindex
   Python Module Index <modindex>
