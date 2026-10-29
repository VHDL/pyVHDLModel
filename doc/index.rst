.. include:: shields.inc

.. image:: _static/logo.svg
   :height: 90 px
   :align: center
   :target: https://GitHub.com/VHDL/pyVHDLModel

.. raw:: html

    <br>

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:pyVHDLModel-github| |SHIELD:svg:pyVHDLModel-src-license| |SHIELD:svg:pyVHDLModel-ghp-doc| |SHIELD:svg:pyVHDLModel-doc-license|
   |  |SHIELD:svg:pyVHDLModel-pypi-tag| |SHIELD:svg:pyVHDLModel-pypi-status| |SHIELD:svg:pyVHDLModel-pypi-python|
   |  |SHIELD:svg:pyVHDLModel-gha-test| |SHIELD:svg:pyVHDLModel-lib-status| |SHIELD:svg:pyVHDLModel-codacy-quality| |SHIELD:svg:pyVHDLModel-codacy-coverage| |SHIELD:svg:pyVHDLModel-codecov-coverage|

.. Disabled shields: |SHIELD:svg:pyVHDLModel-lib-dep| |SHIELD:svg:pyVHDLModel-lib-rank|

.. only:: latex

   |SHIELD:png:pyVHDLModel-github| |SHIELD:png:pyVHDLModel-src-license| |SHIELD:png:pyVHDLModel-ghp-doc| |SHIELD:png:pyVHDLModel-doc-license|
   |SHIELD:png:pyVHDLModel-pypi-tag| |SHIELD:png:pyVHDLModel-pypi-status| |SHIELD:png:pyVHDLModel-pypi-python|
   |SHIELD:png:pyVHDLModel-gha-test| |SHIELD:png:pyVHDLModel-lib-status| |SHIELD:png:pyVHDLModel-codacy-quality| |SHIELD:png:pyVHDLModel-codacy-coverage| |SHIELD:png:pyVHDLModel-codecov-coverage|

.. Disabled shields: |SHIELD:png:pyVHDLModel-lib-dep| |SHIELD:png:pyVHDLModel-lib-rank|

The pyVHDLModel Documentation
#############################

An abstract VHDL language model.


.. _GOALS:

Main Goals
**********

This package provides a unified abstract language model for VHDL. Projects reading
from source files can derive own classes and implement additional logic to create
a concrete language model for their tools.

Projects consuming pre-processed VHDL data (parsed, analyzed or elaborated) can
build higher level features and services on such a model, while supporting multiple
frontends.


.. _USECASES:

Use Cases
*********

* High-level API for `GHDL's <https://GitHub.com/ghdl/ghdl>`__ `libghdl` offered via `pyGHDL <https://ghdl.github.io/ghdl/pyGHDL/pyGHDL.html>`__.
* Code Document-Object-Model (Code-DOM) in `pyVHDLParser <https://paebbels.github.io/pyVHDLParser/>`__.
* `PyHDLio <https://github.com/amb5l/PyHDLio>`__ based on an ANTLR4 grammar.
* `pyVHDLModelTreesitter <https://gitlab.com/dawalters/pyVHDLModelTreesitter>`__ based on `tree-sitter-vhdl <https://github.com/jpt13653903/tree-sitter-vhdl>`__.


.. _CONTRIBUTORS:

Contributors
************

* :gh:`Patrick Lehmann <Paebbels>` (Maintainer)
* :gh:`Unai Martinez-Corral <umarcor>`
* `and more... <https://GitHub.com/VHDL/pyVHDLModel/graphs/contributors>`__


.. _LICENSE:

License
*******

This Python package (source code) is licensed under :ref:`Apache License 2.0 <CODELICENSE>`. |br|
The accompanying documentation is licensed under :ref:`Creative Commons - Attribution 4.0 (CC-BY 4.0) <DOCLICENSE>`.



.. toctree::
   :hidden:

   Used as a layer of EDA² ➚ <https://edaa-org.github.io/>


.. toctree::
   :caption: Introduction
   :hidden:

   News
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
   Writer/index

.. raw:: latex

   \part{References and Reports}

.. toctree::
   :caption: References and Reports
   :hidden:

   Python Class Reference <pyVHDLModel/pyVHDLModel>
   unittests/index
   coverage/index
   Doc. Coverage Report <doccoverage/index>
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
   TODO
