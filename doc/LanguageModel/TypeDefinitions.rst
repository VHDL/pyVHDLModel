.. _vhdlmodel-types:

Type Declarations
#################

VHDL has types (also called a base type) and subtypes. The following shows VHDL's type hierarchy:

.. rubric:: Type Hierarchy

* Types

  * :ref:`vhdlmodel-scalartypes`

    * :ref:`vhdlmodel-enumeratedtypes`
    * :ref:`vhdlmodel-integertypes`
    * :ref:`vhdlmodel-realtypes`
    * :ref:`vhdlmodel-physicaltypes`

  * :ref:`vhdlmodel-compositetypes`

    * :ref:`vhdlmodel-arraytypes`
    * :ref:`vhdlmodel-recordtypes`

  * :ref:`vhdlmodel-protectedtypes`
  * :ref:`vhdlmodel-accesstypes`
  * :ref:`vhdlmodel-filetypes`

* Subtype

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.VHDLModel.EnumeratedType pyVHDLModel.VHDLModel.IntegerType pyVHDLModel.VHDLModel.RealType pyVHDLModel.VHDLModel.PhysicalType pyVHDLModel.VHDLModel.ArrayType pyVHDLModel.VHDLModel.RecordType pyVHDLModel.VHDLModel.ProtectedType pyVHDLModel.VHDLModel.AccessType pyVHDLModel.VHDLModel.FileType
   :parts: 1


.. _vhdlmodel-scalartypes:

Scalar Types
============

.. _vhdlmodel-enumeratedtypes:

Enumeration
-----------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.EnumeratedType`:

.. code-block:: Python

   @export
   class EnumeratedType(ScalarType, DiscreteType):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # from EnumeratedType
     @property
     def Elements(self) -> List[str]:



.. _vhdlmodel-integertypes:

Integer
-------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.IntegerType`:

.. code-block:: Python

   @export
   class IntegerType(RangedScalarType, NumericType, DiscreteType):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from RangedScalarType
     @property
     def LeftBound(self) -> 'BaseExpression':

     @property
     def RightBound(self) -> 'BaseExpression':



.. _vhdlmodel-realtypes:

Real
----

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.RealType`:

.. code-block:: Python

   @export
   class RealType(RangedScalarType, NumericType):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from RangedScalarType
     @property
     def LeftBound(self) -> 'BaseExpression':

     @property
     def RightBound(self) -> 'BaseExpression':



.. _vhdlmodel-physicaltypes:

Physical
--------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.PhysicalType`:

.. code-block:: Python

   @export
   class PhysicalType(RangedScalarType, NumericType):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from RangedScalarType
     @property
     def LeftBound(self) -> 'BaseExpression':

     @property
     def RightBound(self) -> 'BaseExpression':

     # from PhysicalType
     @property
     def PrimaryUnit(self) -> str:

     @property
     def SecondaryUnits(self) -> List[Tuple[int, str]]:



.. _vhdlmodel-compositetypes:

Composite Types
===============

.. _vhdlmodel-arraytypes:

Array
-----

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.ArrayType`:

.. code-block:: Python

   @export
   class ArrayType(CompositeType):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # from ArrayType
     @property
     def Dimensions(self) -> List[Range]:

     @property
     def ElementType(self) -> SubType:



.. _vhdlmodel-recordtypes:

Record
------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.RecordType`:

.. code-block:: Python

   @export
   class RecordType(CompositeType):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # from RecordType
     @property
     def Members(self) -> List[RecordTypeElement]:


.. _vhdlmodel-protectedtypes:

Protected
=========

.. todo::

   Write documentation.

.. _vhdlmodel-accesstypes:

Access
======

.. todo::

   Write documentation.

.. _vhdlmodel-filetypes:

File
====

.. todo::

   Write documentation.
