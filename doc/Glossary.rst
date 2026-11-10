.. _GLOSSARY:

Glossary
########

.. glossary::

   Declarative Part
     The list of declarations of a VHDL construct, e.g. ``architecture_declarative_part`` before the ``begin`` of an
     architecture, or ``package_declarative_part`` of a package. Its declarations belong to the construct's
     :term:`declarative region`.

     In pyVHDLModel, a declarative part is the list of declared items of a model entity, e.g.
     :attr:`~pyVHDLModel.Regions.ConcurrentDeclarationRegionMixin.DeclaredItems`. Its mutators are provided by
     :class:`~pyVHDLModel.Regions.DeclarativePartMixin`.

     See :term:`LRM` (IEEE Std 1076-2008), clause 3 (design entities), 4 (subprograms and packages) and 11 (concurrent
     statements) for the declarative parts of each construct.

   Declarative Region
     A portion of the VHDL text, in which declarations are visible and identifiers are unique. Declarative regions are
     formed by e.g. an entity declaration together with its architecture bodies, a package declaration together with
     its package body, a component declaration, a subprogram, a block, a process or a loop statement. Regions nest; a
     declaration hides a homograph of an enclosing region.

     In pyVHDLModel, a declarative region (:class:`~pyVHDLModel.Regions.DeclarativeRegionMixin`) has a namespace
     (:class:`~pyVHDLModel.Namespace.Namespace`); entity and architecture, as well as package and package body, share
     one region.

     See :term:`LRM` (IEEE Std 1076-2008), clause 12.1.

   Design Unit
     A :term:`primary unit` or :term:`secondary unit` together with its context clause (library clauses, use clauses
     and context references). It is the smallest part of a VHDL description, which can be analyzed on its own, and it
     is stored in a design library.

     In pyVHDLModel, all design units derive from :class:`~pyVHDLModel.DesignUnit.DesignUnit`.

     See :term:`LRM` (IEEE Std 1076-2008), clause 13.1.

   LRM
     IEEE Standard for VHDL Language Reference Manual

     * `1076-2019 <https://ieeexplore.ieee.org/document/8938196>`__.
     * `1076-2008 <https://ieeexplore.ieee.org/document/4772740>`__ aka IEC 61691-1-1:2011.
     * `1076-2002 <https://ieeexplore.ieee.org/document/1003477>`__ aka IEC 61691-1-1 Ed.1 (2004-10).
     * `1076-2000 <https://ieeexplore.ieee.org/document/893288>`__.
     * `1076-1993 <https://ieeexplore.ieee.org/document/392561>`__.
     * `1076-1987 <https://ieeexplore.ieee.org/document/26487>`__.

     See :ref:`VASG:About:Standards` for further details.

   Normalized
     The lower-case form of an identifier, label or designator. VHDL basic identifiers are case insensitive, so
     ``Counter``, ``COUNTER`` and ``counter`` name the same entity.

     pyVHDLModel uses the normalized form as key in its lookup dictionaries and namespaces, and to resolve names. The
     identifier as written is kept for messages and for writing VHDL.

     See :term:`LRM` (IEEE Std 1076-2008), clause 15.4.2.

   Primary Unit
     A :term:`design unit`, which can be analyzed without another design unit of the same name: an entity declaration,
     a package declaration, a package instantiation, a configuration declaration or a context declaration (and a PSL
     verification unit).

     In pyVHDLModel, primary units derive from :class:`~pyVHDLModel.DesignUnit.PrimaryUnit`.

     See :term:`LRM` (IEEE Std 1076-2008), clause 13.1.

   Secondary Unit
     A :term:`design unit`, which belongs to a :term:`primary unit` analyzed before: an architecture body belongs to an
     entity declaration, a package body to a package declaration.

     In pyVHDLModel, secondary units derive from :class:`~pyVHDLModel.DesignUnit.SecondaryUnit`.

     See :term:`LRM` (IEEE Std 1076-2008), clause 13.1.
