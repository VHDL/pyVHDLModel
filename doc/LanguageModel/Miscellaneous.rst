.. _vhdlmodel-misc:

Concepts not defined by VHDL
############################

Some features required for a holistic language model are not defined in the VHDL
:term:`LRM` (IEEE Std. 1076). Other features made explicitly implementation
specific to the implementer.

.. rubric:: Table of Content

* :ref:`vhdlmodel-design`
* :ref:`vhdlmodel-library`
* :ref:`vhdlmodel-document`


.. _vhdlmodel-design:

Design
======

The root element in the language model is a design mode out of multiple
sourcecode files (documents). Sourcecode files are compiled into libraries. Thus
a design has the two child nodes: ``Libraries`` and ``Documents``. Each is a
:class:`list`.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Design`:

.. code-block:: Python

   @export
   class Design(ModelEntity):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # from Design
     @property
     def Libraries(self) -> List[Library]:

     @property
     def Documents(self) -> List[Document]:



.. _vhdlmodel-library:

Library
=======

A library contains multiple *design units*. Each design unit listed in a library
is a *primary* design unit like: ``configuration``, ``entity``, ``package`` or
``context``.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Library`:

.. code-block:: Python

   @export
   class Library(ModelEntity):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # from Library
     @property
     def Contexts(self) -> List[Context]:

     @property
     def Configurations(self) -> List[Configuration]:

     @property
     def Entities(self) -> List[Entity]:

     @property
     def Packages(self) -> List[Package]:



.. _vhdlmodel-document:

Document
========

A source file (document) contains multiple *design units*. Each design unit
listed in a sourcecode file is a *primary* or *secondary* design unit like:
``configuration``, ``entity``, ``architecture``, ``package``, ``package body``
or ``context``.

Design unit may be preceded by a context made of ``library``, ``use`` and
``context`` statements. These statements are not directly visible in the
``Document`` object, because design unit contexts are consumed by the design
units. See the ``Libraries`` and ``Uses`` fields of each design unit to
investigate the consumed contexts.

**Condensed definition of class** :class:`~pyVHDLModel.VHDLModel.Document`:

.. code-block:: Python

   @export
   class Document(ModelEntity):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # from Document
     @property
     def Path(self) -> Path:

     @property
     def Contexts(self) -> List[Context]:

     @property
     def Configurations(self) -> List[Configuration]:

     @property
     def Entities(self) -> List[Entity]:

     @property
     def Architectures(self) -> List[Architecture]:

     @property
     def Packages(self) -> List[Package]:

     @property
     def PackageBodies(self) -> List[PackageBody]:
