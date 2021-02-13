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

An ``Entity`` represents a VHDL entity declaration. It has a list of generic and
port items. It can contain a list of declared and body items.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Entity`:

.. code-block:: Python

   @export
   class Entity(PrimaryUnit):
     _libraryReferences: List[LibraryReference]
     _packageReferences: List[PackageReference]
     _genericItems:      List[GenericInterfaceItem]
     _portItems:         List[PortInterfaceItem]
     _declaredItems:     List   # FIXME: define liste element type e.g. via Union
     _bodyItems:         List['ConcurrentStatement']

     def __init__(self, name: str):

     @property
     def LibraryReferences(self) -> List[LibraryReference]:

     @property
     def PackageReferences(self) -> List[PackageReference]:

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
   class Package(PrimaryUnit):
     _libraryReferences: List[Library]
     _packageReferences: List[PackageReference]
     _genericItems:      List[GenericInterfaceItem]
     _declaredItems:     List

     def __init__(self, name: str):

     @property
     def LibraryReferences(self) -> List[Library]:

     @property
     def PackageReferences(self) -> List[PackageReference]:

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
   class Architecture(SecondaryUnit):
     _entity:            Entity
     _libraryReferences: List[Library]
     _packageReferences: List[PackageReference]
     _declaredItems:     List   # FIXME: define liste element type e.g. via Union
     _bodyItems:         List['ConcurrentStatement']

     def __init__(self, name: str):

     @property
     def Entity(self) -> Entity:

     @property
     def LibraryReferences(self) -> List[Library]:

     @property
     def PackageReferences(self) -> List[PackageReference]:

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
   class PackageBody(SecondaryUnit):
     _package:           Package
     _libraryReferences: List[Library]
     _packageReferences: List[PackageReference]
     _declaredItems:     List

     def __init__(self, name: str):

     @property
     def Package(self) -> Package:

     @property
     def LibraryReferences(self) -> List[Library]:

     @property
     def PackageReferences(self) -> List[PackageReference]:

     @property
     def DeclaredItems(self) -> List:
