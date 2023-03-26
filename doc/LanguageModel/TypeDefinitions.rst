.. _vhdlmodel-types:

Type Declarations
#################

VHDL has types (also called a base type) and subtypes. The following shows VHDL's type hierarchy:

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.EnumeratedType pyVHDLModel.SyntaxModel.IntegerType pyVHDLModel.SyntaxModel.RealType pyVHDLModel.SyntaxModel.PhysicalType pyVHDLModel.SyntaxModel.ArrayType pyVHDLModel.SyntaxModel.RecordType pyVHDLModel.SyntaxModel.ProtectedType pyVHDLModel.SyntaxModel.AccessType pyVHDLModel.SyntaxModel.FileType
   :parts: 1


.. _vhdlmodel-scalartypes:

Scalar Types
============

.. _vhdlmodel-enumeratedtypes:

Enumeration
-----------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.EnumeratedType`:

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

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.IntegerType`:

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

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.RealType`:

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

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.PhysicalType`:

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

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ArrayType`:

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
     def ElementType(self) -> Subtype:



.. _vhdlmodel-recordtypes:

Record
------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.RecordType`:

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
