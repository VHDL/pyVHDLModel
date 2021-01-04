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
     _libraries:  List['Library']  #: List of all libraries defined for a design
     _documents:  List['Document'] #: List of all documents loaded for a design

     def __init__(self):

     @property
     def Libraries(self) -> List['Library']:

     @property
     def Documents(self) -> List['Document']:



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
     _contexts:       List['Context']        #: List of all contexts defined in a library.
     _configurations: List['Configuration']  #: List of all configurations defined in a library.
     _entities:       List['Entity']         #: List of all entities defined in a library.
     _packages:       List['Package']        #: List of all packages defined in a library.

     def __init__(self):

     @property
     def Contexts(self) -> List['Context']:

     @property
     def Configurations(self) -> List['Configuration']:

     @property
     def Entities(self) -> List['Entity']:

     @property
     def Packages(self) -> List['Package']:



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
     _path:           Path                   #: path to the document. ``None`` if virtual document.
     _contexts:       List['Context']        #: List of all contexts defined in a document.
     _configurations: List['Configuration']  #: List of all configurations defined in a document.
     _entities:       List['Entity']         #: List of all entities defined in a document.
     _architectures:  List['Architecture']   #: List of all architectures defined in a document.
     _packages:       List['Package']        #: List of all packages defined in a document.
     _packageBodies:  List['PackageBody']    #: List of all package bodies defined in a document.

     def __init__(self, path: Path):

     @property
     def Path(self) -> Path:

     @property
     def Contexts(self) -> List['Context']:

     @property
     def Configurations(self) -> List['Configuration']:

     @property
     def Entities(self) -> List['Entity']:

     @property
     def Architectures(self) -> List['Architecture']:

     @property
     def Packages(self) -> List['Package']:

     @property
     def PackageBodies(self) -> List['PackageBody']:
