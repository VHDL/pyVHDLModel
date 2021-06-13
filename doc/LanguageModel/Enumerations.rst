.. _vhdlmodel-enum:

Enumerations
############

The language model contains some enumerations to express a *kind* of a models
entity. These are not enumerated types defined by VHDL itself, like `boolean`.

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
In addition to the modes defined by VHDL (`In`, `Out`, `InOut`, `Buffer` and `Linkage`), `Default`
is a placeholder for omitted modes. The mode is then determined from the context.

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

In addition to the 4 object classes defined by VHDL (`Constant`, `Variable`,
`Signal` and `File`), `Default` is used when no object class is defined. In
such a case, the object class is determined from the context.

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
