.. _lngmod-desuni:

Design Units
############

* Primary Units

  * Context
  * Configuration
  * Entity
  * Package

* Secondary Units

  * Architeture
  * Package Body

Primary Units
=============

Context
-------

.. todo::

   Write documentation.

Configuration
-------------

.. todo::

   Write documentation.

Entity
------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Entity`:

.. code-block:: Python

   @export
   class Entity(PrimaryUnit):
     _libraryReferences: List[LibraryReference]
     _uses:              List[Use]
     _genericItems:      List[GenericInterfaceItem]
     _portItems:         List[PortInterfaceItem]
     _declaredItems:     List   # FIXME: define liste element type e.g. via Union
     _bodyItems:         List['ConcurrentStatement']

     def __init__(self, name: str):

     @property
     def LibraryReferences(self) -> List[LibraryReference]:

     @property
     def Uses(self) -> List[Use]:

     @property
     def GenericItems(self) -> List[GenericInterfaceItem]:

     @property
     def PortItems(self) -> List[PortInterfaceItem]:

     @property
     def DeclaredItems(self) -> List:

     @property
     def BodyItems(self) -> List['ConcurrentStatement']:



Package
-------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Package`:

.. code-block:: Python

   @export
   class Package(PrimaryUnit):
     _libraryReferences: List[Library]
     _uses:              List[Use]
     _genericItems:      List[GenericInterfaceItem]
     _declaredItems:     List

     def __init__(self, name: str):

     @property
     def LibraryReferences(self) -> List[Library]:

     @property
     def Uses(self) -> List[Use]:

     @property
     def GenericItems(self) -> List[GenericInterfaceItem]:

     @property
     def DeclaredItems(self) -> List:



Secondary Units
===============

Architeture
-----------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Architecture`:

.. code-block:: Python

   @export
   class Architecture(SecondaryUnit):
     _entity:            Entity
     _libraryReferences: List[Library]
     _uses:              List[Use]
     _declaredItems:     List   # FIXME: define liste element type e.g. via Union
     _bodyItems:         List['ConcurrentStatement']

     def __init__(self, name: str):

     @property
     def Entity(self) -> Entity:

     @property
     def LibraryReferences(self) -> List[Library]:

     @property
     def Uses(self) -> List[Use]:

     @property
     def DeclaredItems(self) -> List:

     @property
     def BodyItems(self) -> List['ConcurrentStatement']:



Package Body
------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.PackageBody`:

.. code-block:: Python

   @export
   class PackageBody(SecondaryUnit):
     _package:           Package
     _libraryReferences: List[Library]
     _uses:              List[Use]
     _declaredItems:     List

     def __init__(self, name: str):

     @property
     def Package(self) -> Package:

     @property
     def LibraryReferences(self) -> List[Library]:

     @property
     def Uses(self) -> List[Use]:

     @property
     def DeclaredItems(self) -> List:
