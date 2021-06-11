.. _vhdlmodel-desuni:

Design Units
############

A VHDL design (see :ref:`vhdlmodel-design`) is assembled from *design units*. VHDL distinguishes
between *primary* and *secondary* design units.

.. rubric:: Table of Content

* :ref:`vhdlmodel-primary`

  * :ref:`vhdlmodel-context`
  * :ref:`vhdlmodel-configuration`
  * :ref:`vhdlmodel-entity`
  * :ref:`vhdlmodel-package`

* :ref:`vhdlmodel-secondary`

  * :ref:`vhdlmodel-architeture`
  * :ref:`vhdlmodel-packagebody`


.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.VHDLModel.Architecture pyVHDLModel.VHDLModel.Context pyVHDLModel.VHDLModel.Configuration pyVHDLModel.VHDLModel.Entity pyVHDLModel.VHDLModel.Package pyVHDLModel.VHDLModel.PackageBody
   :parts: 1

.. _vhdlmodel-primary:

Primary Units
=============

.. _vhdlmodel-context:

Context
-------

.. todo::

   Write documentation.



.. _vhdlmodel-configuration:

Configuration
-------------

.. todo::

   Write documentation.



.. _vhdlmodel-entity:

Entity
------

An ``Entity`` represents a VHDL entity declaration. Libraries and package
references declared ahead an entity are consumed by that entity and made
available as lists. An entities also provides lists of generic and port items.
The list of declared items (e.g. objects) also contains defined items (e.g.
types). An entity's list of statements is called body items.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Entity`:

.. code-block:: Python

   @export
   class Entity(PrimaryUnit, DesignUnitWithContext):
     # inherited from ModelEntity
     @property
     def Parent(self) -> 'ModelEntity':

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from DesignUnitWithContext
     @property
     def LibraryReferences(self) -> List[LibraryReference]:

     @property
     def PackageReferences(self) -> List[PackageReference]:

     @property
     def ContextReferences(self) -> List[ContextReference]:

     # from Entity
     def __init__(self, name: str):

     @property
     def GenericItems(self) -> List[GenericInterfaceItem]:

     @property
     def PortItems(self) -> List[PortInterfaceItem]:

     @property
     def DeclaredItems(self) -> List:

     @property
     def BodyItems(self) -> List['ConcurrentStatement']:



.. _vhdlmodel-package:

Package
-------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Package`:

.. code-block:: Python

   @export
   class Package(PrimaryUnit, DesignUnitWithContext):
     # inherited from ModelEntity
     @property
     def Parent(self) -> 'ModelEntity':

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from DesignUnitWithContext
     @property
     def LibraryReferences(self) -> List[LibraryReference]:

     @property
     def PackageReferences(self) -> List[PackageReference]:

     @property
     def ContextReferences(self) -> List[ContextReference]:

     # from Package
     def __init__(self, name: str):

     @property
     def GenericItems(self) -> List[GenericInterfaceItem]:

     @property
     def DeclaredItems(self) -> List:



.. _vhdlmodel-secondary:

Secondary Units
===============

.. _vhdlmodel-architeture:

Architeture
-----------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Architecture`:

.. code-block:: Python

   @export
   class Architecture(SecondaryUnit, DesignUnitWithContext):
     # inherited from ModelEntity
     @property
     def Parent(self) -> 'ModelEntity':

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from DesignUnitWithContext
     @property
     def LibraryReferences(self) -> List[LibraryReference]:

     @property
     def PackageReferences(self) -> List[PackageReference]:

     @property
     def ContextReferences(self) -> List[ContextReference]:

     # from Architecture
     def __init__(self, name: str):

     @property
     def Entity(self) -> Entity:

     @property
     def DeclaredItems(self) -> List:

     @property
     def BodyItems(self) -> List['ConcurrentStatement']:



.. _vhdlmodel-packagebody:

Package Body
------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.PackageBody`:

.. code-block:: Python

   @export
   class PackageBody(SecondaryUnit, DesignUnitWithContext):
     # inherited from ModelEntity
     @property
     def Parent(self) -> 'ModelEntity':

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from DesignUnitWithContext
     @property
     def LibraryReferences(self) -> List[LibraryReference]:

     @property
     def PackageReferences(self) -> List[PackageReference]:

     @property
     def ContextReferences(self) -> List[ContextReference]:

     # from Package Body
     def __init__(self, name: str):

     @property
     def Package(self) -> Package:

     @property
     def DeclaredItems(self) -> List:
