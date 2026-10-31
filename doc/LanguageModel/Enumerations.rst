.. _vhdlmodel-enum:

Enumerations
############

The language model contains some enumerations to express a *kind* of a models
entity. These are not enumerated types defined by VHDL itself, like ``boolean``.

.. contents:: Table of Content
   :local:


.. _vhdlmodel-direction:

Direction
*********

Ranges and slices have an ascending (``To``) or descending (``DownTo``) direction.

**Condensed definition of class** :class:`~pyVHDLModel.Base.Direction`:

.. condensed-class:: pyVHDLModel.Base.Direction


.. _vhdlmodel-mode:

Mode
****

A *mode* describes the direction of data exchange e.g. for entity ports or subprogram parameters.
In addition to the modes defined by VHDL (``In``, ``Out``, ``InOut``, ``Buffer`` and ``Linkage``), ``Default``
is a placeholder for omitted modes. The mode is then determined from the context.

**Condensed definition of class** :class:`~pyVHDLModel.Base.Mode`:

.. condensed-class:: pyVHDLModel.Base.Mode


.. _vhdlmodel-objclass:

Object Class
************

In addition to the 4 object classes defined by VHDL (`Constant`, `Variable`,
`Signal` and `File`), `Default` is used when no object class is defined. In
such a case, the object class is determined from the context.

**Condensed definition of class** :class:`~pyVHDLModel.ObjectClass`:

.. condensed-class:: pyVHDLModel.ObjectClass
