.. _vhdlmodel-enum:

Enumerations
############

The language model contains some enumerations to express a *kind* of a models entity.

.. rubric:: Table of Content

* :ref:`vhdlmodel-direction`
* :ref:`vhdlmodel-mode`
* :ref:`vhdlmodel-objclass`



.. _vhdlmodel-direction:

Direction
=========

Ranges and slices have an ascending (`to`) or descending (`downto`) direction.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Direction`:

.. code-block:: Python

   @export
   class Direction(Enum):
     To =      0
     DownTo =  1



.. _vhdlmodel-mode:

Mode
====

A *mode* describes the direction of data exchange e.g. for entity ports or subprogram parameters.

VHDL supports:

* `in`
* `out`
* `inout`
* `buffer`
* `linkage`

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Mode`:

.. code-block:: Python

   @export
   class Mode(Enum):
     Default = 0
     In =      1
     Out =     2
     InOut =   3
     Buffer =  4
     Linkage = 5



.. _vhdlmodel-objclass:

Object Class
============

VHDL has 4 object classes.

These are

* `Constant`
* `Variable`
* `Signal`
* `File`

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Class`:

.. code-block:: Python

   @export
   class Class(Enum):
     Default =    0
     Constant =   1
     Variable =   2
     Signal =     3
     File =       4
     Type =       5
     Subprogram = 6
