.. include:: shields.inc

.. raw:: latex

   \part{Introduction}

.. only:: html

   |SHIELD:svg:pyVHDLModel-github| |SHIELD:svg:pyVHDLModel-tag| |SHIELD:svg:pyVHDLModel-release| |SHIELD:svg:pyVHDLModel-date| |br|
   |SHIELD:svg:pyVHDLModel-lib-status| |SHIELD:svg:pyVHDLModel-req-status| |SHIELD:svg:pyVHDLModel-lib-dep| |br|
   |SHIELD:svg:pyVHDLModel-travis| |SHIELD:svg:pyVHDLModel-pypi-tag| |SHIELD:svg:pyVHDLModel-pypi-status| |SHIELD:svg:pyVHDLModel-pypi-python| |br|
   |SHIELD:svg:pyVHDLModel-codacy-quality| |SHIELD:svg:pyVHDLModel-codacy-coverage| |SHIELD:svg:pyVHDLModel-codecov-coverage| |SHIELD:svg:pyVHDLModel-lib-rank| |br|
   |SHIELD:svg:pyVHDLModel-rtd| |SHIELD:svg:pyVHDLModel-license|

.. only:: latex

   |SHIELD:png:pyVHDLModel-github| |SHIELD:png:pyVHDLModel-tag| |SHIELD:png:pyVHDLModel-release| |SHIELD:png:pyVHDLModel-date| |br|
   |SHIELD:png:pyVHDLModel-lib-status| |SHIELD:png:pyVHDLModel-req-status| |SHIELD:png:pyVHDLModel-lib-dep| |br|
   |SHIELD:png:pyVHDLModel-travis| |SHIELD:png:pyVHDLModel-pypi-tag| |SHIELD:png:pyVHDLModel-pypi-status| |SHIELD:png:pyVHDLModel-pypi-python| |br|
   |SHIELD:png:pyVHDLModel-codacy-quality| |SHIELD:png:pyVHDLModel-codacy-coverage| |SHIELD:png:pyVHDLModel-codecov-coverage| |SHIELD:png:pyVHDLModel-lib-rank| |br|
   |SHIELD:png:pyVHDLModel-rtd| |SHIELD:png:pyVHDLModel-license|

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

* High-level API for GHDL's `libghdl` offered via `pyghdl`.
* Code Document-Object-Model (Code-DOM) in `pyVHDLParser`.



.. _news:

News
****

.. only:: html

   Dez. 2020 - Split from pyVHDLParser
   ===================================

.. only:: latex

   .. rubric:: Split from pyVHDLParser

`pyVHDLModel` was split from `pyVHDLParser` (v0.6.0) as an independent Python package.



.. _contributors:

Contributors
************

* `Patrick Lehmann <https://github.com/Paebbels>`_ (Maintainer)


License
*******

This library is licensed under **Apache License 2.0**.

------------------------------------

.. |docdate| date:: %b %d, %Y - %H:%M

.. only:: html

   This document was generated on |docdate|.


.. toctree::
   :caption: Introduction
   :hidden:

   Installation


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
   Glossary
   genindex
   py-modindex
