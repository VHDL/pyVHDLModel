.. include:: shields.inc

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:pyVHDLModel-github| |SHIELD:svg:pyVHDLModel-src-license| |SHIELD:svg:pyVHDLModel-tag| |SHIELD:svg:pyVHDLModel-release| |SHIELD:svg:pyVHDLModel-date| |SHIELD:svg:pyVHDLModel-lib-dep|
   |  |SHIELD:svg:pyVHDLModel-gha-test| |SHIELD:svg:pyVHDLModel-codacy-quality| |SHIELD:svg:pyVHDLModel-codacy-coverage| |SHIELD:svg:pyVHDLModel-codecov-coverage| |SHIELD:svg:pyVHDLModel-lib-rank|
   |  |SHIELD:svg:pyVHDLModel-gha-release| |SHIELD:svg:pyVHDLModel-pypi-tag| |SHIELD:svg:pyVHDLModel-pypi-status| |SHIELD:svg:pyVHDLModel-pypi-python| |SHIELD:svg:pyVHDLModel-lib-status| |SHIELD:svg:pyVHDLModel-req-status|
   |  |SHIELD:svg:pyVHDLModel-gha-doc| |SHIELD:svg:pyVHDLModel-doc-license| |SHIELD:svg:pyVHDLModel-ghp-doc|

.. only:: latex

   |SHIELD:png:pyVHDLModel-github| |SHIELD:png:pyVHDLModel-src-license| |SHIELD:png:pyVHDLModel-tag| |SHIELD:png:pyVHDLModel-release| |SHIELD:png:pyVHDLModel-date| |SHIELD:png:pyVHDLModel-lib-dep|
   |SHIELD:png:pyVHDLModel-gha-test| |SHIELD:png:pyVHDLModel-codacy-quality| |SHIELD:png:pyVHDLModel-codacy-coverage| |SHIELD:png:pyVHDLModel-codecov-coverage| |SHIELD:png:pyVHDLModel-lib-rank|
   |SHIELD:png:pyVHDLModel-gha-release| |SHIELD:png:pyVHDLModel-pypi-tag| |SHIELD:png:pyVHDLModel-pypi-status| |SHIELD:png:pyVHDLModel-pypi-python| |SHIELD:png:pyVHDLModel-lib-status| |SHIELD:png:pyVHDLModel-req-status|
   |SHIELD:png:pyVHDLModel-gha-doc| |SHIELD:png:pyVHDLModel-doc-license| |SHIELD:png:pyVHDLModel-ghp-doc|

--------------------------------------------------------------------------------

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

* High-level API for `GHDL's <https://github.com/ghdl/ghdl>`__ `libghdl` offered via `pyGHDL <https://ghdl.github.io/ghdl/using/pyGHDL/index.html>`__.
* Code Document-Object-Model (Code-DOM) in `pyVHDLParser <https://github.com/Paebbels/pyVHDLParser>`__.



.. _news:

News
****

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

* `pyVHDLModel` was split from `pyVHDLParser <https://github.com/Paebbels/pyVHDLParser>`__ (v0.6.0) as an independent Python package.



.. _contributors:

Contributors
************

* `Patrick Lehmann <https://github.com/Paebbels>`__ (Maintainer)
* `Unai Martinez-Corral <https://github.com/umarcor/>`__
* `and more... <https://github.com/VHDL/pyVHDLModel/graphs/contributors>`__


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
   :caption: Introduction
   :hidden:

   Installation
   Dependency


.. raw:: latex

   \part{Main Documentation}

.. toctree::
   :caption: Main Documentation
   :hidden:

   LanguageModel/index


.. raw:: latex

   \part{References}

.. toctree::
   :caption: References
   :hidden:

   pyVHDLModel/index


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

.. #
   py-modindex
