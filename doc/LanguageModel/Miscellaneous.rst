.. _vhdlmodel-misc:

Concepts not defined by VHDL
############################

Some features required for a holistic language model are not defined in the VHDL
:term:`LRM` (IEEE Std. 1076). Other features are made explicitly implementation
specific to the implementer. This chapter will cover these parts.

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.Design
                         pyVHDLModel.Library
                         pyVHDLModel.Document
   :parts: 1


.. _vhdlmodel-design:

Design
======

The root element in the language model is a design made out of multiple
sourcecode files (documents). Sourcecode files are compiled into libraries. Thus
a design has the two child nodes: :attr:`~pyVHDLModel.Design.Libraries`
and :attr:`~pyVHDLModel.Design.Documents`. Libraries are a :class:`dict` indexed by library name,
documents are a :class:`list`.

A primary design unit is looked up by name with :meth:`~pyVHDLModel.Design.GetEntity`,
:meth:`~pyVHDLModel.Design.GetPackage`, :meth:`~pyVHDLModel.Design.GetConfiguration` or
:meth:`~pyVHDLModel.Design.GetContext`. The lookup is case-insensitive and searches one named library or all
libraries. Unlike :meth:`~pyVHDLModel.Design.GetLibrary`, these methods create nothing: a missing library raises
:exc:`~pyVHDLModel.Exception.LibraryNotFoundError`, a missing design unit raises a kind-specific error derived from
:exc:`~pyVHDLModel.Exception.DesignUnitNotFoundError` (e.g. :exc:`~pyVHDLModel.Exception.EntityNotFoundError`), and a
design unit found in several libraries raises a kind-specific error derived from
:exc:`~pyVHDLModel.Exception.AmbiguousDesignUnitError` (e.g. :exc:`~pyVHDLModel.Exception.AmbiguousEntityError`).

**Condensed definition of class** :class:`~pyVHDLModel.Design`:

.. condensed-class:: pyVHDLModel.Design


.. _vhdlmodel-library:

Library
=======

A library contains multiple *design units*. Each design unit listed in a library
is a *primary* design unit like: :class:`~pyVHDLModel.DesignUnit.Configuration`,
:class:`~pyVHDLModel.DesignUnit.Entity`, :class:`~pyVHDLModel.DesignUnit.Package` or
:class:`~pyVHDLModel.DesignUnit.Context`.

**Condensed definition of class** :class:`~pyVHDLModel.Library`:

.. condensed-class:: pyVHDLModel.Library


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

**Condensed definition of class** :class:`~pyVHDLModel.Document`:

.. condensed-class:: pyVHDLModel.Document
